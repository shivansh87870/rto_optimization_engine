import os
import pandas as pd
import mysql.connector

class DataPipelineBouncer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def load_and_audit(self):
        print("\n🛡️ Ingesting and auditing raw logistics streams...")
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Missing raw file! Drop your Kaggle CSV into: {self.file_path}")
            
        self.df = pd.read_csv(self.file_path)
        print(f"📋 Total initial records ingested: {len(self.df)}")
        
        # Define strict quality guardrails (drop missing values, negative metrics)
        corrupt_mask = (
            (self.df['package_weight_kg'] <= 0) | 
            (self.df['distance_km'] <= 0) |
            (self.df['delivery_cost'] <= 0) |
            (self.df['delivery_id'].isna())
        )
        
        quarantine_df = self.df[corrupt_mask]
        clean_df = self.df[~corrupt_mask]
        
        # Log dirty telemetry records for engineering audits
        if not quarantine_df.empty:
            quarantine_df.to_csv("data/quarantined_errors.csv", index=False)
            print(f"⚠️ Security Flag: Quarantined {len(quarantine_df)} anomalous records to data/quarantined_errors.csv")
            
        print(f"🚀 Data Quality verified. {len(clean_df)} pure records passed to memory.")
        return clean_df

    def seed_dimensions_and_get_mappings(self, cursor, conn, clean_df):
        print("🗂️ Seeding dimension arrays and generating lookup caches...")
        
        # 1. Handle Courier Dimension
        unique_partners = clean_df['delivery_partner'].dropna().unique()
        for partner in unique_partners:
            cursor.execute("""
                INSERT IGNORE INTO dim_couriers (delivery_partner) 
                VALUES (%s)
            """, (str(partner),))
        conn.commit()
        
        # Fetch the auto-generated courier keys back into a quick-lookup dictionary
        cursor.execute("SELECT partner_id, delivery_partner FROM dim_couriers")
        courier_map = {partner: p_id for (p_id, partner) in cursor.fetchall()}

        # 2. Handle Route Dimension
        unique_routes = clean_df[['region', 'distance_km']].drop_duplicates()
        for _, row in unique_routes.iterrows():
            cursor.execute("""
                INSERT IGNORE INTO dim_routes (region, distance_km) 
                VALUES (%s, %s)
            """, (str(row['region']), float(row['distance_km'])))
        conn.commit()
        
        # Fetch the auto-generated route keys back into a lookup tuple-dictionary
        cursor.execute("SELECT route_id, region, distance_km FROM dim_routes")
        route_map = {(region, float(dist)): r_id for (r_id, region, dist) in cursor.fetchall()}
        
        return courier_map, route_map

    def bulk_load_fact(self, cursor, conn, clean_df, courier_map, route_map):
        print("⚡ Executing unified mapping transformations and loading fact table...")
        
        fact_payloads = []
        for _, row in clean_df.iterrows():
            # Match the raw records to our relational database IDs
            p_id = courier_map.get(row['delivery_partner'])
            
            # Simple tuple coordinate lookup for routes
            r_key = (row['region'], float(row['distance_km']))
            r_id = route_map.get(r_key)
            
            fact_payloads.append((
                str(row['delivery_id']),
                p_id,
                r_id,
                str(row['delivery_mode']),
                str(row['weather_condition']),
                float(row['package_weight_kg']),
                float(row['delivery_cost']),
                str(row['delivery_status'])
            ))
            
        # Fast bulk transactional insertion
        insert_query = """
            INSERT INTO fact_shipments (
                delivery_id, partner_id, route_id, delivery_mode, 
                weather_condition, package_weight_kg, delivery_cost, delivery_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE delivery_status=VALUES(delivery_status)
        """
        cursor.executemany(insert_query, fact_payloads)
        conn.commit()
        print(f"📊 Fact tables successfully loaded with {len(fact_payloads)} mapped transactions.")

    def run_pipeline(self):
        clean_df = self.load_and_audit()
        
        # Connect to local server
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="as123AS@" ,  # <--- Type your MySQL password here!
            database="rto_optimization"
        )
        cursor = conn.cursor()
        
        try:
            courier_map, route_map = self.seed_dimensions_and_get_mappings(cursor, conn, clean_df)
            self.bulk_load_fact(cursor, conn, clean_df, courier_map, route_map)
        finally:
            cursor.close()
            conn.close()
            print("🔒 Database connections cleanly closed. Pipeline run complete.\n")

if __name__ == "__main__":
    # Point this to where your downloaded Kaggle dataset is located
    bouncer = DataPipelineBouncer("data/raw_logistics_data.csv")
    bouncer.run_pipeline()