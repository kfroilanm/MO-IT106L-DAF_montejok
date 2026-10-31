from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

BASE_DIR = Path(__file__).resolve().parent

PRODUCT_CANDIDATES = [
    "MotorPH_Products_Preprocessed.csv",
    "MotorPH_Products_Preprocessed - Sheet1.csv",
    "MotorPH_Products_Preprocessed  - Sheet1.csv",
    "MotorPH_Products_Preprocessed_source.csv",
]

SALES_CANDIDATES = [
    "MotorPH_Sales_MS2_Cleaned.csv",
    "MotorPH_MS2_Cleaned_Sales.csv",
    "MotorPH_Sales_Preprocessed.csv",
    "MotorPH_Sales_Preprocessed - Sheet1.csv",
]

RAW_SALES_CANDIDATES = [
    "MotorPH_Sales_Preprocessed_source.csv",
    "MotorPH_Sales Data-3rd Quarter-Year 2025.csv",
]

PRODUCT_NAME_CORRECTIONS = {
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


def find_file(candidates, label, required=True):
    for name in candidates:
        path = BASE_DIR / name
        if path.exists():
            return path
    if required:
        raise FileNotFoundError(
            f"{label} file not found. Place it in the same folder as this script."
        )
    return None


def parse_motorph_date(value):
    if pd.isna(value) or str(value).strip() == "":
        return pd.NaT
    value = str(value).strip()
    for fmt in ["%m/%d/%Y", "%m-%d-%y", "%b-%d-%Y", "%d/%m/%Y", "%Y-%m-%d"]:
        try:
            return pd.to_datetime(value, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT


def load_data():
    products_path = find_file(PRODUCT_CANDIDATES, "Products")
    sales_path = find_file(SALES_CANDIDATES, "Sales")

    products = pd.read_csv(products_path)
    sales = pd.read_csv(sales_path)

    required_product_cols = {
        "Product Name", "Product Type", "Unit Price",
        "Date of Manufacturing", "Date of Acquisition"
    }
    required_sales_cols = {
        "Date", "Client Type", "Product Name", "Product Category",
        "Unit Price", "Quantity", "Revenue", "Payment Method"
    }

    missing_products = required_product_cols.difference(products.columns)
    missing_sales = required_sales_cols.difference(sales.columns)
    if missing_products:
        raise ValueError(f"Missing Product columns: {sorted(missing_products)}")
    if missing_sales:
        raise ValueError(f"Missing Sales columns: {sorted(missing_sales)}")

    sales["Date"] = pd.to_datetime(sales["Date"], errors="coerce")
    for col in ["Quantity", "Unit Price", "Revenue"]:
        sales[col] = pd.to_numeric(sales[col], errors="coerce")

    sales = sales.dropna(
        subset=["Date", "Product Name", "Quantity", "Unit Price", "Revenue"]
    ).copy()
    sales = sales.drop_duplicates().copy()
    sales = sales[sales["Quantity"] > 0].copy()
    sales = sales[
        (sales["Date"] >= "2025-06-01") &
        (sales["Date"] <= "2025-08-31")
    ].copy()
    sales["Month"] = sales["Date"].dt.to_period("M").astype(str)

    sales["Revenue Check"] = sales["Unit Price"] * sales["Quantity"]
    mismatches = int((sales["Revenue"] != sales["Revenue Check"]).sum())
    if mismatches:
        raise ValueError(
            f"Found {mismatches} revenue mismatches. Re-run MS2 cleaning first."
        )

    return products, sales, products_path, sales_path


def descriptive_analysis(products, sales):
    product_counts = products["Product Type"].value_counts()
    monthly = sales.groupby("Month").agg(
        Units_Sold=("Quantity", "sum"),
        Revenue=("Revenue", "sum"),
        Transactions=("Revenue", "size"),
    )

    print("\n=== DESCRIPTIVE ANALYSIS ===")
    print(f"Products: {len(products):,}")
    print(f"Categories: {products['Product Type'].nunique():,}")
    print(f"Average unit price: PHP {products['Unit Price'].mean():,.2f}")
    print(f"Median unit price: PHP {products['Unit Price'].median():,.2f}")
    print(f"Minimum unit price: PHP {products['Unit Price'].min():,.2f}")
    print(f"Maximum unit price: PHP {products['Unit Price'].max():,.2f}")
    print(f"Sum of listed unit prices: PHP {products['Unit Price'].sum():,.2f}")
    print("\nMonthly sales:")
    print(monthly)
    print(f"\nTotal Q3 units sold: {sales['Quantity'].sum():,}")
    print(f"Total Q3 revenue: PHP {sales['Revenue'].sum():,.2f}")

    return product_counts, monthly


def price_mismatch_sensitivity(products):
    """
    Reconstruct the 19 original unit-price mismatches and test whether excluding
    those records would materially change the Q3 monthly revenue trend.

    Important: the finalized MS2 analysis DID NOT exclude these 19 rows.
    Their prices were corrected using the Product master and revenue was recalculated.
    This function removes them only as a robustness/sensitivity test.
    """
    raw_path = find_file(RAW_SALES_CANDIDATES, "Raw Sales", required=False)
    if raw_path is None:
        print("\nPrice-mismatch sensitivity skipped: raw Sales source not found.")
        return None

    raw = pd.read_csv(raw_path)
    rename_map = {
        "Client_Type": "Client Type",
        "Product": "Product Name",
        "Unitprice": "Original Unit Price",
        "Total": "Original Total",
        "Payment": "Payment Method",
    }
    raw = raw.rename(columns=rename_map).copy()

    raw["Product Name"] = (
        raw["Product Name"].astype("string").str.strip()
        .replace(PRODUCT_NAME_CORRECTIONS)
    )

    raw["Date"] = raw["Date"].apply(parse_motorph_date)
    raw["Original Unit Price"] = pd.to_numeric(
        raw["Original Unit Price"], errors="coerce"
    )
    raw["Quantity"] = pd.to_numeric(raw["Quantity"], errors="coerce")

    raw = raw.dropna(subset=["Date", "Product Name", "Quantity"]).copy()
    raw = raw[raw["Quantity"] > 0].copy()
    raw = raw[
        (raw["Date"] >= "2025-06-01") &
        (raw["Date"] <= "2025-08-31")
    ].drop_duplicates().copy()

    master = products[
        ["Product Name", "Product Type", "Unit Price"]
    ].rename(columns={"Unit Price": "Official Unit Price"})

    raw = raw.merge(
        master, on="Product Name", how="left", validate="many_to_one"
    )
    raw = raw.dropna(subset=["Official Unit Price"]).copy()

    raw["Price Mismatch"] = (
        raw["Original Unit Price"].notna() &
        (raw["Original Unit Price"] != raw["Official Unit Price"])
    )
    raw["Corrected Revenue"] = (
        raw["Official Unit Price"] * raw["Quantity"]
    )
    raw["Month"] = raw["Date"].dt.to_period("M").astype(str)

    all_monthly = raw.groupby("Month")["Corrected Revenue"].sum()
    excluded_monthly = (
        raw.loc[~raw["Price Mismatch"]]
        .groupby("Month")["Corrected Revenue"].sum()
    )
    mismatch_counts = raw.groupby("Month")["Price Mismatch"].sum()
    transaction_counts = raw.groupby("Month").size()

    sensitivity = pd.DataFrame({
        "Revenue_All_Corrected_Rows": all_monthly,
        "Revenue_Excluding_19_Mismatches": excluded_monthly,
        "Mismatch_Rows": mismatch_counts,
        "Transactions": transaction_counts,
    })
    sensitivity["Revenue_Difference"] = (
        sensitivity["Revenue_All_Corrected_Rows"] -
        sensitivity["Revenue_Excluding_19_Mismatches"]
    )
    sensitivity["Revenue_Difference_Pct"] = (
        sensitivity["Revenue_Difference"] /
        sensitivity["Revenue_All_Corrected_Rows"] * 100
    )
    sensitivity["Mismatch_Rate_Pct"] = (
        sensitivity["Mismatch_Rows"] /
        sensitivity["Transactions"] * 100
    )
    sensitivity["MoM_All_Corrected_Pct"] = (
        sensitivity["Revenue_All_Corrected_Rows"].pct_change() * 100
    )
    sensitivity["MoM_Excluding_Mismatches_Pct"] = (
        sensitivity["Revenue_Excluding_19_Mismatches"].pct_change() * 100
    )

    sensitivity.to_csv(
        BASE_DIR / "MotorPH_Price_Mismatch_Sensitivity.csv"
    )

    print("\n=== PRICE-MISMATCH SENSITIVITY CHECK ===")
    print(
        "The 19 rows were corrected in the final dataset, not excluded. "
        "This robustness test temporarily excludes them."
    )
    print(sensitivity.round(3))

    june_all = all_monthly.loc["2025-06"]
    august_all = all_monthly.loc["2025-08"]
    june_ex = excluded_monthly.loc["2025-06"]
    august_ex = excluded_monthly.loc["2025-08"]

    decline_all = (august_all / june_all - 1) * 100
    decline_ex = (august_ex / june_ex - 1) * 100

    print(
        f"\nJune-to-August revenue change with corrected rows: "
        f"{decline_all:.2f}%"
    )
    print(
        f"June-to-August revenue change excluding mismatch rows: "
        f"{decline_ex:.2f}%"
    )
    print(
        "Conclusion: the June > July > August decline remains in both cases, "
        "so the trend is not driven by the 19 price-mismatch rows."
    )

    return sensitivity


def inferential_analysis(products, sales):
    alpha = 0.05
    all_products = products["Product Name"].tolist()

    # Q1: July product-level unit sales normality.
    july_product_sales = (
        sales[sales["Month"] == "2025-07"]
        .groupby("Product Name")["Quantity"]
        .sum()
        .reindex(all_products, fill_value=0)
    )
    july_shapiro = stats.shapiro(july_product_sales)

    # Q2: July retail revenue > June retail revenue.
    retail = sales[
        sales["Client Type"].astype(str).str.lower() == "retail"
    ].copy()
    daily_retail = retail.groupby("Date")["Revenue"].sum()
    june_dates = pd.date_range("2025-06-01", "2025-06-30")
    july_dates = pd.date_range("2025-07-01", "2025-07-31")
    june_retail_daily = daily_retail.reindex(june_dates, fill_value=0)
    july_retail_daily = daily_retail.reindex(july_dates, fill_value=0)

    june_retail_shapiro = stats.shapiro(june_retail_daily)
    july_retail_shapiro = stats.shapiro(july_retail_daily)

    q2_one_tailed = stats.mannwhitneyu(
        july_retail_daily, june_retail_daily, alternative="greater"
    )
    q2_two_tailed = stats.mannwhitneyu(
        july_retail_daily, june_retail_daily, alternative="two-sided"
    )

    q2_n1, q2_n2 = len(july_retail_daily), len(june_retail_daily)
    q2_rank_biserial = (
        2 * q2_one_tailed.statistic / (q2_n1 * q2_n2) - 1
    )

    # Q3: August product-level unit sales normality.
    august_product_sales = (
        sales[sales["Month"] == "2025-08"]
        .groupby("Product Name")["Quantity"]
        .sum()
        .reindex(all_products, fill_value=0)
    )
    august_shapiro = stats.shapiro(august_product_sales)

    # Q4: August daily units > June+July daily units.
    daily_units = sales.groupby("Date")["Quantity"].sum()
    august_dates = pd.date_range("2025-08-01", "2025-08-31")
    previous_dates = pd.date_range("2025-06-01", "2025-07-31")
    august_daily_units = daily_units.reindex(august_dates, fill_value=0)
    previous_daily_units = daily_units.reindex(previous_dates, fill_value=0)

    august_daily_shapiro = stats.shapiro(august_daily_units)

    q4_one_tailed = stats.mannwhitneyu(
        august_daily_units, previous_daily_units, alternative="greater"
    )
    q4_two_tailed = stats.mannwhitneyu(
        august_daily_units, previous_daily_units, alternative="two-sided"
    )

    q4_n1, q4_n2 = len(august_daily_units), len(previous_daily_units)
    q4_rank_biserial = (
        2 * q4_one_tailed.statistic / (q4_n1 * q4_n2) - 1
    )

    results = pd.DataFrame([
        {
            "Question": "Q1 July product sales normality",
            "Test": "Shapiro-Wilk",
            "Statistic": july_shapiro.statistic,
            "p_value": july_shapiro.pvalue,
            "Decision": "Fail to reject H0" if july_shapiro.pvalue > alpha else "Reject H0",
        },
        {
            "Question": "Q2 July retail sales > June",
            "Test": "Mann-Whitney U (one-tailed, greater)",
            "Statistic": q2_one_tailed.statistic,
            "p_value": q2_one_tailed.pvalue,
            "Decision": "Fail to reject H0" if q2_one_tailed.pvalue > alpha else "Reject H0",
        },
        {
            "Question": "Q2 robustness: July retail differs from June",
            "Test": "Mann-Whitney U (two-tailed)",
            "Statistic": q2_two_tailed.statistic,
            "p_value": q2_two_tailed.pvalue,
            "Decision": "Fail to reject H0" if q2_two_tailed.pvalue > alpha else "Reject H0",
        },
        {
            "Question": "Q3 August product sales normality",
            "Test": "Shapiro-Wilk",
            "Statistic": august_shapiro.statistic,
            "p_value": august_shapiro.pvalue,
            "Decision": "Fail to reject H0" if august_shapiro.pvalue > alpha else "Reject H0",
        },
        {
            "Question": "Q4 August units > previous months",
            "Test": "Mann-Whitney U (one-tailed, greater)",
            "Statistic": q4_one_tailed.statistic,
            "p_value": q4_one_tailed.pvalue,
            "Decision": "Fail to reject H0" if q4_one_tailed.pvalue > alpha else "Reject H0",
        },
        {
            "Question": "Q4 robustness: August differs from previous months",
            "Test": "Mann-Whitney U (two-tailed)",
            "Statistic": q4_two_tailed.statistic,
            "p_value": q4_two_tailed.pvalue,
            "Decision": "Fail to reject H0" if q4_two_tailed.pvalue > alpha else "Reject H0",
        },
    ])

    print("\n=== INFERENTIAL ANALYSIS (alpha = 0.05) ===")
    print(
        f"Q1 July Shapiro-Wilk: W={july_shapiro.statistic:.3f}, "
        f"p={july_shapiro.pvalue:.3f}"
    )
    print(
        f"Q2 one-tailed: U={q2_one_tailed.statistic:.1f}, "
        f"p={q2_one_tailed.pvalue:.3f}"
    )
    print(
        f"Q2 two-tailed robustness: U={q2_two_tailed.statistic:.1f}, "
        f"p={q2_two_tailed.pvalue:.3f}, "
        f"rank-biserial={q2_rank_biserial:.3f}"
    )
    print(
        f"Q3 August Shapiro-Wilk: W={august_shapiro.statistic:.3f}, "
        f"p={august_shapiro.pvalue:.3f}"
    )
    print(
        f"Q4 one-tailed: U={q4_one_tailed.statistic:.1f}, "
        f"p={q4_one_tailed.pvalue:.3f}"
    )
    print(
        f"Q4 two-tailed robustness: U={q4_two_tailed.statistic:.1f}, "
        f"p={q4_two_tailed.pvalue:.3f}, "
        f"rank-biserial={q4_rank_biserial:.3f}"
    )

    results.to_csv(
        BASE_DIR / "MotorPH_Terminal_Inferential_Results_FINAL.csv",
        index=False,
    )

    return {
        "july_product_sales": july_product_sales,
        "august_product_sales": august_product_sales,
        "july_shapiro": july_shapiro,
        "q2_one_tailed": q2_one_tailed,
        "q2_two_tailed": q2_two_tailed,
        "q2_rank_biserial": q2_rank_biserial,
        "august_shapiro": august_shapiro,
        "q4_one_tailed": q4_one_tailed,
        "q4_two_tailed": q4_two_tailed,
        "q4_rank_biserial": q4_rank_biserial,
        "results_table": results,
    }


def proposed_scooter_margin_benchmarks():
    """
    Proposed operating thresholds only. The current MotorPH datasets do not
    contain unit cost/COGS, so actual gross margins cannot yet be calculated.
    """
    benchmarks = pd.DataFrame([
        {
            "Decision Zone": "Maintain",
            "Gross Margin Benchmark": "Scooter GM% at/above portfolio GM%, or no more than 2 pp below",
            "Additional Condition": "Gross profit per unit at/above portfolio median",
            "Action": "Maintain lineup; continue monitoring sell-through",
        },
        {
            "Decision Zone": "Review",
            "Gross Margin Benchmark": "Scooter GM% 3-5 pp below portfolio GM%",
            "Additional Condition": "Persists for 2 consecutive months",
            "Action": "Review pricing, promotions, product mix, and aging",
        },
        {
            "Decision Zone": "Significant change",
            "Gross Margin Benchmark": "Scooter GM% >5 pp below portfolio GM%",
            "Additional Condition": "Persists for 2 months AND sell-through <80% of portfolio median/target",
            "Action": "Consider meaningful assortment/replenishment reduction",
        },
    ])
    benchmarks.to_csv(
        BASE_DIR / "MotorPH_Scooter_Margin_Benchmarks.csv",
        index=False,
    )
    return benchmarks


def create_supporting_charts(products, sales, inferential):
    monthly_units = sales.groupby("Month")["Quantity"].sum().sort_index()
    fig, ax = plt.subplots(figsize=(8, 4.8))
    bars = ax.bar(monthly_units.index, monthly_units.values)
    ax.set_title("MotorPH Q3 2025 Units Sold by Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Units Sold")
    ax.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, monthly_units.values):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            value,
            f"{int(value):,}",
            ha="center",
            va="bottom",
        )
    fig.tight_layout()
    fig.savefig(BASE_DIR / "MotorPH_Terminal_Monthly_Units_FINAL.png", dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.hist(inferential["july_product_sales"], bins=10, edgecolor="black")
    ax.set_title("July 2025 Product-Level Unit Sales Distribution")
    ax.set_xlabel("Units Sold per Product")
    ax.set_ylabel("Number of Products")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(BASE_DIR / "MotorPH_Terminal_July_Distribution_FINAL.png", dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.hist(inferential["august_product_sales"], bins=10, edgecolor="black")
    ax.set_title("August 2025 Product-Level Unit Sales Distribution")
    ax.set_xlabel("Units Sold per Product")
    ax.set_ylabel("Number of Products")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(BASE_DIR / "MotorPH_Terminal_August_Distribution_FINAL.png", dpi=220)
    plt.close(fig)


def main():
    products, sales, products_path, sales_path = load_data()

    print(f"Products file: {products_path.name}")
    print(f"Sales file: {sales_path.name}")
    print(f"Final valid sales rows: {len(sales):,}")
    print(f"Duplicate rows: {sales.duplicated().sum():,}")

    descriptive_analysis(products, sales)
    price_mismatch_sensitivity(products)
    inferential = inferential_analysis(products, sales)

    print("\n=== PROPOSED SCOOTER MARGIN BENCHMARKS ===")
    print(
        "These are management thresholds to apply once unit cost/COGS data "
        "are available; they are not observed margins from the current dataset."
    )
    print(proposed_scooter_margin_benchmarks().to_string(index=False))

    create_supporting_charts(products, sales, inferential)

    print("\nCreated supporting files:")
    print("- MotorPH_Terminal_Inferential_Results_FINAL.csv")
    print("- MotorPH_Price_Mismatch_Sensitivity.csv")
    print("- MotorPH_Scooter_Margin_Benchmarks.csv")
    print("- MotorPH_Terminal_Monthly_Units_FINAL.png")
    print("- MotorPH_Terminal_July_Distribution_FINAL.png")
    print("- MotorPH_Terminal_August_Distribution_FINAL.png")


if __name__ == "__main__":
    main()
