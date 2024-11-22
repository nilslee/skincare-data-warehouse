{{
    config(
        unique_key='size_id'
    )
}}

with int_Product_Size as (
  select
      ROW_NUMBER() OVER () as size_id, product_id, other_size, imperial_size, metric_size, _load_time
  from {{ ref('int_tmp_cosine_sephora_ingredients') }}
  where other_size is not null
    or imperial_size is not null
    or metric_size is not null
    and dbt_valid_to is null
)

select *
from int_Product_Size
where size_id not in (select size_id from int_Product_Size group by size_id having count(*) > 1)

/// DIDNT USE