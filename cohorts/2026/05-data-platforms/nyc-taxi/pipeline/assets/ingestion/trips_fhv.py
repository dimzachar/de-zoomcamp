"""@bruin
name: ingestion.trips_fhv
type: python
image: python:3.11
connection: duckdb-default

materialization:
  type: table
  strategy: create+replace
@bruin"""

import os
import json
import pandas as pd

def materialize():
    start_date = os.environ["BRUIN_START_DATE"]
    end_date = os.environ["BRUIN_END_DATE"]

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    months = pd.date_range(start=start, end=end, freq='MS')
    
    dataframes = []
    
    for month in months:
        year = month.year
        month_num = month.month
        url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_{year}-{month_num:02d}.parquet"
        
        try:
            df = pd.read_parquet(url, engine='fastparquet')
            
            # Convert datetime columns to strings
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
                    df[col] = df[col].astype(str).replace('nan', None)
            
            dataframes.append(df)
            print(f"Successfully loaded {len(df)} rows from {url}")
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            continue
    
    if not dataframes:
        return pd.DataFrame()
    
    return pd.concat(dataframes, ignore_index=True)
