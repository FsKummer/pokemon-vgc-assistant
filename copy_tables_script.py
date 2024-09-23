from google.cloud import bigquery
import os

# Environment Variables
PROJECT_ID = os.environ['PROJECT_ID']
BRONZE_DATASET_NAME = os.environ['BRONZE_DATA_SET_NAME']
GOLD_DATASET_NAME = os.environ['GOLD_DATA_SET_NAME']

# List of tables to copy
tables = ['pokemons', 'types', 'items', 'abilities', 'moves']

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)


def copy_table(table_name: str) -> None:
    """
    Function to copy a table from the Bronze dataset to the Gold dataset using SQL.
    """
    # SQL query to copy data from the Bronze dataset to the Gold dataset
    copy_query = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{GOLD_DATASET_NAME}.{table_name}` AS
    SELECT * FROM `{PROJECT_ID}.{BRONZE_DATASET_NAME}.{table_name}`;
    """

    print(f"Copying {table_name} from Bronze to Gold dataset...")

    # Execute the copy query
    query_job = client.query(copy_query)  # Make an API request.

    # Wait for the query to finish
    query_job.result()

    print(f"Successfully copied {table_name} to Gold dataset.")


def main():
    """
    Main function to copy all specified tables from the Bronze to Gold dataset.
    """
    for table in tables:
        copy_table(table)
    print("All tables have been successfully copied from Bronze to Gold dataset.")


if __name__ == '__main__':
    main()
