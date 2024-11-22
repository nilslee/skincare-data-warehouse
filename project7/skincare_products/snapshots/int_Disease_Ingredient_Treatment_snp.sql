{% snapshot int_Disease_Ingredient_Treatment_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='id',
          updated_at='_load_time',
        )
    }}

    select 
    coalesce(disease_name, '') || '-' || 
    coalesce(ingredient_unique_name, '') as id, * 
	from {{ ref('int_Disease_Ingredient_Treatment') }}

{% endsnapshot %}