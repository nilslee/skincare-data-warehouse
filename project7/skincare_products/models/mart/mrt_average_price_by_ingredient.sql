{{
    config(
        unique_key='ingredient_unique_name'
    )
}}

with average_price_by_ingredient as (
  select
      i.ingredient_unique_name,
      avg(pp.price_usd) as average_price,
      count(distinct p.product_id) as product_count
  from
      {{ ref('int_Product_Ingredient_snp') }} i
  join
      {{ ref('int_Sephora_Product_snp') }} p
  on
      i.product_id = p.product_id
  join
      {{ ref('int_Product_Price_snp') }} pp
  on
      p.product_id = pp.product_id
  group by
      i.ingredient_unique_name
  order by
      product_count desc
)

select *
from average_price_by_ingredient