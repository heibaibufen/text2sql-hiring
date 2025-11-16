-- PostgreSQL‑ready DDL
-- All key columns are NOT NULL and declared PRIMARY KEY.
-- Monetary fields use float8 for exact precision.
-- COUNT fields use float8.
-- Timestamps use the shorthand TIMESTAMPTZ.

\connect winwin;


-- ===========================
-- Category
-- ===========================
CREATE TABLE dim_category (
  cls_1 TEXT,
  cls_2 TEXT,
  cls_3 TEXT,
  category TEXT PRIMARY KEY
);

COMMENT ON TABLE dim_category IS '类目结构表';
COMMENT ON COLUMN dim_category.cls_1 IS '一级类目名称';
COMMENT ON COLUMN dim_category.cls_2 IS '二级类目名称';
COMMENT ON COLUMN dim_category.cls_3 IS '三级类目名称';
COMMENT ON COLUMN dim_category.category IS '类目;四级类目';


-- ===========================
-- Product dimension
-- ===========================
CREATE TABLE dim_product (
    product_id   TEXT PRIMARY KEY NOT NULL,
    product_name TEXT NOT NULL,
    manufacturer_code    TEXT,
    manufacturer_name    TEXT,
    group_id     float8,
    group_name   TEXT,
    brand_id     float8,
    brand_name   TEXT,
    cls_1        TEXT,
    cls_2        TEXT,
    cls_3        TEXT,
    category     TEXT NOT  NULL
      REFERENCES dim_category (category)
      ON DELETE RESTRICT,
    unit         TEXT,
    spec         TEXT,
    package      TEXT,
    launch_time  TIMESTAMPTZ,
    price        float8
);

COMMENT ON TABLE dim_product IS '商品表;商品维度表';
COMMENT ON COLUMN dim_product.product_id IS '条码';
COMMENT ON COLUMN dim_product.product_name IS '商品名称';
COMMENT ON COLUMN dim_product.manufacturer_code IS '厂商ID';
COMMENT ON COLUMN dim_product.manufacturer_name IS '厂商名称';
COMMENT ON COLUMN dim_product.group_id IS '集团ID';
COMMENT ON COLUMN dim_product.group_name IS '集团名称';
COMMENT ON COLUMN dim_product.brand_id IS '品牌ID';
COMMENT ON COLUMN dim_product.brand_name IS '品牌名称';
COMMENT ON COLUMN dim_product.cls_1 IS '一级类目';
COMMENT ON COLUMN dim_product.cls_2 IS '二级类目';
COMMENT ON COLUMN dim_product.cls_3 IS '三级类目';
COMMENT ON COLUMN dim_product.category IS '类目;四级类目';
COMMENT ON COLUMN dim_product.unit IS '单位';
COMMENT ON COLUMN dim_product.spec IS '规格';
COMMENT ON COLUMN dim_product.package IS '包装';
COMMENT ON COLUMN dim_product.launch_time IS '上市时间';
COMMENT ON COLUMN dim_product.price IS '售价;商品价格;商品中位价';
-- ===========================
-- Product‑level sales
-- ===========================
CREATE TABLE product_sales_monthly (
    id SERIAL PRIMARY KEY,
    biz_date TIMESTAMPTZ NOT NULL,
    region_name TEXT,
    province_name TEXT,
    channel TEXT,
    category TEXT NOT NULL
      REFERENCES dim_category (category)
      ON DELETE RESTRICT,
    group_id   float8,
    group_name TEXT,
    brand_id   float8,
    brand_name TEXT,
    product_id TEXT NOT NULL
      REFERENCES dim_product (product_id)
        ON DELETE RESTRICT,
    amount float8,
    quantity float8,
    branch_count float8,
    cls_branch_amount float8,
    UNIQUE(biz_date, region_name, province_name, channel, product_id)
);

COMMENT ON TABLE product_sales_monthly IS '商品的月度销售表';
COMMENT ON COLUMN product_sales_monthly.biz_date IS '时间';
COMMENT ON COLUMN product_sales_monthly.region_name IS '大区;地区';
COMMENT ON COLUMN product_sales_monthly.province_name IS '省份';
COMMENT ON COLUMN product_sales_monthly.channel IS '业态';
COMMENT ON COLUMN product_sales_monthly.category IS '类目;四级类目';
COMMENT ON COLUMN product_sales_monthly.group_id IS '集团ID';
COMMENT ON COLUMN product_sales_monthly.group_name IS '集团名称';
COMMENT ON COLUMN product_sales_monthly.brand_id IS '品牌ID';
COMMENT ON COLUMN product_sales_monthly.brand_name IS '品牌名称';
COMMENT ON COLUMN product_sales_monthly.product_id IS '条码';
COMMENT ON COLUMN product_sales_monthly.amount IS '商品的销售额';
COMMENT ON COLUMN product_sales_monthly.quantity IS '商品的销量';
COMMENT ON COLUMN product_sales_monthly.branch_count IS '商品的在售门店数';
COMMENT ON COLUMN product_sales_monthly.cls_branch_amount IS '商品的在售门店的类目销售额';
