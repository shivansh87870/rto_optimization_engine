-- Phase 3: Regional Carrier Risk Leaderboard Analysis

WITH regional_carrier_aggregates AS (
    SELECT 
        c.delivery_partner,
        r.region,
        COUNT(f.delivery_id) AS total_dispatches,
        SUM(CASE WHEN f.delivery_status = 'Failed' THEN 1 ELSE 0 END) AS total_failures
    FROM fact_shipments f
    JOIN dim_couriers c ON f.partner_id = c.partner_id
    JOIN dim_routes r ON f.route_id = r.route_id
    GROUP BY c.delivery_partner, r.region
),
risk_metrics AS (
    SELECT 
        delivery_partner,
        region,
        total_dispatches,
        total_failures,
        ROUND((total_failures * 100.0 / total_dispatches), 2) AS failure_percentage
    FROM regional_carrier_aggregates
)
SELECT 
    delivery_partner,
    region,
    total_dispatches,
    total_failures,
    failure_percentage,
    RANK() OVER (PARTITION BY region ORDER BY failure_percentage DESC) AS inner_region_risk_rank
FROM risk_metrics;