import pandas as pd

PRODUCTS_FILE = "MotorPH_Products_List_2025.csv"
SALES_FILE = "MotorPH_Sales Data-3rd Quarter-Year 2025.csv"

products = pd.read_csv(PRODUCTS_FILE)
sales = pd.read_csv(SALES_FILE)

print("PRODUCT LIST - ORIGINAL")
print(products.head())
products.info()
print("\nMissing values:\n", products.isnull().sum())
print("Duplicate rows:", products.duplicated().sum())

print("\nSALES DATA - ORIGINAL")
print(sales.head())
sales.info()
print("\nMissing values:\n", sales.isnull().sum())
print("Duplicate rows:", sales.duplicated().sum())

for col in ["EntrName", "EntrDetails"]:
    products[col] = products[col].astype(str).str.strip()

products = products.drop_duplicates().copy()

products["EntrNo"] = pd.to_numeric(products["EntrNo"], errors="coerce")
products["UnitPrice"] = pd.to_numeric(products["UnitPrice"], errors="coerce")
products["Manufacturing Date"] = pd.to_numeric(products["Manufacturing Date"], errors="coerce")
products["Acquisiton"] = pd.to_numeric(products["Acquisiton"], errors="coerce")

products = products.dropna(
    subset=[
        "EntrName",
        "EntrDetails",
        "UnitPrice",
        "Manufacturing Date",
        "Acquisiton",
    ]
).copy()

products["Product Type"] = (
    products["EntrDetails"]
    .str.split("/", n=1)
    .str[0]
    .str.strip()
    .str.title()
)

products_clean = products.rename(
    columns={
        "EntrName": "Product Name",
        "UnitPrice": "Unit Price",
        "Manufacturing Date": "Date of Manufacturing",
        "Acquisiton": "Date of Acquisition",
    }
).copy()

products_clean = products_clean.reset_index(drop=True)
products_clean["Product ID Number"] = range(1, len(products_clean) + 1)

for col in [
    "Product ID Number",
    "Unit Price",
    "Date of Manufacturing",
    "Date of Acquisition",
]:
    products_clean[col] = products_clean[col].astype(int)

products_clean = products_clean[
    [
        "Product ID Number",
        "Product Name",
        "Product Type",
        "Unit Price",
        "Date of Manufacturing",
        "Date of Acquisition",
    ]
]

sales = sales.rename(
    columns={
        "date": "Date",
        "client_type": "Client Type",
        "product": "Product Name",
        "unitprice": "Unit Price",
        "quantity": "Quantity",
        "total": "Total",
        "payment": "Payment Method",
    }
).copy()

for col in ["Client Type", "Product Name", "Payment Method"]:
    sales[col] = sales[col].astype("string").str.strip()

sales["Client Type"] = sales["Client Type"].fillna("Unknown").replace("", "Unknown")
sales["Payment Method"] = sales["Payment Method"].fillna("Unknown").replace("", "Unknown")

sales["Client Type"] = sales["Client Type"].str.title()
sales["Payment Method"] = sales["Payment Method"].str.title()

product_name_corrections = {
    "Yamaha Serow 25x": "Yamaha Serow 250",
    "Suzuki Raider R150 Fx": "Suzuki Raider R150 Fi",
    "Kawasaki KLX 23x": "Kawasaki KLX 230",
    "Bajaj CT12x": "Bajaj CT125",
    "KTM 790 Dukx": "KTM 790 Duke",
    "Yamaha Sniper 15x": "Yamaha Sniper 155",
    "Bristol Bobber 65x": "Bristol Bobber 650",
    "Yamaha MT-1x": "Yamaha MT-15",
    "Benelli 502x": "Benelli 502C",
    "TVS Apache RTR 200 4x": "TVS Apache RTR 200 4V",
    "Motorstar Xplorer 250x": "Motorstar Xplorer 250R",
    "CFMoto 300Sx": "CFMoto 300SR",
    "Honda ADV 16x": "Honda ADV 160",
}

sales["Product Name"] = sales["Product Name"].replace(product_name_corrections)

for col in ["Unit Price", "Quantity", "Total"]:
    sales[col] = pd.to_numeric(sales[col], errors="coerce")

def parse_motorph_date(value):
    if pd.isna(value) or str(value).strip() == "":
        return pd.NaT

    value = str(value).strip()
    formats = ["%m/%d/%Y", "%m-%d-%y", "%b-%d-%Y", "%d/%m/%Y"]

    for fmt in formats:
        try:
            return pd.to_datetime(value, format=fmt)
        except (ValueError, TypeError):
            pass

    return pd.NaT

sales["Date"] = sales["Date"].apply(parse_motorph_date)

sales = sales.dropna(subset=["Date", "Product Name", "Quantity"]).copy()
sales = sales.drop_duplicates().copy()
sales["Quantity"] = sales["Quantity"].astype(int)

price_lookup = products_clean.set_index("Product Name")["Unit Price"]
sales["Unit Price"] = sales["Product Name"].map(price_lookup)

sales = sales.dropna(subset=["Unit Price"]).copy()
sales["Unit Price"] = sales["Unit Price"].astype(int)

sales["Total"] = sales["Unit Price"] * sales["Quantity"]
sales["Date"] = sales["Date"].dt.strftime("%Y-%m-%d")

sales_clean = sales[
    [
        "Date",
        "Client Type",
        "Product Name",
        "Unit Price",
        "Quantity",
        "Total",
        "Payment Method",
    ]
].reset_index(drop=True)

print("\nPRODUCT LIST - CLEANED")
print(products_clean.head())
products_clean.info()
print("Missing values:\n", products_clean.isnull().sum())
print("Duplicate rows:", products_clean.duplicated().sum())

print("\nSALES DATA - CLEANED")
print(sales_clean.head())
sales_clean.info()
print("Missing values:\n", sales_clean.isnull().sum())
print("Duplicate rows:", sales_clean.duplicated().sum())

products_clean.to_csv("MotorPH_Products_Preprocessed.csv", index=False)
sales_clean.to_csv("MotorPH_Sales_Preprocessed.csv", index=False)

print("\nPreprocessing complete.")
print("Created: MotorPH_Products_Preprocessed.csv")
print("Created: MotorPH_Sales_Preprocessed.csv")
