-- ADD PRE RUN CODE TO INSERT any treatment that is not found in cosmetic ingredient's ingredient_unique_name col
{{ config(
    unique_key='id',
    pre_hook="{{ insert_missing_treatments() }}",
    post_hook="ALTER TABLE {{ ref('int_Dermatologic_Disease') }} DROP COLUMN treatments"
) }}


-- ADD POST RUN CODE TO DROP treatments COLUMN in dermatologic_disease table

WITH Disease_Ingredient_Treatment as (
  SELECT
    dd.disease_name, -- Primary key from the dermatologic_disease table
    ci.ingredient_unique_name, -- Primary key from the cosmetic_ingredient table
    dd._load_time
  FROM
    (SELECT
        disease_name,
        ingredient,
        _load_time -- Split the treatments into individual ingredients
    FROM
        {{ ref('int_Dermatologic_Disease') }},
        UNNEST(treatments) as ingredient
    WHERE ARRAY_LENGTH(treatments) > 0) dd
  JOIN
    {{ ref('int_Cosmetic_Ingredient') }} ci
  ON
    ci.ingredient_unique_name = dd.ingredient
)

SELECT *
FROM Disease_Ingredient_Treatment