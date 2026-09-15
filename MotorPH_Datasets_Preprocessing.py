import pandas as pd

PRODUCTS_FILE = "/workspaces/MO-IT106L-DAF_montejok/MotorPH_Products_Preprocessed  - Sheet1.csv"
SALES_FILE = "/workspaces/MO-IT106L-DAF_montejok/MotorPH_Sales_Preprocessed - Sheet1.csv"

products = pd.read_csv(PRODUCTS_FILE)
sales = pd.read_csv(SALES_FILE)

print("PRODUCT LIST - ORIGINAL")
print(products.head())
print(products.info())

print("\nMissing values:\n",
      products.isnull().sum())
print("Duplicate rows:",
      products.duplicated().sum())
      

print("SALES DATA - ORIGINAL")
print(sales.head())
print(sales.info())
print("\nMissing values:\n",
      sales.isnull().sum())
print("Duplicate rows:",
      sales.duplicated().sum())

print("Dataset Shape:")
print(sales.shape)


print("\nColumn Names:")
print(sales.columns)

print("\nDataset Information:")
sales.info()

print("\nMissing Values:")
print(sales.isnull().sum())

print("\nMissing Value Percentage:")
print((sales.isnull().mean() * 100).round(2))

print("\nNumber of Duplicate Rows:")
print(sales.duplicated().sum())

print("\nDescriptive Statistics:")
print(sales.describe())



