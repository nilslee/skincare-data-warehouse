WITH tmp_sephora_product_review AS (
  SELECT
    sp.*,
    b.brand_id
  FROM
    {{ ref('sephora_product_review') }} sp
  LEFT JOIN
    {{ ref('Brand') }} b
  ON
    sp.brand_name = b.brand_name
),

int_sephora_product_review AS (
  WITH numbered_rows AS (
    SELECT
      ROW_NUMBER() OVER () AS review_id,
      * except(_data_source, _load_time)
    FROM
      tmp_sephora_product_review
  )
  SELECT
    * except(product_name, brand_name)
  FROM
    numbered_rows
)

SELECT *
FROM int_sephora_product_review