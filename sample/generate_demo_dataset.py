"""
Generates sample/supply_chain_demo.xlsx — a realistic, presentation-ready
dataset for Traqify (24 products · 10 suppliers · 130 shipments · 18 months of sales).

Run:  python3 sample/generate_demo_dataset.py
"""
import datetime as dt
import random

import numpy as np
import pandas as pd

random.seed(7)
np.random.seed(7)

OUT = "sample/supply_chain_demo.xlsx"

# ---------------------------------------------------------------- suppliers
SUPPLIERS = [
    (1, "Rheinmetall Components GmbH", "Germany", 94.2),
    (2, "Pacific Rim Electronics", "China", 88.6),
    (3, "Midwest Auto Supply", "United States", 91.4),
    (4, "Mumbai Textiles Co.", "India", 96.1),
    (5, "Saigon Precision Mfg.", "Vietnam", 82.7),
    (6, "Sao Paulo Metals Ltda.", "Brazil", 71.3),
    (7, "Dubai Trading FZE", "United Arab Emirates", 68.9),
    (8, "Monterrey Industrial", "Mexico", 85.5),
    (9, "Osaka Bearings KK", "Japan", 97.3),
    (10, "Anatolia Textiles A.S.", "Turkey", 76.8),
]

# ---------------------------------------------------------------- products
# (name, category, unit_price, supplier_id)
CATALOG = [
    ("Wireless Mouse Pro",        "Electronics",     42.50,  2),
    ("4K UltraWide Monitor",      "Electronics",    389.99,  2),
    ("USB-C Docking Hub",         "Electronics",     89.90,  9),
    ("Noise-Cancelling Headset",  "Electronics",    249.00,  2),
    ("Mechanical Keyboard K8",    "Electronics",    119.50,  9),
    ("1080p Conference Webcam",   "Electronics",     74.25,  2),
    ("Heavy-Duty Brake Pad Set",  "Automotive",     156.40,  1),
    ("Synthetic Oil Filter",      "Automotive",      18.75,  1),
    ("Iridium Spark Plug Kit",    "Automotive",      36.20,  3),
    ("LED Matrix Headlight",      "Automotive",     284.00,  1),
    ("High-Flow Air Filter",      "Automotive",      27.90,  8),
    ("Reinforced Denim Jacket",   "Apparel",         78.00, 10),
    ("Performance Running Shoe",  "Apparel",        134.99,  5),
    ("Merino Wool Sweater",       "Apparel",         92.50, 10),
    ("Premium Cotton T-Shirt",    "Apparel",         24.99,  4),
    ("Structured Baseball Cap",   "Apparel",         21.40,  4),
    ("Ergonomic Office Chair",    "Home & Furniture", 329.00, 6),
    ("Electric Standing Desk",    "Home & Furniture", 549.00, 6),
    ("Oak Bookshelf 5-Tier",      "Home & Furniture", 189.00, 6),
    ("Architect Table Lamp",      "Home & Furniture",  64.50, 8),
    ("Single-Origin Coffee 1kg",  "Groceries",       31.80,  7),
    ("Extra Virgin Olive Oil 1L", "Groceries",       15.60,  7),
    ("Aged Basmati Rice 5kg",     "Groceries",       22.40,  4),
    ("Ceremonial Green Tea Pack", "Groceries",       27.15,  9),
]

WAREHOUSES = ["WH-Berlin", "WH-Rotterdam", "WH-Mumbai", "WH-Singapore"]

products = []
for i, (name, cat, price, sid) in enumerate(CATALOG, start=1):
    reorder = round(random.uniform(45, 95), 2)
    # a handful of products deliberately sit below their reorder level
    stock = round(random.uniform(18, 42), 2) if i % 6 == 1 else round(random.uniform(120, 460), 2)
    country = next(s[2] for s in SUPPLIERS if s[0] == sid)
    products.append(
        {
            "product_id": i,
            "product_name": name,
            "category": cat,
            "stock_quantity": stock,
            "reorder_level": reorder,
            "country": country,
            "warehouse_location": random.choice(WAREHOUSES),
            "unit_price": price,
        }
    )
products_df = pd.DataFrame(products)

suppliers_df = pd.DataFrame(
    SUPPLIERS, columns=["supplier_id", "supplier_name", "country", "reliability_score"]
)

# ---------------------------------------------------------------- shipments (Jan 2025 -> Sep 2026)
shipments = []
sid_counter = 1000
start = dt.date(2025, 1, 6)
for month_offset in range(21):
    month = (start + dt.timedelta(days=30 * month_offset)).replace(day=1)
    for _ in range(random.randint(5, 8)):
        sid_counter += 1
        pid = random.randint(1, len(products_df))
        sup = random.choice(SUPPLIERS)
        ship_day = month + dt.timedelta(days=random.randint(0, 25))
        lead = random.randint(14, 38)
        expected = ship_day + dt.timedelta(days=lead)
        # suppliers with lower reliability slip more often
        slip = np.random.poisson(max(0.4, (100 - sup[3]) / 18))
        if random.random() < 0.18:
            slip = 0
        actual = expected + dt.timedelta(days=int(slip))
        shipments.append(
            {
                "shipment_id": sid_counter,
                "supplier_id": sup[0],
                "product_id": pid,
                "shipment_date": ship_day.isoformat(),
                "expected_delivery": expected.isoformat(),
                "actual_delivery": actual.isoformat(),
                "quantity": random.randint(40, 480),
                "transport_cost": round(random.uniform(240, 4200), 2),
            }
        )
shipments_df = pd.DataFrame(shipments)

# ---------------------------------------------------------------- sales (Jan 2025 -> Sep 2026)
sales = []
sale_id = 1
sale_start = dt.date(2025, 1, 1)
# month index -> seasonal multiplier (Q4 retail peak, summer lull)
season = [1.00, 0.94, 1.02, 1.05, 1.03, 0.92, 0.88, 0.95, 1.08, 1.18, 1.34, 1.22]
for m in range(21):
    cur = (sale_start + dt.timedelta(days=30 * m)).replace(day=1)
    growth = 1 + 0.022 * m
    mult = season[m % 12] * growth
    for _, prod in products_df.iterrows():
        orders = max(1, int(np.random.normal(3.2 * mult, 1.2)))
        for _ in range(orders):
            day = cur + dt.timedelta(days=random.randint(0, 27))
            if day > dt.date(2026, 9, 30):
                continue
            qty = max(1, int(np.random.normal(26 * mult, 9)))
            revenue = round(qty * float(prod["unit_price"]) * random.uniform(0.93, 1.07), 2)
            sales.append(
                {
                    "sale_id": sale_id,
                    "product_id": int(prod["product_id"]),
                    "sale_date": day.isoformat(),
                    "quantity_sold": qty,
                    "revenue": revenue,
                }
            )
            sale_id += 1
sales_df = pd.DataFrame(sales)

# ---------------------------------------------------------------- write
with pd.ExcelWriter(OUT, engine="openpyxl") as xl:
    products_df.to_excel(xl, sheet_name="products", index=False)
    suppliers_df.to_excel(xl, sheet_name="suppliers", index=False)
    shipments_df.to_excel(xl, sheet_name="shipments", index=False)
    sales_df.to_excel(xl, sheet_name="sales", index=False)

print(f"wrote {OUT}")
print(f"  products  {products_df.shape}  low-stock: {(products_df.stock_quantity < products_df.reorder_level).sum()}")
print(f"  suppliers {suppliers_df.shape}")
print(f"  shipments {shipments_df.shape}")
print(f"  sales     {sales_df.shape}  revenue: ${sales_df.revenue.sum():,.0f}")
