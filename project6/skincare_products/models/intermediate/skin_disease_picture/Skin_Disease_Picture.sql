with int_Skin_Disease_Picture as (
  select
    ROW_NUMBER() OVER () as picture_id,
    skin_condition_name as disease_name,
    affected_skin_color,
    severity,
    image_link,
  from {{ ref('tmp_skin_disease_picture_name_int') }}
  order by skin_condition_name
)

select *
from int_Skin_Disease_Picture