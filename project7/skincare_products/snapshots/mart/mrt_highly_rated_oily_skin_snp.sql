{% snapshot mrt_highly_rated_oily_skin_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='check',
          unique_key='product_name',
          check_cols=['product_name', 'average_rating', 'total_reviews'],
        )
    }}

    select * 
	from {{ ref('mrt_highly_rated_oily_skin') }}

{% endsnapshot %}