# Anomalies

## 1
### Description
Data collection must be made up of multiple independent data sources. You need at least 4 data sources.

### Applicable Skincare Products Data 
Sephora Skincare Products, Cosmetic Ingredients, Skin Disease Pictures, and Disease Database

### Explanation
Each of these 4 are independent data sets that we used to populate our data warehouse


## 2
### Description
Data collection must be composed of at least one source whose type is unstructured. This can be text, pdf, or images.

### Applicable Skincare Products Data 
Dermatologic diseases PDFs and skin disease pictures

### Explanation
We have sources that supply PDFs and images. PDFs and Images are considered unstructured data.


## 3
### Description
Data collection must be composed of multiple logical entities.

### Applicable Skincare Products Data
Skin_disease_pictures, reviews, ingredients, dermatologic_diseases, skin_disease_pictures, prices, variations, highlights, stock_status, variation_stats, products, categories, product_ingredients, brands

### Explanation
Each dataset contributes at least one logical entity to the dataset. Sephora skincare products dataset in particular contributes to 8 logical entities alone (excluding junctions)


## 4
### Description
Functional dependencies should hold across all tables such that the values of all records are Consistent.

### Applicable Skincare Products Data
The products, brands, reviews, (and other product related entities) are all consistent.
Product Ingredients names should be consistent with cosmetic ingredient names listed on the EU cosmetic ingredients database. 
Disease names are also consistent across the images/disease database. 

### Explanation
All the dependencies across tables should be consistent, but since we are unable to manually verify the values of each ingredient and disease name, there might be slight variations in the naming and diseases from the disease database and disease pictures.


## 5
### Description
There exists a field in any table whose assigned data type does not best fit its domain of values.

### Applicable Skincare Products Data
cosmetic_ingrdient.update_date is stored as a string instead of date.
sephora_product_review.is_recommended is a float instead of boolean
sephora_product_review.submission_time is a string instead of a date
sephora_product.new is an integer instead of a boolean
sephora_product.limited_edition is an integer instead of a boolean
sephora_product.online_only is an integer instead of a boolean
sephora_product.out_of_stock is an integer instead of a boolean
sephora_product.sephora_exclusive is an integer instead of a boolean

### Explanation
The fields listed above are assigned data types that aren’t best suited for their representation.


## 6
### Description
There exists a field in any table whose null values are represented as empty strings, "\n" or
something similar.

### Applicable Skincare Products Data
cosmetic_ingredient.ingredient_common_name use empty strings for null values
cosmetic_ingredient.european_pharmacopoeia_name use empty strings for null values
cosmetic_ingredient.restriction use empty strings for null values
cosmetic_ingredient.function use empty strings for null values

### Explanation
The fields above use empty strings to represent null values.


## 7
### Description
There exists a field in any table that stores the values of multiple attributes in a single cell. The
values represent different attributes.

### Applicable Skincare Products Data
sephora_product.product_name includes information about product name, brand, and ingredients, treatments

### Explanation
The field above includes at least 2 of the listed attributes for each product name.


## 8
### Description
There exists a field that stores multiple values in the same cell. The values represent a list of
elements for the same attribute.

### Applicable Skincare Products Data
sephora_product.ingredients stores a list of cosmetic ingredients in the same cell
sephora_product.highlights stores a list of product highlights in the same cell

### Explanation
The fields above stores multiple string values in the same cell in the form of a list


## 9
### Description
There exists two tables in your collection which originated from different sources and which have similar data. Moreover, the tables in question use two different identifier systems to refer to the same entity.

### Applicable Skincare Products Data
sephora_products identify products with their product_name
sephora_products_reviews identify products with their product_id. 

### Explanation
product_name is the name of the product while product_id is a unique number that identifies the product


## 10
### Description
There exists a table that models more than one logical entity. This can lead to storing repeated
values within the same table.

### Applicable Skincare Products Data
cosmetic_ingredients have fields like ingredient_unique_name and ingredient_common_name which have the same repeated values.

### Explanation
The common and unique names of ingredients are the same in the dataset.