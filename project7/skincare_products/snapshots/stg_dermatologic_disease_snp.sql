{% snapshot stg_dermatologic_disease_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='id',
          updated_at='_load_time',
        )
    }}

    select *
  from {{ ref('stg_dermatologic_disease') }}

{% endsnapshot %}