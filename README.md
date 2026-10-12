# MotorPH Milestone 2 - How to Run

## Required files

Place the following files in the same folder:

1. `MotorPH_MS2_Final_Dashboard_REVISED.py`
2. The cleaned MotorPH Products CSV from Milestone 1.
3. The MotorPH Sales CSV.

The script recognizes these common filenames for the Products file:
- `MotorPH_Products_Preprocessed  - Sheet1.csv`
- `MotorPH_Products_Preprocessed - Sheet1.csv`
- `MotorPH_Products_Preprocessed.csv`

The script recognizes these common filenames for the Sales file:
- `MotorPH_Sales Data-3rd Quarter-Year 2025.csv`
- `MotorPH_Sales_Preprocessed - Sheet1.csv`
- `MotorPH_Sales_Preprocessed.csv`

## Python requirements

Install:

```bash
pip install pandas matplotlib
```

## Run

Open a terminal in the project folder and run:

```bash
python MotorPH_MS2_Final_Dashboard_REVISED.py
```

## Files created

- `MotorPH_Analytical_Dashboard.png`
- `MotorPH_Inventory_Section.png`
- `MotorPH_Analytical_Dashboard.pdf`
- `MotorPH_Sales_MS2_Cleaned.csv`
- `MotorPH_MS2_Analysis.md`
- `MotorPH_MS2_README.md`

## Main analytical test

The revised dashboard compares each category's product-lineup share with its share of total units sold.

- Positive gap = overrepresented in the product lineup relative to demand.
- Negative gap = sales demand exceeds product-lineup representation.

This comparison is an assortment/inventory-risk proxy because the Products dataset does not include actual on-hand stock quantity by category.
