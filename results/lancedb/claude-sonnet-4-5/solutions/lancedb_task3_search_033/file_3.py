# Basic usage
results = search_with_prefilter(query_vector, "electronics", k=10)

# With complex conditions
results = table.search(query_vector)\
    .where("category = 'electronics' AND price < 500", prefilter=True)\
    .limit(10)\
    .to_pandas()