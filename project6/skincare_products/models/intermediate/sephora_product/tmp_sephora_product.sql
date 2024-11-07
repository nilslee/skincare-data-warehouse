with tmp_sephora_product as (
  select
    product_id,
    product_name,
    brand_id,
    brand_name,
    loves_count,
    rating,
    reviews,
    SPLIT(REGEXP_REPLACE(ingredients, r"[\[\]']", ''), ', ') AS ingredients,
  from {{ ref("tmp_cosine_sephora_ingredients") }}
)

select *
from tmp_sephora_product