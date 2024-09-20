from datetime import datetime
from google.cloud import storage
import os

def upload_file_to_lake(file_path: str, folder_name: str) -> None:
    storage_client = storage.Client()
    bucket_name = os.getenv("LAKE_BUCKET")
    bucket = storage_client.bucket(bucket_name)
    date_today = datetime.now()
    year = date_today.strftime("%Y")
    month = date_today.strftime("%m")
    day = date_today.strftime("%d")
    file_name = os.path.basename(file_path)
    blob_path = f"{folder_name}/{year}/{month}/{day}/{file_name}"
    blob = bucket.blob(blob_path)
    with open(file_path, 'rb') as file_obj:
        blob.upload_from_file(file_obj)
    print(f"File {file_name} uploaded to {blob_path}.")


def __main__():
    upload_file_to_lake(file_path='data/battle_info_2.csv', folder_name='battle_info')

if __name__ == "__main__":
    __main__()
