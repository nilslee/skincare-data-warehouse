with int_Sephora_Product as (
  select
      product_id, product_name, brand_id, rating, reviews, loves_count, _data_source, _load_time
  from {{ ref('sephora_product') }}
)

select *
from int_Sephora_Product