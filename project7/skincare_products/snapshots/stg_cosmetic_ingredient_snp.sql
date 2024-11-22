{% snapshot stg_cosmetic_ingredient_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='cosing_ref_no',
          updated_at='_load_time',
        )
    }}

    select * 
	from {{ ref('stg_cosmetic_ingredient') }}

{% endsnapshot %}