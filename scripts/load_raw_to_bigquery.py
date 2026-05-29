from __future__ import annotations

import argparse
from pathlib import Path

from google.cloud import bigquery
from google.oauth2 import service_account


RAW_FILES = {
    "raw_customers": Path("raw_data/raw_customers_updated.csv"),
    "raw_orders": Path("raw_data/raw_orders_updated.csv"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load the raw CSV files required by the dbt project into BigQuery."
    )
    parser.add_argument("--project", required=True, help="GCP project id.")
    parser.add_argument("--keyfile", required=True, help="Service account JSON path.")
    parser.add_argument("--dataset", default="raw", help="BigQuery raw dataset name.")
    parser.add_argument("--location", default="US", help="BigQuery dataset location.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    credentials = service_account.Credentials.from_service_account_file(args.keyfile)
    client = bigquery.Client(project=args.project, credentials=credentials)

    dataset = bigquery.Dataset(f"{args.project}.{args.dataset}")
    dataset.location = args.location
    client.create_dataset(dataset, exists_ok=True)
    print(f"Dataset ready: {args.project}.{args.dataset}")

    for table_name, csv_path in RAW_FILES.items():
        table_id = f"{args.project}.{args.dataset}.{table_name}"
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )

        with csv_path.open("rb") as csv_file:
            job = client.load_table_from_file(csv_file, table_id, job_config=job_config)
        job.result()

        table = client.get_table(table_id)
        print(f"{table_id}: {table.num_rows} rows")


if __name__ == "__main__":
    main()
