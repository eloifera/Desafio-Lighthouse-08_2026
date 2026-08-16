-- ==============================================================================

-- Schema Relacional com Foreign Keys

-- Gerado via Python (Bibliotecas Nativas + Mapeamento de Referências)

-- ==============================================================================


-- -----------------------------------------------------------------------
-- Tabela: addresses
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS addresses (
    id                         INTEGER PRIMARY KEY,
    customer_id                INTEGER REFERENCES customers(id),
    address_type               VARCHAR(50),
    postal_code                VARCHAR(50),
    street                     VARCHAR(50),
    number                     INTEGER,
    complement                 VARCHAR(50),
    district                   VARCHAR(50),
    city                       VARCHAR(50),
    state                      VARCHAR(50),
    country                    VARCHAR(50),
    is_primary                 BOOLEAN
);

-- -----------------------------------------------------------------------
-- Tabela: attributes
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attributes (
    id                         INTEGER PRIMARY KEY,
    name                       VARCHAR(50),
    data_type                  VARCHAR(50)
);

-- -----------------------------------------------------------------------
-- Tabela: brands
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS brands (
    id                         INTEGER PRIMARY KEY,
    name                       VARCHAR(50),
    country                    VARCHAR(50),
    is_active                  BOOLEAN,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: categories
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    id                         INTEGER PRIMARY KEY,
    name                       VARCHAR(50),
    slug                       VARCHAR(50),
    parent_category_id         INTEGER REFERENCES categories(id),
    is_active                  BOOLEAN,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: customers
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    id                         INTEGER PRIMARY KEY,
    person_type                VARCHAR(50),
    legal_name                 VARCHAR(50),
    trade_name                 VARCHAR(50),
    tax_id                     VARCHAR(50),
    state_registration         VARCHAR(50),
    email                      VARCHAR(50),
    phone                      VARCHAR(50),
    is_active                  BOOLEAN,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: employees
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS employees (
    id                         INTEGER PRIMARY KEY,
    full_name                  VARCHAR(50),
    cpf                        VARCHAR(50),
    email                      VARCHAR(50),
    role                       VARCHAR(50),
    primary_location_id        INTEGER REFERENCES locations(id),
    hire_date                  DATE,
    termination_date           DATE,
    is_active                  BOOLEAN,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: fiscal_invoices
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fiscal_invoices (
    id                         INTEGER PRIMARY KEY,
    order_id                   INTEGER REFERENCES orders(id),
    nfe_number                 VARCHAR(50),
    nfe_access_key             VARCHAR(50),
    series                     INTEGER,
    issued_at                  TIMESTAMP,
    status                     VARCHAR(50),
    total_amount               NUMERIC(12, 2),
    xml_storage_uri            VARCHAR(255),
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: goods_receipt_items
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS goods_receipt_items (
    id                         INTEGER PRIMARY KEY,
    goods_receipt_id           INTEGER REFERENCES goods_receipts(id),
    purchase_order_item_id     INTEGER REFERENCES purchase_order_items(id),
    quantity_received          NUMERIC(12, 3)
);

-- -----------------------------------------------------------------------
-- Tabela: goods_receipts
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS goods_receipts (
    id                         INTEGER PRIMARY KEY,
    purchase_order_id          INTEGER REFERENCES purchase_orders(id),
    received_by_employee_id    INTEGER REFERENCES employees(id),
    received_at                TIMESTAMP,
    notes                      VARCHAR(50),
    created_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: locations
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS locations (
    id                         INTEGER PRIMARY KEY,
    name                       VARCHAR(50),
    location_type              VARCHAR(50),
    postal_code                VARCHAR(50),
    street                     VARCHAR(50),
    number                     INTEGER,
    complement                 VARCHAR(50),
    district                   VARCHAR(50),
    city                       VARCHAR(50),
    state                      VARCHAR(50),
    country                    VARCHAR(50),
    is_active                  BOOLEAN,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: order_items
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
    id                         INTEGER PRIMARY KEY,
    order_id                   INTEGER REFERENCES orders(id),
    product_variant_id         INTEGER REFERENCES product_variants(id),
    quantity                   INTEGER,
    unit_price                 NUMERIC(12, 2),
    icms_rate                  NUMERIC(12, 2),
    ipi_rate                   NUMERIC(12, 2),
    line_total                 NUMERIC(12, 2)
);

-- -----------------------------------------------------------------------
-- Tabela: orders
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id                         INTEGER PRIMARY KEY,
    order_number               VARCHAR(50),
    channel                    VARCHAR(50),
    customer_id                INTEGER REFERENCES customers(id),
    salesperson_id             INTEGER REFERENCES employees(id),
    location_id                INTEGER REFERENCES locations(id),
    status                     VARCHAR(50),
    subtotal                   NUMERIC(12, 2),
    discount_amount            NUMERIC(12, 2),
    total                      NUMERIC(12, 2),
    placed_at                  TIMESTAMP,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: payments
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    id                         INTEGER PRIMARY KEY,
    order_id                   INTEGER REFERENCES orders(id),
    method                     VARCHAR(50),
    installments               INTEGER,
    amount                     NUMERIC(12, 2),
    status                     VARCHAR(50),
    paid_at                    TIMESTAMP,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: product_suppliers
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS product_suppliers (
    product_variant_id         INTEGER REFERENCES product_variants(id),
    supplier_id                INTEGER REFERENCES suppliers(id),
    supplier_sku               VARCHAR(50),
    last_quoted_cost           NUMERIC(12, 2),
    lead_time_days             INTEGER,
    is_preferred               BOOLEAN,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP,
    PRIMARY KEY (product_variant_id, supplier_id)
);

-- -----------------------------------------------------------------------
-- Tabela: product_variants
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS product_variants (
    id                         INTEGER PRIMARY KEY,
    product_id                 INTEGER REFERENCES products(id),
    sku                        VARCHAR(50),
    barcode_ean                VARCHAR(50),
    sale_price                 NUMERIC(12, 2),
    cost_price                 NUMERIC(12, 2),
    weight_kg                  NUMERIC(12, 3),
    icms_rate                  NUMERIC(12, 2),
    ipi_rate                   NUMERIC(12, 2),
    is_active                  BOOLEAN,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: products
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id                         INTEGER PRIMARY KEY,
    name                       VARCHAR(50),
    description                VARCHAR(50),
    brand_id                   INTEGER REFERENCES brands(id),
    category_id                INTEGER REFERENCES categories(id),
    ncm_code                   VARCHAR(50),
    unit_of_measure            VARCHAR(50),
    is_active                  BOOLEAN,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: purchase_order_items
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS purchase_order_items (
    id                         INTEGER PRIMARY KEY,
    purchase_order_id          INTEGER REFERENCES purchase_orders(id),
    product_variant_id         INTEGER REFERENCES product_variants(id),
    quantity_ordered           INTEGER,
    unit_cost                  NUMERIC(12, 2),
    line_total                 NUMERIC(12, 2)
);

-- -----------------------------------------------------------------------
-- Tabela: purchase_orders
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS purchase_orders (
    id                         INTEGER PRIMARY KEY,
    po_number                  VARCHAR(50),
    supplier_id                INTEGER REFERENCES suppliers(id),
    buyer_id                   INTEGER REFERENCES employees(id),
    destination_location_id    INTEGER REFERENCES locations(id),
    status                     VARCHAR(50),
    currency                   VARCHAR(50),
    subtotal                   NUMERIC(12, 2),
    total                      NUMERIC(12, 2),
    placed_at                  TIMESTAMP,
    expected_delivery_at       DATE,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: return_items
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS return_items (
    id                         INTEGER PRIMARY KEY,
    return_id                  INTEGER REFERENCES returns(id),
    order_item_id              INTEGER REFERENCES order_items(id),
    quantity                   NUMERIC(12, 3),
    action                     VARCHAR(50),
    exchange_variant_id        INTEGER REFERENCES product_variants(id),
    unit_refund_amount         NUMERIC(12, 2)
);

-- -----------------------------------------------------------------------
-- Tabela: returns
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS returns (
    id                         INTEGER PRIMARY KEY,
    return_number              VARCHAR(50),
    order_id                   INTEGER REFERENCES orders(id),
    customer_id                INTEGER REFERENCES customers(id),
    received_at_location_id    INTEGER REFERENCES locations(id),
    status                     VARCHAR(50),
    reason                     VARCHAR(50),
    total_refund_amount        NUMERIC(12, 2),
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: stock_levels
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stock_levels (
    product_variant_id         INTEGER REFERENCES product_variants(id),
    location_id                INTEGER REFERENCES locations(id),
    quantity_on_hand           NUMERIC(12, 3),
    reorder_point              VARCHAR(255),
    updated_at                 TIMESTAMP,
    PRIMARY KEY (product_variant_id, location_id)
);

-- -----------------------------------------------------------------------
-- Tabela: stock_movements
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stock_movements (
    id                         INTEGER PRIMARY KEY,
    product_variant_id         INTEGER REFERENCES product_variants(id),
    location_id                INTEGER REFERENCES locations(id),
    movement_type              VARCHAR(50),
    quantity                   NUMERIC(12, 3),
    reference_table            VARCHAR(50),
    reference_id               INTEGER,
    employee_id                INTEGER REFERENCES employees(id),
    notes                      VARCHAR(50),
    occurred_at                TIMESTAMP,
    created_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: suppliers
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS suppliers (
    id                         INTEGER PRIMARY KEY,
    legal_name                 VARCHAR(50),
    trade_name                 VARCHAR(50),
    country                    VARCHAR(50),
    tax_id                     VARCHAR(50),
    tax_id_type                VARCHAR(50),
    email                      VARCHAR(50),
    phone                      VARCHAR(50),
    contact_name               VARCHAR(50),
    is_active                  BOOLEAN,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- -----------------------------------------------------------------------
-- Tabela: variant_attribute_values
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS variant_attribute_values (
    product_variant_id         INTEGER REFERENCES product_variants(id),
    attribute_id               INTEGER REFERENCES attributes(id),
    value                      VARCHAR(50),
    PRIMARY KEY (product_variant_id, attribute_id)
);
