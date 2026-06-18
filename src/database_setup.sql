-- Phase 1: Database DDL Schemas

CREATE TABLE dim_couriers (
    partner_id INT AUTO_INCREMENT PRIMARY KEY,
    delivery_partner VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE dim_routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    region VARCHAR(50) NOT NULL,
    distance_km DECIMAL(6,2) NOT NULL
);

CREATE TABLE fact_shipments (
    delivery_id VARCHAR(50) PRIMARY KEY,
    partner_id INT,
    route_id INT,
    delivery_mode VARCHAR(50),
    weather_condition VARCHAR(50),
    package_weight_kg DECIMAL(5,2),
    delivery_cost DECIMAL(10,2),
    delivery_status VARCHAR(50),
    FOREIGN KEY (partner_id) REFERENCES dim_couriers(partner_id),
    FOREIGN KEY (route_id) REFERENCES dim_routes(route_id)
);