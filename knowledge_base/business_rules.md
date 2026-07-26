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

`Margin % = Margin / Revenue`

## 5. Top customer

A top customer is ranked by total Revenue unless the user explicitly asks for another metric.

## 6. Top product

A top product is ranked by total Revenue unless the user explicitly asks for quantity.

## 7. Country

Country corresponds to the country of the customer, not the product.

## 8. Dates

Monthly, quarterly, and yearly analyses must use `dim_date`.

## 9. Missing data

The system must never invent a missing value or fill a metric without data support.

## 10. Causality

The system may describe a variation, a ranking, or a trend, but it must not invent a cause unless the available data demonstrates it.
