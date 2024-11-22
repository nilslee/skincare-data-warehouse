{% snapshot int_Dermatologic_Disease_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='id',
          updated_at='_load_time',
        )
    }}

    select * 
	from {{ ref('int_Dermatologic_Disease') }}

{% endsnapshot %}