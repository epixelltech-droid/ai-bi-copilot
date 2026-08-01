# Business Rules

## 1. Revenue

Revenue is calculated as:

`Revenue = Quantity x Unit Price`

## 2. Cost

Cost is calculated as:

`Cost = Quantity x Unit Cost`

## 3. Margin

Margin is calculated as:

`Margin = Revenue - Cost`

## 4. Margin %

Margin % is calculated as:

`Margin % = Margin / Revenue x 100`

When Margin % is calculated on grouped data, use aggregated values:

`Margin % = SUM(Margin) / SUM(Revenue) x 100`

## 5. Top customer

A top customer is ranked by total Revenue unless the user explicitly asks for another metric.

## 6. Top product

A top product is ranked by total Revenue unless the user explicitly asks for quantity.

If the user asks for "top product by quantity", "most sold product", or "best product in quantity", products must be ranked by total Quantity instead of Revenue.

If the user only says "top product" without a metric, use total Revenue.

## 7. Country

Country corresponds to the country of the customer, not the product.

Country analysis should join sales with the customer dimension and use `dim_customer.country`.

## 8. Dates

Monthly, quarterly, and yearly analyses must use `dim_date`.

Year filters such as 2025 or 2026 must use `dim_date.year`.

Month filters such as January 2026 must use `dim_date.month` and `dim_date.year`.

## 9. Missing data

The system must never invent a missing value or fill a metric without data support.

## 10. Causality

The system may describe a variation, a ranking, or a trend, but it must not invent a cause unless the available data demonstrates it.

## 11. Average Selling Price

Average Selling Price is calculated as:

`Average Selling Price = Revenue / Quantity`

When ASP is calculated on grouped data, use aggregated values:

`Average Selling Price = SUM(Revenue) / SUM(Quantity)`

ASP is the abbreviation of Average Selling Price.

## 12. Gross Margin

Gross Margin is calculated as:

`Gross Margin = Revenue - Cost`

In this demo model, Gross Margin and Margin refer to the same KPI.

## 13. Segment analysis

Segment analysis uses `dim_customer.segment`.

The available customer segments are Enterprise, SMB, and Retail.

## 14. Category analysis

Category analysis uses `dim_product.category`.

The available product categories are IT, Office, and Accessories.

## 15. Revenue share

Revenue share measures contribution to total revenue.

`Revenue Share % = Group Revenue / Total Revenue x 100`

Revenue share can be used by country, segment, category, product, or customer.

## 16. Evolution over time

Evolution means comparing the same KPI across dates or periods.

Yearly evolution uses `dim_date.year`.

Monthly evolution uses `dim_date.year`, `dim_date.month`, and `dim_date.month_name`.

The system can describe an increase or decrease, but it must not invent a business cause without supporting data.
