with aggregate_skin_type_ratings as (
  select
      sr.skin_type as skin_condition,
      avg(sr.rating) as average_rating
  from
      {{ ref('Sephora_Product_Review') }} sr
  where
      sr.skin_type is not null
  group by
      skin_condition
  order by
      skin_condition
)

select *
from aggregate_skin_type_ratings