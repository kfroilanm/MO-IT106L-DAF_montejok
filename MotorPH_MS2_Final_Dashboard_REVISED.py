"""
MotorPH Milestone 2 - Final Analytical Dashboard

This script:
1. Loads my cleaned Products dataset from Milestone 1.
2. Loads and checks the MotorPH Sales dataset.
3. Handles missing values, duplicate rows, date issues, inconsistent product names,
   and inconsistent unit prices.
4. Combines Products and Sales using Product Name.
5. Computes KPI metrics.
6. Creates a Matplotlib analytical dashboard.
7. Creates a complete Inventory Section.
8. Writes a short first-person analysis that I can use in my Milestone 2 report.
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


# ------------------------------------------------------------
# FILE SETTINGS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# I use the cleaned Products dataset from Milestone 1.
PRODUCT_CANDIDATES = [
    "MotorPH_Products_Preprocessed  - Sheet1.csv",
    "MotorPH_Products_Preprocessed - Sheet1.csv",
    "MotorPH_Products_Preprocessed.csv",
]

# I load the Sales dataset and clean/check it again for Milestone 2.
SALES_CANDIDATES = [
    "MotorPH_Sales Data-3rd Quarter-Year 2025.csv",
    "MotorPH_Sales_Preprocessed - Sheet1.csv",
    "MotorPH_Sales_Preprocessed.csv",
]

DASHBOARD_PNG = BASE_DIR / "MotorPH_Analytical_Dashboard.png"
INVENTORY_PNG = BASE_DIR / "MotorPH_Inventory_Section.png"
DASHBOARD_PDF = BASE_DIR / "MotorPH_Analytical_Dashboard.pdf"
ANALYSIS_FILE = BASE_DIR / "MotorPH_MS2_Analysis.md"
CLEAN_SALES_FILE = BASE_DIR / "MotorPH_Sales_MS2_Cleaned.csv"
README_FILE = BASE_DIR / "MotorPH_MS2_README.md"


def find_file(candidates, description):
    """Find the first available file from a list of possible filenames."""
    for name in candidates:
        path = BASE_DIR / name
        if path.exists():
            return path

    # Fallback: search for similar filenames.
    keyword = "Products" if description == "Products" else "Sales"
    matches = list(BASE_DIR.glob(f"*MotorPH*{keyword}*.csv"))
    if matches:
        return matches[0]

    raise FileNotFoundError(
        f"{description} dataset was not found.\n"
        f"Place the required CSV file in the same folder as this script."
    )


def standardize_column_name(column):
    """Convert column names to a simple form for easier matching."""
    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
    )


def load_products():
    """Load and validate my cleaned Milestone 1 Products dataset."""
    product_path = find_file(PRODUCT_CANDIDATES, "Products")

    try:
        products = pd.read_csv(product_path)
    except pd.errors.EmptyDataError:
        raise SystemExit("ERROR: The Products dataset is empty.")
    except pd.errors.ParserError as error:
        raise SystemExit(f"ERROR: Products CSV could not be read: {error}")

    required = {
        "Product ID Number",
        "Product Name",
        "Product Type",
        "Unit Price",
        "Date of Manufacturing",
        "Date of Acquisition",
    }

    missing = required.difference(products.columns)
    if missing:
        raise SystemExit(
            "ERROR: Missing required Products column(s): "
            + ", ".join(sorted(missing))
        )

    products = products.copy()

    # Clean text fields.
    products["Product Name"] = products["Product Name"].astype("string").str.strip()
    products["Product Type"] = products["Product Type"].astype("string").str.strip()

    # Convert numeric fields.
    for column in [
        "Product ID Number",
        "Unit Price",
        "Date of Manufacturing",
        "Date of Acquisition",
    ]:
        products[column] = pd.to_numeric(products[column], errors="coerce")

    # Remove invalid product rows.
    products = products.dropna(
        subset=["Product Name", "Product Type", "Unit Price"]
    ).copy()

    products = products.drop_duplicates(subset=["Product Name"]).copy()
    products["Unit Price"] = products["Unit Price"].astype(float)

    return products, product_path


def parse_motorph_date(value):
    """
    Parse the date formats found in the MotorPH Sales file.
    I explicitly try several formats instead of allowing a failed conversion
    to stop the whole script.
    """
    if pd.isna(value) or str(value).strip() == "":
        return pd.NaT

    value = str(value).strip()

    formats = [
        "%m/%d/%Y",
        "%m-%d-%y",
        "%b-%d-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return pd.to_datetime(value, format=fmt)
        except (ValueError, TypeError):
            continue

    return pd.NaT


def load_and_clean_sales(products):
    """Load, review, clean, and prepare the Sales dataset for analysis."""
    sales_path = find_file(SALES_CANDIDATES, "Sales")

    try:
        sales = pd.read_csv(sales_path)
    except pd.errors.EmptyDataError:
        raise SystemExit("ERROR: The Sales dataset is empty.")
    except pd.errors.ParserError as error:
        raise SystemExit(f"ERROR: Sales CSV could not be read: {error}")

    original_rows = len(sales)
    original_duplicates = int(sales.duplicated().sum())

    # --------------------------------------------------------
    # 1. STANDARDIZE COLUMN NAMES
    # --------------------------------------------------------
    normalized_lookup = {
        standardize_column_name(column): column for column in sales.columns
    }

    aliases = {
        "date": "Date",
        "clienttype": "Client Type",
        "product": "Product Name",
        "productname": "Product Name",
        "unitprice": "Original Unit Price",
        "quantity": "Quantity",
        "total": "Original Total",
        "payment": "Payment Method",
        "paymentmethod": "Payment Method",
    }

    rename_map = {}
    for normalized, original in normalized_lookup.items():
        if normalized in aliases:
            rename_map[original] = aliases[normalized]

    sales = sales.rename(columns=rename_map).copy()

    required = {"Date", "Product Name", "Quantity"}
    missing = required.difference(sales.columns)
    if missing:
        raise SystemExit(
            "ERROR: Missing required Sales column(s): "
            + ", ".join(sorted(missing))
        )

    # Add optional columns if absent.
    for column in [
        "Client Type",
        "Payment Method",
        "Original Unit Price",
        "Original Total",
    ]:
        if column not in sales.columns:
            sales[column] = pd.NA

    # Keep a copy of missing counts before cleaning for my data-quality report.
    missing_before = sales.isna().sum().to_dict()

    # --------------------------------------------------------
    # 2. CLEAN TEXT FIELDS
    # --------------------------------------------------------
    for column in ["Client Type", "Product Name", "Payment Method"]:
        sales[column] = sales[column].astype("string").str.strip()

    sales["Client Type"] = (
        sales["Client Type"]
        .fillna("Unknown")
        .replace("", "Unknown")
        .str.title()
    )

    sales["Payment Method"] = (
        sales["Payment Method"]
        .fillna("Unknown")
        .replace("", "Unknown")
        .str.title()
    )

    # These corrections are carried forward from my Milestone 1 preprocessing.
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

    # --------------------------------------------------------
    # 3. FIX DATA TYPES
    # --------------------------------------------------------
    sales["Date"] = sales["Date"].apply(parse_motorph_date)
    sales["Quantity"] = pd.to_numeric(sales["Quantity"], errors="coerce")
    sales["Original Unit Price"] = pd.to_numeric(
        sales["Original Unit Price"], errors="coerce"
    )
    sales["Original Total"] = pd.to_numeric(
        sales["Original Total"], errors="coerce"
    )

    invalid_dates = int(sales["Date"].isna().sum())

    # Remove records that cannot be used in the analysis.
    sales = sales.dropna(subset=["Date", "Product Name", "Quantity"]).copy()
    sales = sales[sales["Quantity"] > 0].copy()

    # The dataset is overwhelmingly June-August 2025.
    # I treat dates outside that reporting period as date-entry outliers.
    report_start = pd.Timestamp("2025-06-01")
    report_end = pd.Timestamp("2025-08-31")

    outside_period = int(
        ((sales["Date"] < report_start) | (sales["Date"] > report_end)).sum()
    )

    sales = sales[
        (sales["Date"] >= report_start) & (sales["Date"] <= report_end)
    ].copy()

    # Remove exact duplicate transaction rows only.
    sales = sales.drop_duplicates().copy()

    # --------------------------------------------------------
    # 4. JOIN SALES WITH THE CLEAN PRODUCT MASTER
    # --------------------------------------------------------
    product_master = products[
        ["Product Name", "Product Type", "Unit Price"]
    ].rename(columns={"Unit Price": "Official Unit Price"})

    sales = sales.merge(
        product_master,
        on="Product Name",
        how="left",
        validate="many_to_one",
    )

    unmatched_products = int(sales["Product Type"].isna().sum())

    # I do not guess the category/price of an unmatched product.
    # Instead I exclude unmatched product records from KPI calculations.
    sales = sales.dropna(
        subset=["Product Type", "Official Unit Price"]
    ).copy()

    # Count price problems before replacing them with the official product price.
    comparable_price = sales["Original Unit Price"].notna()
    price_mismatches = int(
        (
            comparable_price
            & (sales["Original Unit Price"] != sales["Official Unit Price"])
        ).sum()
    )

    # Use the cleaned Products dataset as the official price source.
    sales["Unit Price"] = sales["Official Unit Price"]
    sales["Quantity"] = sales["Quantity"].astype(int)

    # Recalculate revenue instead of trusting inconsistent Total values.
    sales["Revenue"] = sales["Unit Price"] * sales["Quantity"]

    comparable_total = sales["Original Total"].notna()
    total_mismatches = int(
        (
            comparable_total
            & (sales["Original Total"] != sales["Revenue"])
        ).sum()
    )

    sales["Month"] = sales["Date"].dt.to_period("M").astype(str)

    # Final clean dataset for reproducibility.
    sales[
        [
            "Date",
            "Client Type",
            "Product Name",
            "Product Type",
            "Unit Price",
            "Quantity",
            "Revenue",
            "Payment Method",
        ]
    ].to_csv(CLEAN_SALES_FILE, index=False)

    quality_summary = {
        "sales_file": sales_path.name,
        "original_rows": original_rows,
        "original_duplicates": original_duplicates,
        "invalid_dates": invalid_dates,
        "outside_period": outside_period,
        "unmatched_products": unmatched_products,
        "price_mismatches": price_mismatches,
        "total_mismatches": total_mismatches,
        "final_rows": len(sales),
        "missing_before": missing_before,
    }

    return sales, sales_path, quality_summary


def peso(value):
    """Format Philippine peso values for display."""
    if abs(value) >= 1_000_000:
        return f"₱{value / 1_000_000:,.2f}M"
    if abs(value) >= 1_000:
        return f"₱{value / 1_000:,.1f}K"
    return f"₱{value:,.0f}"


def calculate_metrics(products, sales):
    """Compute the main KPI figures shown in the overview."""
    total_revenue = sales["Revenue"].sum()
    total_units = int(sales["Quantity"].sum())
    number_products = int(products["Product Name"].nunique())
    number_categories = int(products["Product Type"].nunique())
    transactions = int(len(sales))
    listed_inventory_value = products["Unit Price"].sum()

    pre_2023_value = products.loc[
        products["Date of Acquisition"] < 2023, "Unit Price"
    ].sum()

    return {
        "total_revenue": total_revenue,
        "total_units": total_units,
        "number_products": number_products,
        "number_categories": number_categories,
        "transactions": transactions,
        "listed_inventory_value": listed_inventory_value,
        "pre_2023_value": pre_2023_value,
    }


def add_kpi(ax, title, value):
    """Draw one KPI card using text only."""
    ax.axis("off")
    ax.text(
        0.5,
        0.62,
        value,
        ha="center",
        va="center",
        fontsize=17,
        fontweight="bold",
    )
    ax.text(
        0.5,
        0.25,
        title,
        ha="center",
        va="center",
        fontsize=9,
    )


def create_dashboard(products, sales, metrics):
    """Create page 1: analytical dashboard with KPIs and six visualizations."""

    # Aggregations used in the charts.
    daily_revenue = sales.groupby("Date")["Revenue"].sum().sort_index()

    monthly_units = (
        sales.groupby("Month")["Quantity"]
        .sum()
        .sort_index()
    )

    product_revenue = (
        sales.groupby("Product Name")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )

    category_revenue = (
        sales.groupby("Product Type")["Revenue"]
        .sum()
        .sort_values()
    )

    category_units = sales.groupby("Product Type")["Quantity"].sum()

    # Product-lineup share is used as a proxy for inventory representation
    # because the Products dataset contains product records/models rather than
    # an explicit on-hand stock quantity.
    product_distribution = products["Product Type"].value_counts()
    inventory_share = product_distribution / product_distribution.sum() * 100
    sales_share = category_units / category_units.sum() * 100

    mix = pd.concat(
        [
            inventory_share.rename("Product Lineup Share"),
            sales_share.rename("Sales Unit Share"),
        ],
        axis=1,
    ).fillna(0)

    # Positive gap = category is more represented in the product lineup
    # than in actual unit sales.
    mix["Gap (pp)"] = (
        mix["Product Lineup Share"] - mix["Sales Unit Share"]
    )

    # Categories with the largest positive gap are the most overrepresented.
    top_overrepresented = mix.sort_values(
        "Gap (pp)", ascending=False
    ).head(3)

    # Largest negative gaps identify categories where demand share is greater
    # than the product-lineup share.
    top_underrepresented = mix.sort_values(
        "Gap (pp)", ascending=True
    ).head(3)

    fig = plt.figure(figsize=(18, 26))
    grid = fig.add_gridspec(
        nrows=5,
        ncols=6,
        height_ratios=[0.55, 1.7, 2.2, 2.5, 2.8],
        hspace=0.58,
        wspace=0.78,
    )

    fig.suptitle(
        "MotorPH Analytical Dashboard",
        fontsize=24,
        fontweight="bold",
        y=0.985,
    )
    fig.text(
        0.5,
        0.966,
        "Products and Sales Performance | June-August 2025",
        ha="center",
        fontsize=12,
    )

    # -----------------------
    # MOTORPH OVERVIEW
    # -----------------------
    fig.text(
        0.03,
        0.945,
        "MotorPH Overview",
        fontsize=15,
        fontweight="bold",
    )

    kpi_values = [
        ("Total Revenue", peso(metrics["total_revenue"])),
        ("Total Units Sold", f'{metrics["total_units"]:,}'),
        ("Products", f'{metrics["number_products"]:,}'),
        ("Categories", f'{metrics["number_categories"]:,}'),
        ("Listed Product Value", peso(metrics["listed_inventory_value"])),
        ("Pre-2023 Product Value", peso(metrics["pre_2023_value"])),
    ]

    for index, (title, value) in enumerate(kpi_values):
        ax = fig.add_subplot(grid[0, index])
        add_kpi(ax, title, value)

    # -----------------------
    # SALES PERFORMANCE
    # -----------------------
    ax1 = fig.add_subplot(grid[1, 0:3])
    ax1.plot(daily_revenue.index, daily_revenue.values, marker="o", markersize=2)
    ax1.set_title("Daily Revenue Trend")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Revenue (PHP)")
    ax1.tick_params(axis="x", rotation=35)
    ax1.grid(axis="y", alpha=0.25)

    ax2 = fig.add_subplot(grid[1, 3:6])
    ax2.bar(monthly_units.index, monthly_units.values)
    ax2.set_title("Units Sold by Month")
    ax2.set_xlabel("Month")
    ax2.set_ylabel("Units Sold")
    ax2.grid(axis="y", alpha=0.25)
    for x, value in enumerate(monthly_units.values):
        ax2.text(
            x,
            value,
            f"{int(value):,}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax3 = fig.add_subplot(grid[2, 0:3])
    ax3.barh(product_revenue.index, product_revenue.values)
    ax3.set_title("Top 10 Products by Revenue")
    ax3.set_xlabel("Revenue (PHP)")
    ax3.set_ylabel("Product")
    ax3.grid(axis="x", alpha=0.25)

    ax4 = fig.add_subplot(grid[2, 3:6])
    ax4.barh(category_revenue.index, category_revenue.values)
    ax4.set_title("Revenue by Product Category")
    ax4.set_xlabel("Revenue (PHP)")
    ax4.set_ylabel("Category")
    ax4.grid(axis="x", alpha=0.25)

    # -----------------------
    # INVENTORY VS DEMAND
    # -----------------------
    # Rebuilt category chart requested in the instructor feedback.
    mix_plot = mix.sort_values("Sales Unit Share")
    y = list(range(len(mix_plot)))
    width = 0.38

    ax5 = fig.add_subplot(grid[3, 0:3])
    ax5.barh(
        [position - width / 2 for position in y],
        mix_plot["Product Lineup Share"],
        height=width,
        label="Product lineup share",
    )
    ax5.barh(
        [position + width / 2 for position in y],
        mix_plot["Sales Unit Share"],
        height=width,
        label="Sales unit share",
    )
    ax5.set_yticks(y)
    ax5.set_yticklabels(mix_plot.index)
    ax5.set_title("Product Lineup Share vs Sales Unit Share")
    ax5.set_xlabel("Share (%)")
    ax5.set_ylabel("Product Category")
    ax5.legend(fontsize=8, loc="lower right")
    ax5.grid(axis="x", alpha=0.25)

    # Leave space to the right for the instructor-requested gap annotations.
    share_max = max(
        mix_plot["Product Lineup Share"].max(),
        mix_plot["Sales Unit Share"].max(),
    )
    ax5.set_xlim(0, share_max + 9)

    # Annotate the three categories with the largest positive gaps.
    for category, row in top_overrepresented.iterrows():
        plot_index = list(mix_plot.index).index(category)
        annotation_x = max(
            row["Product Lineup Share"],
            row["Sales Unit Share"],
        ) + 0.6
        ax5.text(
            annotation_x,
            plot_index,
            f"{category}: +{row['Gap (pp)']:.2f} pp",
            va="center",
            fontsize=8,
            fontweight="bold",
        )

    # Diverging gap chart: positive = overrepresented, negative = underrepresented.
    gap_plot = mix.sort_values("Gap (pp)")
    ax6 = fig.add_subplot(grid[3, 3:6])
    ax6.barh(gap_plot.index, gap_plot["Gap (pp)"])
    ax6.axvline(0, linewidth=1)
    ax6.set_title("Product Lineup Share Gap vs Sales Demand")
    ax6.set_xlabel(
        "Gap in percentage points "
        "(positive = overrepresented; negative = underrepresented)"
    )
    ax6.set_ylabel("Product Category")
    ax6.grid(axis="x", alpha=0.25)

    # -----------------------
    # EXPLANATIONS & INSIGHTS
    # -----------------------
    ax7 = fig.add_subplot(grid[4, :])
    ax7.axis("off")

    top_product = sales.groupby("Product Name")["Revenue"].sum().idxmax()
    top_category_revenue = (
        sales.groupby("Product Type")["Revenue"].sum().idxmax()
    )
    top_category_units = (
        sales.groupby("Product Type")["Quantity"].sum().idxmax()
    )

    chart_explanations = (
        "Chart guide\n"
        "• Daily Revenue Trend — line chart: shows how revenue changes through time.\n"
        "• Units Sold by Month — bar chart: compares monthly sales volume directly.\n"
        "• Top 10 Products by Revenue — horizontal bar chart: ranks products while keeping long names readable.\n"
        "• Revenue by Product Category — horizontal bar chart: compares category contribution to revenue.\n"
        "• Product Lineup Share vs Sales Unit Share — grouped horizontal bars: tests whether category representation matches demand.\n"
        "• Product Lineup Share Gap — diverging bars: positive values indicate overrepresentation; negative values indicate stronger demand than lineup share.\n"
    )

    over_lines = []
    for category, row in top_overrepresented.iterrows():
        over_lines.append(
            f"{category}: {row['Product Lineup Share']:.1f}% lineup vs "
            f"{row['Sales Unit Share']:.1f}% sales "
            f"(+{row['Gap (pp)']:.2f} pp)"
        )

    under_lines = []
    for category, row in top_underrepresented.iterrows():
        under_lines.append(
            f"{category}: {row['Product Lineup Share']:.1f}% lineup vs "
            f"{row['Sales Unit Share']:.1f}% sales "
            f"({row['Gap (pp)']:.2f} pp)"
        )

    insight_text = (
        chart_explanations
        + "\nKey insights\n"
        + f"• I analyzed {metrics['transactions']:,} valid sales records after data cleaning.\n"
        + f"• The dataset generated {metrics['total_units']:,} units sold and "
        + f"{peso(metrics['total_revenue'])} in calculated revenue.\n"
        + f"• The highest-revenue product is {top_product}; "
        + f"{top_category_revenue} leads category revenue, while "
        + f"{top_category_units} leads sales volume.\n"
        + "• Largest overrepresentation gaps: "
        + "; ".join(over_lines)
        + ".\n"
        + "• Largest underrepresentation gaps: "
        + "; ".join(under_lines)
        + ".\n"
        + "• Recommendation: slow replenishment or reduce assortment growth first in the most overrepresented categories, "
        + "especially Naked Bike and Underbone. Keep Scooters under observation rather than cutting aggressively because its "
        + "lineup share and sales share are already close. Reallocate purchasing attention toward categories where sales share "
        + "exceeds lineup share, such as Commuter and Adventure, while also checking margin and stock aging before changing order quantities.\n"
        + "• Limitation: product-lineup share is a proxy for inventory representation because the Products dataset does not contain "
        + "actual on-hand stock quantity by category."
    )

    ax7.text(
        0.015,
        0.98,
        insight_text,
        va="top",
        fontsize=10.5,
        linespacing=1.45,
        wrap=True,
    )

    fig.text(
        0.5,
        0.01,
        (
            "Source: MotorPH Products and Sales datasets | "
            "Analysis prepared in Python using pandas and matplotlib"
        ),
        ha="center",
        fontsize=9,
    )

    plt.savefig(DASHBOARD_PNG, dpi=250, bbox_inches="tight")
    return fig


def create_inventory_page(products):
    """Create page 2: complete structured inventory section."""
    inventory = (
        products[
            ["Product ID Number", "Product Name", "Product Type", "Unit Price"]
        ]
        .sort_values("Product ID Number")
        .copy()
    )

    inventory["Product ID Number"] = inventory["Product ID Number"].astype(int)
    inventory["Unit Price"] = inventory["Unit Price"].map(
        lambda value: f"₱{value:,.0f}"
    )

    midpoint = (len(inventory) + 1) // 2
    left = inventory.iloc[:midpoint]
    right = inventory.iloc[midpoint:]

    fig = plt.figure(figsize=(18, 16))
    grid = fig.add_gridspec(1, 2, wspace=0.08)

    fig.suptitle(
        "MotorPH Inventory Section",
        fontsize=22,
        fontweight="bold",
        y=0.97,
    )
    fig.text(
        0.5,
        0.945,
        "Structured list of products, categories, and pricing",
        ha="center",
        fontsize=11,
    )

    for position, data in enumerate([left, right]):
        ax = fig.add_subplot(grid[0, position])
        ax.axis("off")

        table = ax.table(
            cellText=data.values,
            colLabels=["ID", "Product", "Category", "Unit Price"],
            loc="center",
            cellLoc="left",
            colLoc="left",
            colWidths=[0.08, 0.43, 0.25, 0.20],
        )

        table.auto_set_font_size(False)
        table.set_fontsize(7.8)
        table.scale(1, 1.45)

    fig.text(
        0.5,
        0.02,
        f"Total products listed: {len(inventory)}",
        ha="center",
        fontsize=10,
    )

    plt.savefig(INVENTORY_PNG, dpi=250, bbox_inches="tight")
    return fig


def write_analysis(products, sales, metrics, quality):
    """Write a first-person Milestone 2 explanation using my actual calculated results."""

    category_count = (
        products["Product Type"]
        .value_counts()
        .sort_values(ascending=False)
    )

    product_revenue = (
        sales.groupby("Product Name")["Revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    category_revenue = (
        sales.groupby("Product Type")["Revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    category_units = (
        sales.groupby("Product Type")["Quantity"]
        .sum()
        .sort_values(ascending=False)
    )

    monthly_revenue = (
        sales.groupby("Month")["Revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    inventory_share = (
        category_count / category_count.sum() * 100
    )

    sales_share = (
        category_units / category_units.sum() * 100
    )

    gap_table = pd.concat(
        [
            inventory_share.rename("Product Lineup Share"),
            sales_share.rename("Sales Unit Share"),
        ],
        axis=1,
    ).fillna(0)

    gap_table["Gap (pp)"] = (
        gap_table["Product Lineup Share"]
        - gap_table["Sales Unit Share"]
    )

    top_overrepresented = gap_table.sort_values(
        "Gap (pp)", ascending=False
    ).head(3)

    top_underrepresented = gap_table.sort_values(
        "Gap (pp)", ascending=True
    ).head(3)

    top_product = product_revenue.index[0]
    top_product_revenue = product_revenue.iloc[0]
    top_revenue_category = category_revenue.index[0]
    top_revenue_category_value = category_revenue.iloc[0]
    top_units_category = category_units.index[0]
    top_units_category_value = int(category_units.iloc[0])
    best_month = monthly_revenue.index[0]
    best_month_revenue = monthly_revenue.iloc[0]

    over_lines = "\n".join(
        (
            f"- **{category}:** "
            f"{row['Product Lineup Share']:.1f}% product-lineup share vs "
            f"{row['Sales Unit Share']:.1f}% sales-unit share "
            f"= **+{row['Gap (pp)']:.2f} percentage points**"
        )
        for category, row in top_overrepresented.iterrows()
    )

    under_lines = "\n".join(
        (
            f"- **{category}:** "
            f"{row['Product Lineup Share']:.1f}% product-lineup share vs "
            f"{row['Sales Unit Share']:.1f}% sales-unit share "
            f"= **{row['Gap (pp)']:.2f} percentage points**"
        )
        for category, row in top_underrepresented.iterrows()
    )

    report = f"""# MotorPH Milestone 2 – Analytical Dashboard

