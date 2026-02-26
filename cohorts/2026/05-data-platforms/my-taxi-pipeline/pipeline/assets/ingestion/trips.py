"""@bruin
name: ingestion.trips
type: python
image: python:3.11
connection: duckdb-default

materialization:
  type: table
  strategy: append

columns:
  - name: pickup_datetime
    type: timestamp
    description: "When the meter was engaged"
  - name: dropoff_datetime
    type: timestamp
    description: "When the meter was disengaged"
@bruin"""

import os
import json
import pandas as pd

def materialize():
    start_date = os.environ["BRUIN_START_DATE"]
    end_date = os.environ["BRUIN_END_DATE"]
    taxi_types = json.loads(os.environ["BRUIN_VARS"]).get("taxi_types", ["yellow"])

    # Generate list of months between start and end dates
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    months = pd.date_range(start=start, end=end, freq='MS')
    
    dataframes = []
    
    for taxi_type in taxi_types:
        for month in months:
            year = month.year
            month_num = month.month
            url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year}-{month_num:02d}.parquet"
            
            try:
                df = pd.read_parquet(url)
                df['taxi_type'] = taxi_type
                dataframes.append(df)
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                continue
    
    if not dataframes:
        return pd.DataFrame()
    
    final_dataframe = pd.concat(dataframes, ignore_index=True)
    
    # Standardize column names
    column_mapping = {
        'tpep_pickup_datetime': 'pickup_datetime',
        'tpep_dropoff_datetime': 'dropoff_datetime',
        'lpep_pickup_datetime': 'pickup_datetime',
        'lpep_dropoff_datetime': 'dropoff_datetime',
        'PULocationID': 'pickup_location_id',
        'DOLocationID': 'dropoff_location_id',
    }
    
    final_dataframe = final_dataframe.rename(columns=column_mapping)
    
    # Select only needed columns
    required_columns = ['pickup_datetime', 'dropoff_datetime', 'pickup_location_id', 
                       'dropoff_location_id', 'fare_amount', 'payment_type', 'taxi_type']
    final_dataframe = final_dataframe[required_columns]
    
    # Convert datetime columns to strings to avoid PyArrow timezone database issues on Windows
    # The destination (DuckDB) will parse them back to timestamps
    for col in ['pickup_datetime', 'dropoff_datetime']:
        if col in final_dataframe.columns:
            final_dataframe[col] = final_dataframe[col].astype(str)
    
    return final_dataframe
