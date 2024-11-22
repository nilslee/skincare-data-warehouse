{{
    config(
        unique_key='product_id'
    )
}}

with int_Sephora_Product as (
  select
      product_id, product_name, brand_id, rating, reviews, loves_count, _data_source, _load_time
  from {{ ref('int_tmp_cosine_sephora_ingredients') }}
  where dbt_valid_to is null
)

select *
from int_Sephora_Product
where product_id not in (select product_id from int_Sephora_Product group by product_id having count(*) > 1)