## 1. Objective

For Milestone 2, I extended my initial product-category visualization into a complete analytical dashboard. I used my cleaned MotorPH Products dataset from Milestone 1 together with the MotorPH Sales dataset. My goal was to summarize MotorPH's product lineup, measure sales performance, compare product categories, and present the information in a clear visual format using Python, pandas, and matplotlib.

## 2. Data Preparation

I first reviewed the structure of both datasets before creating the visualizations. The Products dataset was used as my master reference for product names, product categories, and official unit prices.

For the Sales dataset, I checked missing values, duplicate rows, data types, dates, product names, unit prices, and totals. I standardized the column names so that the script can work with the MotorPH source files even when some headers use underscores or slightly different capitalization.

I also reused the product-name corrections from my Milestone 1 preprocessing. Instead of trusting inconsistent prices in individual sales records, I matched each sales product with the official unit price from my cleaned Products dataset and recalculated revenue as:

**Revenue = Official Unit Price × Quantity**

### Data-quality checks performed

- Original sales rows loaded: **{quality['original_rows']:,}**
- Exact duplicate rows detected before cleaning: **{quality['original_duplicates']:,}**
- Missing or unparseable dates detected: **{quality['invalid_dates']:,}**
- Date records outside the June-August 2025 reporting period: **{quality['outside_period']:,}**
- Sales records with unmatched products after name standardization: **{quality['unmatched_products']:,}**
- Sales rows with a listed unit price different from the official product price: **{quality['price_mismatches']:,}**
- Sales rows where the supplied total differed from my recalculated revenue: **{quality['total_mismatches']:,}**
- Final valid sales rows used in the dashboard: **{quality['final_rows']:,}**

