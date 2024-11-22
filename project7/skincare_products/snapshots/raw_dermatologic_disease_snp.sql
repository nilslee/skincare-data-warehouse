{% snapshot raw_dermatologic_disease_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='id',
          updated_at='_load_time',
        )
    }}

  select 
    coalesce(`name`, '') || '-' || 
    coalesce(physical_description, '') || '-' || 
    coalesce(causes, '') || '-' || 
    coalesce(treatments, '') as id, *
	  from {{ source('skincare_products_raw', 'dermatologic_disease') }}

{% endsnapshot %}