WITH RankedDiseases AS (
    SELECT *,
          ROW_NUMBER() OVER (PARTITION BY name ORDER BY ARRAY_LENGTH(treatments) DESC) as rank
    FROM {{ ref('stg_dermatologic_disease_snp') }}
),

tmp_dermatologic_disease AS (
  SELECT
    name as disease_name,
    * except(name, rank, _data_source, dbt_scd_id, dbt_updated_at, dbt_valid_from, dbt_valid_to)
  FROM RankedDiseases
  WHERE rank = 1
    AND dbt_valid_to is null
)

select *
from tmp_dermatologic_disease