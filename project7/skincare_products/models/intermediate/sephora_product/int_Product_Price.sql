{{
    config(
        unique_key='price_id'
    )
}}

with int_Product_Price as (
  select
      ROW_NUMBER() OVER () as price_id,
      product_id,
      price_usd,
      value_price_usd,
      sale_price_usd, _load_time
  from {{ ref('int_tmp_cosine_sephora_ingredients') }}
  where price_usd is not null
    or value_price_usd is not null
    or sale_price_usd is not null
    and dbt_valid_to is null
)

select *
from int_Product_Price
where price_id not in (select price_id from int_Product_Price group by price_id having count(*) > 1)