#!/usr/bin/env python
# coding: utf-8

import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import pyarrow.parquet as pq
import os


@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--taxi-type', default='green', type=click.Choice(['green', 'yellow', 'fhv', 'fhvhv']), help='Taxi dataset type'
)
@click.option('--year', default=2025, type=int, help='Year of the data')
@click.option('--month', default=11, type=int, help='Month of the data')
@click.option('--target-table', default=None, help='Target table name')
@click.option('--batch-size', default=100000, type=int, help='Batch size for Parquet loading')


def run(pg_user, pg_pass, pg_host, pg_port, pg_db, taxi_type,year, month, target_table, batch_size):
    """Ingest NYC taxi Parquet data into PostgreSQL database."""

    prefix = "https://d37ci6vzurychx.cloudfront.net/trip-data"

    url = f"{prefix}/{taxi_type}_tripdata_{year}-{month:02d}.parquet"

    local_file = f"{taxi_type}_tripdata_{year}-{month:02d}.parquet"

    if target_table is None:
        target_table = f"{taxi_type}_taxi_data_{year}_{month:02d}"


    engine = create_engine(
        f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    )


    if not os.path.exists(local_file):
        print(f"Downloading {url}")
        pd.read_parquet(url).to_parquet(local_file)

    parquet_file = pq.ParquetFile(local_file)

    first = True

    for batch in tqdm(
        parquet_file.iter_batches(batch_size=batch_size),
        desc="Ingesting Parquet"
    ):
        df_chunk = batch.to_pandas()

        if first:
            df_chunk.head(0).to_sql(
                name=target_table,
                con=engine,
                if_exists="replace",
                index=False
            )
            first = False

        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="append",
            index=False
        )

    print("Ingestion completed successfully")


if __name__ == '__main__':
    run()
