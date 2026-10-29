# Data Dictionary

## sales data
The sales dataset contains daily or periodic demand by SKU.

Typical fields:
- `date`: date of transaction
- `sku`: unique product code
- `product_name`: item name
- `category`: product family
- `units_sold`: units sold in the period
- `revenue`: commercial value generated

## supplier data
Supplier information used for lead-time modeling.

Typical fields:
- `sku`
- `supplier`
- `lead_time_days`
- `unit_cost`
- `service_level`

## derived inventory plan
After processing, this dashboard creates operational fields such as:
- `avg_daily_demand`
- `annual_demand`
- `safety_stock`
- `reorder_point`
- `eoq`
- `stockout_probability`
- `abc_class`
- `ved_class`
- `risk_score`
- `alert_level`