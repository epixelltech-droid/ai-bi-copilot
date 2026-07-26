import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB = Path("data/demo.db")
DB.parent.mkdir(parents=True, exist_ok=True)

SEED = 42
random.seed(SEED)

COUNTRIES = ["France", "Maroc", "Espagne", "Allemagne", "Italie"]
SEGMENTS = ["Enterprise", "SMB", "Retail"]
PRODUCTS = [
    ("Laptop Pro 14", "IT", 720.0),
    ("Laptop Air 13", "IT", 560.0),
    ("Desktop Mini", "IT", 430.0),
    ("Monitor 24", "IT", 118.0),
    ("Monitor 27", "IT", 168.0),
    ("Dock Station", "IT", 74.0),
    ("Office Chair", "Office", 112.0),
    ("Standing Desk", "Office", 230.0),
    ("Meeting Table", "Office", 315.0),
    ("Storage Cabinet", "Office", 142.0),
    ("Desk Lamp", "Office", 24.0),
    ("Headset Pro", "Accessories", 38.0),
    ("Wireless Mouse", "Accessories", 12.0),
    ("Mechanical Keyboard", "Accessories", 46.0),
    ("Webcam HD", "Accessories", 34.0),
    ("USB-C Hub", "Accessories", 21.0),
    ("Backpack", "Accessories", 19.0),
    ("Notebook Pack", "Accessories", 4.0),
]
CUSTOMER_PREFIXES = [
    "Atlas", "Nova", "Horizon", "Delta", "Orion", "Zenith", "Pulse", "Vertex",
    "Cedar", "Summit", "Lumen", "Helios", "Opal", "Aster", "Coral", "Nimbus",
    "Aquila", "Mistral", "Argon", "Sierra", "Artemis", "Kepler", "Aurora", "Solstice",
    "Lyra", "Eclipse", "Pegasus", "Apex", "Matrix", "Fusion", "Vector", "Cobalt",
    "Jade", "Quartz", "Meridian", "Northwind", "Bluewave", "Redstone", "Grandview", "Pioneer",
    "Everest", "Silverline", "Moonlight", "Sunrise", "Bridgeway", "Lakefront", "Urbanix", "Terranova",
    "Boreal", "Ventura",
]
MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def build_customers() -> list[tuple[int, str, str, str]]:
    customers = []
    for customer_id, prefix in enumerate(CUSTOMER_PREFIXES, start=1):
        country = COUNTRIES[(customer_id - 1) % len(COUNTRIES)]
        segment = SEGMENTS[(customer_id - 1) % len(SEGMENTS)]
        customer_name = f"{prefix} {segment}"
        customers.append((customer_id, customer_name, country, segment))
    return customers


def build_products() -> list[tuple[int, str, str, float]]:
    return [
        (product_id, product_name, category, unit_cost)
        for product_id, (product_name, category, unit_cost) in enumerate(PRODUCTS, start=1)
    ]


def build_dates() -> list[tuple[int, str, int, int, int, str, int]]:
    start_date = date(2025, 1, 1)
    end_date = date(2026, 12, 31)
    total_days = (end_date - start_date).days + 1
    rows = []
    for offset in range(total_days):
        current = start_date + timedelta(days=offset)
        date_id = int(current.strftime("%Y%m%d"))
        quarter = ((current.month - 1) // 3) + 1
        rows.append((
            date_id,
            current.isoformat(),
            current.year,
            quarter,
            current.month,
            MONTH_NAMES[current.month],
            current.day,
        ))
    return rows


def build_sales(customers, products, dates) -> list[tuple[int, int, int, int, int, float, float, float, float]]:
    sales = []
    seasonality = {
        1: 0.96, 2: 0.97, 3: 1.00, 4: 1.01, 5: 1.03, 6: 1.05,
        7: 1.02, 8: 0.98, 9: 1.04, 10: 1.08, 11: 1.12, 12: 1.15,
    }
    for sale_id in range(1, 3001):
        date_id, full_date, year, quarter, month, month_name, day = random.choice(dates)
        customer_id, customer_name, country, segment = random.choice(customers)
        product_id, product_name, category, unit_cost = random.choice(products)

        base_qty = {"Enterprise": (6, 20), "SMB": (3, 12), "Retail": (1, 6)}[segment]
        quantity = random.randint(*base_qty)

        category_markup = {"IT": 1.45, "Office": 1.35, "Accessories": 1.60}[category]
        segment_markup = {"Enterprise": 0.97, "SMB": 1.03, "Retail": 1.08}[segment]
        seasonal_markup = seasonality[month]
        variation = random.uniform(0.93, 1.08)
        unit_price = round(unit_cost * category_markup * segment_markup * seasonal_markup * variation, 2)

        revenue = round(quantity * unit_price, 2)
        cost = round(quantity * unit_cost, 2)
        margin = round(revenue - cost, 2)
        sales.append((sale_id, date_id, customer_id, product_id, quantity, unit_price, revenue, cost, margin))
    return sales


conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON")

sales_object = cur.execute(
    "SELECT type FROM sqlite_master WHERE name = 'sales'"
).fetchone()
if sales_object:
    cur.execute(f"DROP {sales_object[0].upper()} sales")
for table_name in ["fact_sales", "dim_date", "dim_product", "dim_customer"]:
    cur.execute(f"DROP TABLE IF EXISTS {table_name}")

cur.execute("""
CREATE TABLE dim_customer(
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    country TEXT NOT NULL,
    segment TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE dim_product(
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_cost REAL NOT NULL
)
""")

cur.execute("""
CREATE TABLE dim_date(
    date_id INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day INTEGER NOT NULL
)
""")

cur.execute("""
CREATE TABLE fact_sales(
    sale_id INTEGER PRIMARY KEY,
    date_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    revenue REAL NOT NULL,
    cost REAL NOT NULL,
    margin REAL NOT NULL,
    FOREIGN KEY(date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY(customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY(product_id) REFERENCES dim_product(product_id)
)
""")

customers = build_customers()
products = build_products()
dates = build_dates()
sales = build_sales(customers, products, dates)

cur.executemany(
    """
    INSERT INTO dim_customer(customer_id, customer_name, country, segment)
    VALUES (?, ?, ?, ?)
    """,
    customers,
)
cur.executemany(
    """
    INSERT INTO dim_product(product_id, product_name, category, unit_cost)
    VALUES (?, ?, ?, ?)
    """,
    products,
)
cur.executemany(
    """
    INSERT INTO dim_date(date_id, full_date, year, quarter, month, month_name, day)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    dates,
)
cur.executemany(
    """
    INSERT INTO fact_sales(sale_id, date_id, customer_id, product_id, quantity, unit_price, revenue, cost, margin)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    sales,
)

conn.commit()
conn.close()

print(
    f"Created {DB} with "
    f"{len(customers)} customers, "
    f"{len(products)} products, "
    f"{len(dates)} dates, "
    f"{len(sales)} sales"
)
