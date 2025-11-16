\connect winwin;

-- category
COPY dim_category(
cls_1, cls_2, cls_3, category)
FROM '/data/dim_category.csv'
WITH(FORMAT csv, HEADER true);

-- product
COPY dim_product(
product_id, product_name, manufacturer_code, manufacturer_name, group_id, group_name, brand_id, brand_name, cls_1,
cls_2, cls_3, category, unit, spec, package, launch_time, price)
FROM '/data/dim_product.csv'
WITH(FORMAT csv, HEADER true);

-- product_sales_monthly1 - part 1
COPY product_sales_monthly(
biz_date, region_name, province_name, channel, category, group_id, group_name, brand_id, brand_name, product_id, amount,
quantity, branch_count, cls_branch_amount)
FROM '/data/product_sales_monthly_part1.csv'
WITH(FORMAT csv, HEADER true);

-- product_sales_monthly1 - part 2
COPY product_sales_monthly(
biz_date, region_name, province_name, channel, category, group_id, group_name, brand_id, brand_name, product_id, amount,
quantity, branch_count, cls_branch_amount)
FROM '/data/product_sales_monthly_part2.csv'
WITH(FORMAT csv, HEADER true);

-- product_sales_monthly1 - part 3
COPY product_sales_monthly(
biz_date, region_name, province_name, channel, category, group_id, group_name, brand_id, brand_name, product_id, amount,
quantity, branch_count, cls_branch_amount)
FROM '/data/product_sales_monthly_part3.csv'
WITH(FORMAT csv, HEADER true);