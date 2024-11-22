{{
    config(
        unique_key='ingredient_name'
    )
}}

WITH mrt_common_ingredient_information as (
  with common_product_ingredients as (
    select
      pi.ingredient_unique_name as ingredient_name,
      dit.disease_name AS treated_disease,  -- delay combining all treated diseases
      count(distinct pi.product_id) as product_count,
    from
      {{ ref('int_Product_Ingredient_snp') }} pi
    left join
      {{ ref('int_Disease_Ingredient_Treatment_snp') }} dit
    on
      pi.ingredient_unique_name = dit.ingredient_unique_name
    where dit.disease_name is not null
    group by
      pi.ingredient_unique_name, dit.disease_name
  ),

  common_ingredient_treatment_information as (
    select
      cpi.ingredient_name,
      cpi.treated_disease,
      cpi.product_count,
      ci.intended_use,
      ci.regulatory_restriction
    from
      common_product_ingredients cpi
    join
      {{ ref('int_Cosmetic_Ingredient_snp') }} ci
    on
      cpi.ingredient_name = ci.ingredient_unique_name
  ),

  ingredient_brand_count as (
    select
      pi.ingredient_unique_name as ingredient_name,
      count(distinct b.brand_id) as brand_count
    from
      {{ ref('int_Brand_snp') }} b
    left join {{ ref('int_Sephora_Product_snp') }} sp on sp.brand_id = b.brand_id
    left join {{ ref('int_Product_Ingredient_snp') }} pi on sp.product_id = pi.product_id
    group by
      pi.ingredient_unique_name
  )

  --  Group ingredient treatment information by product
  select
    citi.ingredient_name,
    STRING_AGG(DISTINCT citi.treated_disease, ', ') AS treated_diseases,  -- Combine all treated diseases
    max(citi.intended_use) as intended_use,  -- Choose the longest intended_use
    string_agg(DISTINCT citi.regulatory_restriction, ', ') as regulatory_restriction,  -- Concatenate all regulatory restrictions
    sum(citi.product_count) as product_count,
    sum(ibc.brand_count) as brand_count
  from
    common_ingredient_treatment_information citi
  left join ingredient_brand_count ibc on ibc.ingredient_name = citi.ingredient_name
  group by
    citi.ingredient_name
  order by product_count desc
)

SELECT *
FROM mrt_common_ingredient_information