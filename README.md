MO-IT106L-DAF_montejok
# MotorPH Dataset Preprocessing

This repository contains my Milestone 1 dataset preprocessing activity for MotorPH.

The project uses Python and pandas to examine, clean, standardize, and prepare the MotorPH Product List and Sales datasets for analysis.

## Files Included

- `MotorPH_Dataset_Preprocessing.py` - Python script used to load, examine, clean, and export the datasets
- `MotorPH_Products_List_2025.csv` - original MotorPH product list
- `MotorPH_Sales Data-3rd Quarter-Year 2025.csv` - original MotorPH sales dataset
- `MotorPH_Products_Preprocessed.csv` - cleaned and structured product dataset
- `MotorPH_Sales_Preprocessed.csv` - cleaned sales dataset

## Preprocessing Performed

The datasets were checked and cleaned by:

- Identifying missing values
- Checking and removing duplicate records
- Correcting data types
- Cleaning and standardizing text values
- Correcting inconsistent product names
- Standardizing date formats
- Renaming columns for clarity
- Creating sequential Product ID Numbers
- Matching sales product prices with the official product list
- Recalculating sales totals
- Removing unnecessary or invalid records
- Arranging the Product List according to the required report format

## Product List Format

The cleaned product dataset contains the following fields:

1. Product ID Number
2. Product Name
3. Product Type
4. Unit Price
5. Date of Manufacturing
6. Date of Acquisition

## Tools Used

- Python
- pandas
- GitHub

## How to Run

Make sure the original CSV files and the Python file are stored in the same folder.

Run:

```bash
python MotorPH_Dataset_Preprocessing.py
