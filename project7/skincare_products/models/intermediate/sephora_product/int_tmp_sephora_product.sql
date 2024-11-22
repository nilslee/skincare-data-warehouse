{{
    config(
        unique_key='product_id'
    )
}}

with int_tmp_sephora_product as (
  select
    product_id,
    product_name,
    brand_id,
    brand_name,
    loves_count,
    rating,
    reviews,
    SPLIT(REGEXP_REPLACE(ingredients, r"[\[\]']", ''), ', ') AS ingredients,
    _load_time
  from {{ ref("int_tmp_cosine_sephora_ingredients") }}
  where dbt_valid_to is null
)

select *
from int_tmp_sephora_product
