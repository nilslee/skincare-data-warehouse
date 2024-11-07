WITH RankedDiseases AS (
    SELECT *,
          ROW_NUMBER() OVER (PARTITION BY name ORDER BY ARRAY_LENGTH(treatments) DESC) as rank
    FROM {{ ref('dermatologic_disease') }}
),

tmp_dermatologic_disease AS (
  SELECT
    name as disease_name,
    * except(name, rank, _data_source, _load_time)
  FROM RankedDiseases
  WHERE rank = 1
)

select *
from tmp_dermatologic_disease