Missing Client Type and Payment Method values were retained as **Unknown** instead of being removed because these fields are not necessary for calculating the sales KPIs. Records without a valid date, product name, quantity, or matching product master record were excluded from the final calculations.

## 3. MotorPH Overview

After preprocessing, my dashboard produced the following key metrics:

- **Total Revenue:** {peso(metrics['total_revenue'])}
- **Total Units Sold:** {metrics['total_units']:,}
- **Number of Products:** {metrics['number_products']:,}
- **Number of Product Categories:** {metrics['number_categories']:,}
- **Valid Sales Transactions:** {metrics['transactions']:,}
- **Listed Product Value:** {peso(metrics['listed_inventory_value'])}
- **Value of Products Acquired Before 2023:** {peso(metrics['pre_2023_value'])}

## 4. Why I Used Each Chart Type

- **Daily Revenue Trend – Line chart:** I used a line chart because the x-axis is time. It makes changes in daily revenue across the reporting period easier to see.
- **Units Sold by Month – Bar chart:** I used vertical bars because there are only three monthly totals and I wanted a direct comparison of sales volume.
- **Top 10 Products by Revenue – Horizontal bar chart:** I used horizontal bars because product names are long and the ranking is easier to read.
- **Revenue by Product Category – Horizontal bar chart:** This shows which categories contribute the most revenue and allows categories to be compared on the same scale.
- **Product Lineup Share vs Sales Unit Share – Grouped horizontal bar chart:** This directly compares category representation in the product lineup with actual demand based on unit sales.
- **Product Lineup Share Gap – Diverging horizontal bar chart:** This converts the comparison into one number. A positive gap indicates overrepresentation, while a negative gap indicates that sales demand is greater than lineup representation.

