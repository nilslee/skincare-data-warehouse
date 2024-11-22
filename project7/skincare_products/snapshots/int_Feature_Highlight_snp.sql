{% snapshot int_Feature_Highlight_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='highlight_id',
          updated_at='_load_time',
        )
    }}

    select * 
	from {{ ref('int_Feature_Highlight') }}

{% endsnapshot %}