{{
    config(
        unique_key='variation_id'
    )
}}

with int_Product_Variation as (
  select
      ROW_NUMBER() OVER () as variation_id, product_id, variation_count, variation_max_price, variation_min_price, _load_time
  from {{ ref('int_tmp_cosine_sephora_ingredients') }}
  where variation_count is not null
    or variation_max_price is not null
    or variation_min_price is not null
    and dbt_valid_to is null
)

select *
from int_Product_Variation
where variation_id not in (select variation_id from int_Product_Variation group by variation_id having count(*) > 1)