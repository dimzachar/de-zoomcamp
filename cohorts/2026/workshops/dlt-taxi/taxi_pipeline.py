"""Pipeline to ingest NYC taxi data from the Data Engineering Zoomcamp API."""

import dlt
from dlt.sources.rest_api import rest_api_source


def taxi_source():
    """
    Create a dlt source for the NYC taxi data API.
    
    The API returns paginated JSON with 1,000 records per page.
    The API uses offset/limit pagination and cycles data after 1000 records.
    """
    return rest_api_source({
        "client": {
            "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net",
        },
        "resources": [
            {
                "name": "taxi_data",
                "endpoint": {
                    "path": "data_engineering_zoomcamp_api",
                    "paginator": {
                        "type": "page_number",
                        "page_param": "page",
                        "total_path": None,
                        "base_page": 1,
                    },
                },
                "write_disposition": "replace",
            },
        ],
    })


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="taxi_pipeline",
        destination="duckdb",
        dataset_name="nyc_taxi_data",
        progress="log",
    )

    load_info = pipeline.run(taxi_source())
    print(load_info)