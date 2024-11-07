with stg_skin_disease_picture as (
  select
    case skin_condition_name
      when 'N/A' then null
      when '\\N' then null
      when '' then null
      else skin_condition_name
      end as skin_condition_name,
    case skin_color
      when 'N/A' then null
      when '\\N' then null
      when '' then null
      else skin_color
      end as affected_skin_color,
    case severity
      when 'N/A' then null
      when '\\N' then null
      when '' then null
      else severity
      end as severity,
    case image_link
      when 'N/A' then null
      when '\\N' then null
      when '' then null
      else image_link
      end as image_link,
      _data_source, _load_time
  from {{ ref("tmp_skin_disease_picture_color") }}
)

select *
from stg_skin_disease_picture