## 5. Key Sales Insights

The month with the highest revenue was **{best_month}**, with approximately **{peso(best_month_revenue)}** in revenue.

The highest-revenue product was **{top_product}**, which generated approximately **{peso(top_product_revenue)}**.

The category with the highest revenue was **{top_revenue_category}**, with approximately **{peso(top_revenue_category_value)}**. The category with the highest unit sales was **{top_units_category}**, with **{top_units_category_value:,} units sold**.

## 6. Inventory Representation vs Actual Demand

I calculated product-lineup share as the number of product records in a category divided by the total number of products. I then compared it with the category's share of total units sold.

The three most overrepresented categories are:

{over_lines}

The three categories with the strongest sales share relative to their product-lineup share are:

{under_lines}

For example, Scooters account for about **{inventory_share.get('Scooter', 0):.1f}%** of the product lineup and about **{sales_share.get('Scooter', 0):.1f}%** of units sold. The gap is only **{gap_table.loc['Scooter', 'Gap (pp)']:+.2f} percentage points**, so Scooter representation is relatively close to actual demand. This means Scooters do not show the strongest mismatch even though they are the largest category.

The larger inventory-risk signal appears in categories such as **Naked Bike** and **Underbone**, where product-lineup share is noticeably higher than sales-unit share.

## 7. Recommendation to MotorPH

