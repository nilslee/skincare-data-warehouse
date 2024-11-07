with int_Product_Size as (
  select
      ROW_NUMBER() OVER () as size_id, product_id, other_size, imperial_size, metric_size
  from {{ ref('sephora_product') }}
  where other_size is not null
    or imperial_size is not null
    or metric_size is not null
)

select *
from int_Product_Size