{% macro insert_missing_treatments() %}

INSERT INTO {{ ref('int_Cosmetic_Ingredient') }} (ingredient_unique_name)
SELECT DISTINCT dd.ingredient
FROM (
    SELECT ingredient
    FROM {{ ref('int_Dermatologic_Disease') }},
    UNNEST(treatments) AS ingredient
    WHERE ARRAY_LENGTH(treatments) > 0 AND ingredient != "[]"
) dd
LEFT JOIN {{ ref('int_Cosmetic_Ingredient') }} ci
ON dd.ingredient = ci.ingredient_unique_name
WHERE ci.ingredient_unique_name IS NULL;

{% endmacro %}
