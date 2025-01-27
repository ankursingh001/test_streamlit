from io import StringIO
from pandas import json_normalize

from elasticsearch import Elasticsearch
import pandas as pd

client = Elasticsearch(
      "http://localhost:9200"
)


def get_data_frame_from_es(index):
    # Example query to retrieve documents
    response = client.search(
        index=index,  # Replace with the name of your index
        body={
            "query": {
                "match_all": {}  # Modify the query as needed
            }
        }
    )

    hits = response['hits']['hits']
    # Extract source data to a pandas DataFrame
    data = [hit['_source'] for hit in hits]
    return json_normalize(data)

# print(get_data_frame_from_es("search_query_meta"))