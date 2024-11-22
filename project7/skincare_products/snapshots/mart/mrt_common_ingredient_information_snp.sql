{% snapshot mrt_common_ingredient_information_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='check',
          unique_key='ingredient_name',
          check_cols=['ingredient_name', 'treated_diseases', 'intended_use', 'regulatory_restriction', 'product_count', 'brand_count'],
        )
    }}

    select * 
	from {{ ref('mrt_common_ingredient_information') }}

{% endsnapshot %}