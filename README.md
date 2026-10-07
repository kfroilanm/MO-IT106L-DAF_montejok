# MotorPH Milestone 2 

## Files I use

Place these files in one folder:

- `MotorPH_MS2_Final_Dashboard.py`
- My cleaned MotorPH Products CSV from Milestone 1
- The MotorPH Sales CSV

The script recognizes the filenames already used in my GitHub repository.

## How I run it

```bash
python MotorPH_MS2_Final_Dashboard.py
```

## Outputs created automatically

1. `MotorPH_Analytical_Dashboard.png`  
   Main dashboard containing the overview KPIs and sales/category visualizations.

2. `MotorPH_Inventory_Section.png`  
   Full inventory list containing Product ID, Product Name, Product Category, and Unit Price.

3. `MotorPH_Analytical_Dashboard.pdf`  
   Two-page submission version combining the dashboard and inventory section.

4. `MotorPH_Sales_MS2_Cleaned.csv`  
   Final sales data actually used for the dashboard calculations.

5. `MotorPH_MS2_Analysis.md`  
   First-person written explanation generated using the exact results from my data.

## Dashboard sections

### MotorPH Overview
- Total Revenue
- Total Units Sold
- Number of Products
- Number of Categories
- Listed Inventory Value
- Value of Products Acquired Before 2023

### Sales Performance
- Daily Revenue Trend
- Units Sold by Month
- Top 10 Products by Revenue

### Sales by Product Category
- Revenue by Product Category
- Product Distribution by Category
- Inventory Product Share vs Sales Unit Share

### Inventory Section
- Complete structured product list
- Product category
- Unit price

## Data cleaning included

Before I calculate the dashboard metrics, I:

- check required columns;
- standardize column names;
- handle missing Client Type and Payment Method values;
- convert dates and numeric columns;
- correct known misspelled product names;
- remove unusable records;
- remove exact duplicate rows;
- compare sales products with the cleaned Products dataset;
- replace inconsistent transaction unit prices with the official product price; and
- recalculate Revenue as `Unit Price × Quantity`.

This is important because the dashboard should be based on validated data rather than simply plotting the raw Sales file.
