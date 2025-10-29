# Data Model: SQLite Sales Agent

## Entities

### Product
- **Purpose**: Catalog of items available for sale in the study dataset.
- **Key Fields**:
  - `product_id` (INTEGER PRIMARY KEY)
  - `name` (TEXT, unique)
  - `category` (TEXT, optional)
  - `unit_price` (REAL)
- **Notes**: Seeded with ≥5 records describing sample products.

### Seller
- **Purpose**: Represents salespeople responsible for completed transactions.
- **Key Fields**:
  - `seller_id` (INTEGER PRIMARY KEY)
  - `name` (TEXT, unique)
  - `region` (TEXT, optional)
- **Notes**: Seeded with ≥3 records.

### Sale
- **Purpose**: Line-level sales facts linking products to sellers.
- **Key Fields**:
  - `sale_id` (INTEGER PRIMARY KEY)
  - `product_id` (INTEGER, FK → Product)
  - `seller_id` (INTEGER, FK → Seller)
  - `sale_date` (TEXT ISO date)
  - `quantity` (INTEGER)
  - `unit_price` (REAL snapshot)
- **Relationships**: Many-to-one to both Product and Seller; referential integrity enforced with foreign keys.
- **Notes**: Seeded with ≥20 rows covering multiple products/sellers to enable ranking queries.

## Derived Metrics
- Top products by total quantity sold (aggregate by `product_id`, sum `quantity`).
- Top sellers by total revenue (aggregate by `seller_id`, sum `quantity * unit_price`).

## Data Integrity Rules
- Enable `PRAGMA foreign_keys = ON` before inserts to enforce relationships.
- Use `INSERT OR IGNORE` (or `ON CONFLICT DO NOTHING`) for seeding to keep reruns idempotent.
- Wrap seeding operations in a single transaction to prevent partial data writes.
