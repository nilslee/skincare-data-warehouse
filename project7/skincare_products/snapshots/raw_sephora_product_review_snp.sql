{% snapshot raw_sephora_product_review_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='id',
          updated_at='_load_time',
        )
    }}

    select row_number || '-' || author_id || '-' || review_text || '-' || review_title || '-' || product_id || '-' || product_name as id, * 
	from {{ source('skincare_products_raw', 'sephora_product_review') }}

{% endsnapshot %}