with average_price_by_ingredient as (
  select
      i.ingredient_unique_name,
      avg(pp.price_usd) as average_price,
      count(distinct p.product_id) as product_count
  from
      {{ ref('Product_Ingredient') }} i
  join
      {{ ref('Sephora_Product') }} p
  on
      i.product_id = p.product_id
  join
      {{ ref('Product_Price') }} pp
  on
      p.product_id = pp.product_id
  group by
      i.ingredient_unique_name
  order by
      product_count desc
)

select *
from average_price_by_ingredient