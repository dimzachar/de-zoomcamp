"""@bruin
name: ingestion.trips
type: python
image: python:3.11
connection: duckdb-default

materialization:
  type: table
  strategy: append
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
                # Use fastparquet and keep raw column names
                df = pd.read_parquet(url, engine='fastparquet')
                df['taxi_type'] = taxi_type
                
                # Convert ALL columns to native Python types to avoid PyArrow issues
                for col in df.columns:
                    if pd.api.types.is_datetime64_any_dtype(df[col]):
                        # Convert datetime to string
                        df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                    elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
                        # Convert to regular Python string
                        df[col] = df[col].astype(str).replace('nan', None)
                
                dataframes.append(df)
                print(f"Successfully loaded {len(df)} rows from {url}")
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                continue
    
    if not dataframes:
        return pd.DataFrame()
    
    # Concatenate all dataframes
    final_dataframe = pd.concat(dataframes, ignore_index=True)
    
    return final_dataframe