Based on the gap analysis, I would recommend that MotorPH **avoid increasing assortment or replenishment too aggressively in the categories with the largest positive gaps**, particularly Naked Bike and Underbone. These categories occupy a larger share of the product lineup than their share of actual unit sales.

For Scooters, I would recommend **maintaining the category but monitoring sell-through**, because its 24% lineup share is already close to its approximately 23.1% unit-sales share. A large reduction in Scooter offerings is not supported by this dataset.

MotorPH can consider shifting some purchasing attention, display space, or future product additions toward categories where sales share is greater than product-lineup share, such as the most underrepresented categories identified above. Before changing actual order quantities, I would also review gross margin, stock aging, and true on-hand stock levels.

## 8. Limitation

The Products dataset contains product records/models and unit prices, but it does not provide actual **on-hand stock quantity by category**. Therefore, the product-lineup share used in this dashboard is a **proxy for inventory representation**, not a complete stock-on-hand measure. The gap analysis is still useful for identifying possible assortment imbalance, but final inventory purchasing decisions should also use real stock quantities and sell-through rates.

## 9. Conclusion

The revised dashboard goes beyond describing which categories are largest. It tests whether the composition of MotorPH's product lineup is aligned with customer demand. By calculating the gap between product-lineup share and sales-unit share, I can identify categories that may be overrepresented and categories where demand may justify more attention.
"""

    ANALYSIS_FILE.write_text(report, encoding="utf-8")


def write_readme():
    """Create a short reproducibility guide for another person running the project."""
    readme = """# MotorPH Milestone 2 - How to Run

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
"""
    README_FILE.write_text(readme, encoding="utf-8")


def print_quality_report(quality):
    """Show the troubleshooting results in the terminal."""
    print("\n" + "=" * 60)
    print("MOTORPH MILESTONE 2 - DATA QUALITY REPORT")
    print("=" * 60)
    print(f"Sales file used: {quality['sales_file']}")
    print(f"Rows loaded: {quality['original_rows']:,}")
    print(f"Exact duplicates detected: {quality['original_duplicates']:,}")
    print(f"Missing/unparseable dates: {quality['invalid_dates']:,}")
    print(f"Dates outside Jun-Aug 2025: {quality['outside_period']:,}")
    print(f"Unmatched products: {quality['unmatched_products']:,}")
    print(f"Unit-price mismatches: {quality['price_mismatches']:,}")
    print(f"Supplied-total mismatches: {quality['total_mismatches']:,}")
    print(f"Final rows used: {quality['final_rows']:,}")
    print("=" * 60)


def main():
    try:
        products, product_path = load_products()
        sales, sales_path, quality = load_and_clean_sales(products)
    except FileNotFoundError as error:
        raise SystemExit(f"ERROR: {error}")

    if sales.empty:
        raise SystemExit(
            "ERROR: No valid Sales records remain after cleaning."
        )

    metrics = calculate_metrics(products, sales)

    print_quality_report(quality)

    print("\nMOTORPH OVERVIEW")
    print("-" * 60)
    print(f"Products file: {product_path.name}")
    print(f"Sales file: {sales_path.name}")
    print(f"Total Revenue: {peso(metrics['total_revenue'])}")
    print(f"Total Units Sold: {metrics['total_units']:,}")
    print(f"Number of Products: {metrics['number_products']:,}")
    print(f"Number of Categories: {metrics['number_categories']:,}")
    print(f"Valid Transactions: {metrics['transactions']:,}")
    print(f"Listed Inventory Value: {peso(metrics['listed_inventory_value'])}")
    print(f"Pre-2023 Product Value: {peso(metrics['pre_2023_value'])}")

    dashboard_fig = create_dashboard(products, sales, metrics)
    inventory_fig = create_inventory_page(products)

    # Combine both dashboard sections into one PDF.
    with PdfPages(DASHBOARD_PDF) as pdf:
        pdf.savefig(dashboard_fig, bbox_inches="tight")
        pdf.savefig(inventory_fig, bbox_inches="tight")

    write_analysis(products, sales, metrics, quality)
    write_readme()

    plt.close(dashboard_fig)
    plt.close(inventory_fig)

    print("\nFILES CREATED")
    print("-" * 60)
    print(DASHBOARD_PNG.name)
    print(INVENTORY_PNG.name)
    print(DASHBOARD_PDF.name)
    print(CLEAN_SALES_FILE.name)
    print(ANALYSIS_FILE.name)
    print(README_FILE.name)
    print("\nMilestone 2 dashboard generation complete.")


if __name__ == "__main__":
    main()
