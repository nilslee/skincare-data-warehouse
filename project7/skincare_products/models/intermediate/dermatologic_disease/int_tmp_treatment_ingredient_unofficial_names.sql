WITH flattened_treatments AS (
  -- Flatten the array into individual rows
  SELECT
    LOWER(TRIM(treatment)) AS treatment -- Convert to lowercase and trim spaces to handle case/whitespace variations
  FROM
    {{ ref('int_tmp_dermatologic_disease') }},
    UNNEST(treatments) AS treatment -- Unnest the arrays into individual strings
  WHERE
    treatments IS NOT NULL
),
-- Select distinct treatments and sort them alphabetically
tmp_treatment_ingredient_unofficial_names AS (
  SELECT DISTINCT treatment AS ingredient
  FROM flattened_treatments
  ORDER BY ingredient
)

SELECT *
FROM tmp_treatment_ingredient_unofficial_names