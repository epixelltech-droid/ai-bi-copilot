# Data Dictionary

## Star Schema Overview

The reporting model uses `fact_sales` as the fact table and three dimensions:
- `dim_customer`
- `dim_product`
- `dim_date`

Each row in `fact_sales` represents one sales transaction.

## TABLE fact_sales

- `sale_id`: unique identifier of a sale.
- `date_id`: link to the calendar date in `dim_date`.
- `customer_id`: link to the customer in `dim_customer`.
- `product_id`: link to the product in `dim_product`.
- `quantity`: number of units sold.
- `unit_price`: selling price per unit at transaction level.
- `revenue`: total sales amount for the row.
- `cost`: total internal cost for the row.
- `margin`: profit amount for the row.

## TABLE dim_customer

- `customer_id`: unique customer identifier.
- `customer_name`: business name used in reporting.
- `country`: customer country used for geographic analysis.
- `segment`: customer segment.

### Customer Segments

- `Enterprise`: large customers with larger order volumes.
- `SMB`: small and medium-sized business customers.
- `Retail`: smaller customers or retail-style demand.

Segment is used to compare customer groups. In this demo model, the available segments are Enterprise, SMB, and Retail.

SMB means small and medium-sized business. SMB customers are usually smaller than Enterprise customers but still represent business accounts.

Retail represents smaller customers or retail-style demand. Retail analysis is useful for understanding performance among smaller customer profiles.

Enterprise represents larger customer accounts. Enterprise analysis is useful for understanding performance among larger customers.

Country always comes from `dim_customer.country`. In this model, a country analysis means the country of the customer, not the product and not the warehouse.

When a user asks for revenue, margin, ASP, or quantity by segment, the analysis should join `fact_sales` with `dim_customer`.

When a user asks for performance by country, the country is always interpreted as the customer country.

## TABLE dim_product

- `product_id`: unique product identifier.
- `product_name`: reporting name of the product.
- `category`: product family used for grouped analysis.
- `unit_cost`: internal cost per unit.

### Product Categories

- `IT`
- `Office`
- `Accessories`

Category is used to group products into business families. Category analysis is useful for comparing Revenue, Cost, Margin, Quantity, or Average Selling Price across product families.

IT contains technology-oriented products.

Office contains workplace and office supply products.

Accessories contains add-on products and smaller complementary items.

When a user asks for revenue, margin, margin %, ASP, or quantity by category, the analysis should join `fact_sales` with `dim_product`.

## TABLE dim_date

- `date_id`: date key in `YYYYMMDD` numeric format.
- `full_date`: full calendar date in ISO format.
- `year`: calendar year.
- `quarter`: calendar quarter from 1 to 4.
- `month`: calendar month number from 1 to 12.
- `month_name`: month label used in reporting.
- `day`: day of month.

## Relationships

- `fact_sales.date_id -> dim_date.date_id`
- `fact_sales.customer_id -> dim_customer.customer_id`
- `fact_sales.product_id -> dim_product.product_id`

These relationships allow BI queries such as:
- revenue by country
- margin by category
- margin % by segment
- average selling price by country
- revenue share by country
- revenue by month
- top customers
