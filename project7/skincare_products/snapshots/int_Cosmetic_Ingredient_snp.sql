{% snapshot int_Cosmetic_Ingredient_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='ingredient_unique_name',
          updated_at='_load_time',
        )
    }}

    select * 
	from {{ ref('int_Cosmetic_Ingredient') }}

{% endsnapshot %}