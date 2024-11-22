{{
    config(
        unique_key='cosing_ref_no'
    )
}}


with stg_cosmetic_ingredient as (
  select
  safe_cast(cosing_ref_no as INTEGER) as cosing_ref_no,
  case ingredient_unique_name when '' then null else ingredient_unique_name end as ingredient_unique_name,
  case ingredient_common_name when '' then null else ingredient_common_name end as ingredient_common_name,
  case european_pharmacopoeia_name when '' then null else european_pharmacopoeia_name end as european_pharmacopoeia_name,
  case
    when cas_no in (' ', ' -') then null
    else cas_no
  end as cas_no,
  case
    when ec_no in (' ', ' ,', ' -', ' - ', ' - / -') then null
    else ec_no
  end as ec_no,
  case restriction when '' then null else restriction end as regulatory_restriction,
  case function when '' then null else function end as intended_use,
  case update_date when '' then null else safe_cast(update_date as DATE format 'DD/MM/YYYY') end as update_date,
  _data_source,
   _load_time
  from {{ ref('raw_cosmetic_ingredient_snp') }} 
  where dbt_valid_to is null
)

select *
from stg_cosmetic_ingredient