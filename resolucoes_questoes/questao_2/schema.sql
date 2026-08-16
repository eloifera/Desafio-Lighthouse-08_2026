-- ==============================================================================

-- Schema Relacional PostgreSQL com Foreign Keys

-- ==============================================================================


-- ==============================================================================

-- ETAPA 1: ESTRUTURA DAS TABELAS

-- ==============================================================================


-- ------------------------------------------------------------------------
-- Tabela: addresses
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS addresses (
    id                         INTEGER PRIMARY KEY,
    customer_id                INTEGER,
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

-- ------------------------------------------------------------------------
-- Tabela: attributes
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attributes (
    id                         INTEGER PRIMARY KEY,
    name                       VARCHAR(50),
    data_type                  VARCHAR(50)
);

-- ------------------------------------------------------------------------
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

-- ------------------------------------------------------------------------
-- Tabela: categories
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    id                         INTEGER PRIMARY KEY,
    name                       VARCHAR(50),
    slug                       VARCHAR(50),
    parent_category_id         INTEGER,
    is_active                  BOOLEAN,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- ------------------------------------------------------------------------
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

-- ------------------------------------------------------------------------
-- Tabela: employees
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS employees (
    id                         INTEGER PRIMARY KEY,
    full_name                  VARCHAR(50),
    cpf                        VARCHAR(50),
    email                      VARCHAR(50),
    role                       VARCHAR(50),
    primary_location_id        INTEGER,
    hire_date                  DATE,
    termination_date           DATE,
    is_active                  BOOLEAN,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- ------------------------------------------------------------------------
-- Tabela: fiscal_invoices
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fiscal_invoices (
    id                         INTEGER PRIMARY KEY,
    order_id                   INTEGER,
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

-- ------------------------------------------------------------------------
-- Tabela: goods_receipt_items
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS goods_receipt_items (
    id                         INTEGER PRIMARY KEY,
    goods_receipt_id           INTEGER,
    purchase_order_item_id     INTEGER,
    quantity_received          NUMERIC(12, 3)
);

-- ------------------------------------------------------------------------
-- Tabela: goods_receipts
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS goods_receipts (
    id                         INTEGER PRIMARY KEY,
    purchase_order_id          INTEGER,
    received_by_employee_id    INTEGER,
    received_at                TIMESTAMP,
    notes                      VARCHAR(50),
    created_at                 TIMESTAMP
);

-- ------------------------------------------------------------------------
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

-- ------------------------------------------------------------------------
-- Tabela: order_items
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
    id                         INTEGER PRIMARY KEY,
    order_id                   INTEGER,
    product_variant_id         INTEGER,
    quantity                   INTEGER,
    unit_price                 NUMERIC(12, 2),
    icms_rate                  NUMERIC(12, 2),
    ipi_rate                   NUMERIC(12, 2),
    line_total                 NUMERIC(12, 2)
);

-- ------------------------------------------------------------------------
-- Tabela: orders
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id                         INTEGER PRIMARY KEY,
    order_number               VARCHAR(50),
    channel                    VARCHAR(50),
    customer_id                INTEGER,
    salesperson_id             INTEGER,
    location_id                INTEGER,
    status                     VARCHAR(50),
    subtotal                   NUMERIC(12, 2),
    discount_amount            NUMERIC(12, 2),
    total                      NUMERIC(12, 2),
    placed_at                  TIMESTAMP,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- ------------------------------------------------------------------------
-- Tabela: payments
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    id                         INTEGER PRIMARY KEY,
    order_id                   INTEGER,
    method                     VARCHAR(50),
    installments               INTEGER,
    amount                     NUMERIC(12, 2),
    status                     VARCHAR(50),
    paid_at                    TIMESTAMP,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- ------------------------------------------------------------------------
-- Tabela: product_suppliers
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS product_suppliers (
    product_variant_id         INTEGER,
    supplier_id                INTEGER,
    supplier_sku               VARCHAR(50),
    last_quoted_cost           NUMERIC(12, 2),
    lead_time_days             INTEGER,
    is_preferred               BOOLEAN,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP,
    PRIMARY KEY (product_variant_id, supplier_id)
);

-- ------------------------------------------------------------------------
-- Tabela: product_variants
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS product_variants (
    id                         INTEGER PRIMARY KEY,
    product_id                 INTEGER,
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

-- ------------------------------------------------------------------------
-- Tabela: products
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id                         INTEGER PRIMARY KEY,
    name                       VARCHAR(50),
    description                VARCHAR(50),
    brand_id                   INTEGER,
    category_id                INTEGER,
    ncm_code                   VARCHAR(50),
    unit_of_measure            VARCHAR(50),
    is_active                  BOOLEAN,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- ------------------------------------------------------------------------
-- Tabela: purchase_order_items
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS purchase_order_items (
    id                         INTEGER PRIMARY KEY,
    purchase_order_id          INTEGER,
    product_variant_id         INTEGER,
    quantity_ordered           INTEGER,
    unit_cost                  NUMERIC(12, 2),
    line_total                 NUMERIC(12, 2)
);

-- ------------------------------------------------------------------------
-- Tabela: purchase_orders
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS purchase_orders (
    id                         INTEGER PRIMARY KEY,
    po_number                  VARCHAR(50),
    supplier_id                INTEGER,
    buyer_id                   INTEGER,
    destination_location_id    INTEGER,
    status                     VARCHAR(50),
    currency                   VARCHAR(50),
    subtotal                   NUMERIC(12, 2),
    total                      NUMERIC(12, 2),
    placed_at                  TIMESTAMP,
    expected_delivery_at       DATE,
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- ------------------------------------------------------------------------
-- Tabela: return_items
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS return_items (
    id                         INTEGER PRIMARY KEY,
    return_id                  INTEGER,
    order_item_id              INTEGER,
    quantity                   NUMERIC(12, 3),
    action                     VARCHAR(50),
    exchange_variant_id        INTEGER,
    unit_refund_amount         NUMERIC(12, 2)
);

-- ------------------------------------------------------------------------
-- Tabela: returns
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS returns (
    id                         INTEGER PRIMARY KEY,
    return_number              VARCHAR(50),
    order_id                   INTEGER,
    customer_id                INTEGER,
    received_at_location_id    INTEGER,
    status                     VARCHAR(50),
    reason                     VARCHAR(50),
    total_refund_amount        NUMERIC(12, 2),
    created_at                 TIMESTAMP,
    updated_at                 TIMESTAMP
);

-- ------------------------------------------------------------------------
-- Tabela: stock_levels
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stock_levels (
    product_variant_id         INTEGER,
    location_id                INTEGER,
    quantity_on_hand           NUMERIC(12, 3),
    reorder_point              VARCHAR(255),
    updated_at                 TIMESTAMP,
    PRIMARY KEY (product_variant_id, location_id)
);

-- ------------------------------------------------------------------------
-- Tabela: stock_movements
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stock_movements (
    id                         INTEGER PRIMARY KEY,
    product_variant_id         INTEGER,
    location_id                INTEGER,
    movement_type              VARCHAR(50),
    quantity                   NUMERIC(12, 3),
    reference_table            VARCHAR(50),
    reference_id               INTEGER,
    employee_id                INTEGER,
    notes                      VARCHAR(50),
    occurred_at                TIMESTAMP,
    created_at                 TIMESTAMP
);

-- ------------------------------------------------------------------------
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

-- ------------------------------------------------------------------------
-- Tabela: variant_attribute_values
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS variant_attribute_values (
    product_variant_id         INTEGER,
    attribute_id               INTEGER,
    value                      VARCHAR(50),
    PRIMARY KEY (product_variant_id, attribute_id)
);

-- ==============================================================================

-- ETAPA 2: FOREIGN KEYS

-- ==============================================================================


ALTER TABLE addresses DROP CONSTRAINT IF EXISTS fk_addresses_customer_id;
ALTER TABLE addresses
    ADD CONSTRAINT fk_addresses_customer_id
    FOREIGN KEY (customer_id)
    REFERENCES customers(id);

ALTER TABLE categories DROP CONSTRAINT IF EXISTS fk_categories_parent_category_id;
ALTER TABLE categories
    ADD CONSTRAINT fk_categories_parent_category_id
    FOREIGN KEY (parent_category_id)
    REFERENCES categories(id);

ALTER TABLE employees DROP CONSTRAINT IF EXISTS fk_employees_primary_location_id;
ALTER TABLE employees
    ADD CONSTRAINT fk_employees_primary_location_id
    FOREIGN KEY (primary_location_id)
    REFERENCES locations(id);

ALTER TABLE fiscal_invoices DROP CONSTRAINT IF EXISTS fk_fiscal_invoices_order_id;
ALTER TABLE fiscal_invoices
    ADD CONSTRAINT fk_fiscal_invoices_order_id
    FOREIGN KEY (order_id)
    REFERENCES orders(id);

ALTER TABLE goods_receipt_items DROP CONSTRAINT IF EXISTS fk_goods_receipt_items_goods_receipt_id;
ALTER TABLE goods_receipt_items
    ADD CONSTRAINT fk_goods_receipt_items_goods_receipt_id
    FOREIGN KEY (goods_receipt_id)
    REFERENCES goods_receipts(id);

ALTER TABLE goods_receipt_items DROP CONSTRAINT IF EXISTS fk_goods_receipt_items_purchase_order_item_id;
ALTER TABLE goods_receipt_items
    ADD CONSTRAINT fk_goods_receipt_items_purchase_order_item_id
    FOREIGN KEY (purchase_order_item_id)
    REFERENCES purchase_order_items(id);

ALTER TABLE goods_receipts DROP CONSTRAINT IF EXISTS fk_goods_receipts_purchase_order_id;
ALTER TABLE goods_receipts
    ADD CONSTRAINT fk_goods_receipts_purchase_order_id
    FOREIGN KEY (purchase_order_id)
    REFERENCES purchase_orders(id);

ALTER TABLE goods_receipts DROP CONSTRAINT IF EXISTS fk_goods_receipts_received_by_employee_id;
ALTER TABLE goods_receipts
    ADD CONSTRAINT fk_goods_receipts_received_by_employee_id
    FOREIGN KEY (received_by_employee_id)
    REFERENCES employees(id);

ALTER TABLE order_items DROP CONSTRAINT IF EXISTS fk_order_items_order_id;
ALTER TABLE order_items
    ADD CONSTRAINT fk_order_items_order_id
    FOREIGN KEY (order_id)
    REFERENCES orders(id);

ALTER TABLE order_items DROP CONSTRAINT IF EXISTS fk_order_items_product_variant_id;
ALTER TABLE order_items
    ADD CONSTRAINT fk_order_items_product_variant_id
    FOREIGN KEY (product_variant_id)
    REFERENCES product_variants(id);

ALTER TABLE orders DROP CONSTRAINT IF EXISTS fk_orders_customer_id;
ALTER TABLE orders
    ADD CONSTRAINT fk_orders_customer_id
    FOREIGN KEY (customer_id)
    REFERENCES customers(id);

ALTER TABLE orders DROP CONSTRAINT IF EXISTS fk_orders_salesperson_id;
ALTER TABLE orders
    ADD CONSTRAINT fk_orders_salesperson_id
    FOREIGN KEY (salesperson_id)
    REFERENCES employees(id);

ALTER TABLE orders DROP CONSTRAINT IF EXISTS fk_orders_location_id;
ALTER TABLE orders
    ADD CONSTRAINT fk_orders_location_id
    FOREIGN KEY (location_id)
    REFERENCES locations(id);

ALTER TABLE payments DROP CONSTRAINT IF EXISTS fk_payments_order_id;
ALTER TABLE payments
    ADD CONSTRAINT fk_payments_order_id
    FOREIGN KEY (order_id)
    REFERENCES orders(id);

ALTER TABLE product_suppliers DROP CONSTRAINT IF EXISTS fk_product_suppliers_product_variant_id;
ALTER TABLE product_suppliers
    ADD CONSTRAINT fk_product_suppliers_product_variant_id
    FOREIGN KEY (product_variant_id)
    REFERENCES product_variants(id);

ALTER TABLE product_suppliers DROP CONSTRAINT IF EXISTS fk_product_suppliers_supplier_id;
ALTER TABLE product_suppliers
    ADD CONSTRAINT fk_product_suppliers_supplier_id
    FOREIGN KEY (supplier_id)
    REFERENCES suppliers(id);

ALTER TABLE product_variants DROP CONSTRAINT IF EXISTS fk_product_variants_product_id;
ALTER TABLE product_variants
    ADD CONSTRAINT fk_product_variants_product_id
    FOREIGN KEY (product_id)
    REFERENCES products(id);

ALTER TABLE products DROP CONSTRAINT IF EXISTS fk_products_brand_id;
ALTER TABLE products
    ADD CONSTRAINT fk_products_brand_id
    FOREIGN KEY (brand_id)
    REFERENCES brands(id);

ALTER TABLE products DROP CONSTRAINT IF EXISTS fk_products_category_id;
ALTER TABLE products
    ADD CONSTRAINT fk_products_category_id
    FOREIGN KEY (category_id)
    REFERENCES categories(id);

ALTER TABLE purchase_order_items DROP CONSTRAINT IF EXISTS fk_purchase_order_items_purchase_order_id;
ALTER TABLE purchase_order_items
    ADD CONSTRAINT fk_purchase_order_items_purchase_order_id
    FOREIGN KEY (purchase_order_id)
    REFERENCES purchase_orders(id);

ALTER TABLE purchase_order_items DROP CONSTRAINT IF EXISTS fk_purchase_order_items_product_variant_id;
ALTER TABLE purchase_order_items
    ADD CONSTRAINT fk_purchase_order_items_product_variant_id
    FOREIGN KEY (product_variant_id)
    REFERENCES product_variants(id);

ALTER TABLE purchase_orders DROP CONSTRAINT IF EXISTS fk_purchase_orders_supplier_id;
ALTER TABLE purchase_orders
    ADD CONSTRAINT fk_purchase_orders_supplier_id
    FOREIGN KEY (supplier_id)
    REFERENCES suppliers(id);

ALTER TABLE purchase_orders DROP CONSTRAINT IF EXISTS fk_purchase_orders_buyer_id;
ALTER TABLE purchase_orders
    ADD CONSTRAINT fk_purchase_orders_buyer_id
    FOREIGN KEY (buyer_id)
    REFERENCES employees(id);

ALTER TABLE purchase_orders DROP CONSTRAINT IF EXISTS fk_purchase_orders_destination_location_id;
ALTER TABLE purchase_orders
    ADD CONSTRAINT fk_purchase_orders_destination_location_id
    FOREIGN KEY (destination_location_id)
    REFERENCES locations(id);

ALTER TABLE return_items DROP CONSTRAINT IF EXISTS fk_return_items_return_id;
ALTER TABLE return_items
    ADD CONSTRAINT fk_return_items_return_id
    FOREIGN KEY (return_id)
    REFERENCES returns(id);

ALTER TABLE return_items DROP CONSTRAINT IF EXISTS fk_return_items_order_item_id;
ALTER TABLE return_items
    ADD CONSTRAINT fk_return_items_order_item_id
    FOREIGN KEY (order_item_id)
    REFERENCES order_items(id);

ALTER TABLE return_items DROP CONSTRAINT IF EXISTS fk_return_items_exchange_variant_id;
ALTER TABLE return_items
    ADD CONSTRAINT fk_return_items_exchange_variant_id
    FOREIGN KEY (exchange_variant_id)
    REFERENCES product_variants(id);

ALTER TABLE returns DROP CONSTRAINT IF EXISTS fk_returns_order_id;
ALTER TABLE returns
    ADD CONSTRAINT fk_returns_order_id
    FOREIGN KEY (order_id)
    REFERENCES orders(id);

ALTER TABLE returns DROP CONSTRAINT IF EXISTS fk_returns_customer_id;
ALTER TABLE returns
    ADD CONSTRAINT fk_returns_customer_id
    FOREIGN KEY (customer_id)
    REFERENCES customers(id);

ALTER TABLE returns DROP CONSTRAINT IF EXISTS fk_returns_received_at_location_id;
ALTER TABLE returns
    ADD CONSTRAINT fk_returns_received_at_location_id
    FOREIGN KEY (received_at_location_id)
    REFERENCES locations(id);

ALTER TABLE stock_levels DROP CONSTRAINT IF EXISTS fk_stock_levels_product_variant_id;
ALTER TABLE stock_levels
    ADD CONSTRAINT fk_stock_levels_product_variant_id
    FOREIGN KEY (product_variant_id)
    REFERENCES product_variants(id);

ALTER TABLE stock_levels DROP CONSTRAINT IF EXISTS fk_stock_levels_location_id;
ALTER TABLE stock_levels
    ADD CONSTRAINT fk_stock_levels_location_id
    FOREIGN KEY (location_id)
    REFERENCES locations(id);

ALTER TABLE stock_movements DROP CONSTRAINT IF EXISTS fk_stock_movements_product_variant_id;
ALTER TABLE stock_movements
    ADD CONSTRAINT fk_stock_movements_product_variant_id
    FOREIGN KEY (product_variant_id)
    REFERENCES product_variants(id);

ALTER TABLE stock_movements DROP CONSTRAINT IF EXISTS fk_stock_movements_location_id;
ALTER TABLE stock_movements
    ADD CONSTRAINT fk_stock_movements_location_id
    FOREIGN KEY (location_id)
    REFERENCES locations(id);

ALTER TABLE stock_movements DROP CONSTRAINT IF EXISTS fk_stock_movements_employee_id;
ALTER TABLE stock_movements
    ADD CONSTRAINT fk_stock_movements_employee_id
    FOREIGN KEY (employee_id)
    REFERENCES employees(id);

ALTER TABLE variant_attribute_values DROP CONSTRAINT IF EXISTS fk_variant_attribute_values_product_variant_id;
ALTER TABLE variant_attribute_values
    ADD CONSTRAINT fk_variant_attribute_values_product_variant_id
    FOREIGN KEY (product_variant_id)
    REFERENCES product_variants(id);

ALTER TABLE variant_attribute_values DROP CONSTRAINT IF EXISTS fk_variant_attribute_values_attribute_id;
ALTER TABLE variant_attribute_values
    ADD CONSTRAINT fk_variant_attribute_values_attribute_id
    FOREIGN KEY (attribute_id)
    REFERENCES attributes(id);
