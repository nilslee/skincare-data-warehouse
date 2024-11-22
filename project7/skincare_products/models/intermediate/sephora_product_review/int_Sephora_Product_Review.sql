{{
    config(
        unique_key='review_id'
    )
}}

WITH tmp_sephora_product_review AS (
  SELECT
    sp.*,
    b.brand_id
  FROM
    {{ ref('stg_sephora_product_review_snp') }} sp
  LEFT JOIN
    {{ ref('int_Brand') }} b
  ON
    sp.brand_name = b.brand_name
  where sp.dbt_valid_to is null
),

int_Sephora_Product_Review AS (
  WITH numbered_rows AS (
    SELECT
      ROW_NUMBER() OVER () AS review_id,
      * except(dbt_scd_id, dbt_updated_at, dbt_valid_from, dbt_valid_to)
    FROM
      tmp_sephora_product_review
  )
  SELECT
    * except(product_name, brand_name)
  FROM
    numbered_rows
)

SELECT *
FROM int_Sephora_Product_Review
where review_id not in (select review_id from int_Sephora_Product_Review group by review_id having count(*) > 1)