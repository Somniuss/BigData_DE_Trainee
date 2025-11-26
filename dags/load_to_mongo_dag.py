from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from airflow.datasets import Dataset
from airflow.decorators import dag, task
from airflow.providers.mongo.hooks.mongo import MongoHook

DATA_DIR = Path("/opt/airflow/data")
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "airflow_data_clean.csv"
PROCESSED_DATASET = Dataset(PROCESSED_DATA_PATH.as_uri())

MONGO_CONN_ID = "mongo_default"
MONGO_DB = "airflow"
MONGO_COLLECTION = "processed_comments"


@task(task_id="load_into_mongo")
def load_into_mongo_task(
    processed_path: str,
    mongo_conn_id: str,
    mongo_db: str,
    mongo_collection: str,
) -> int:
    """Insert the processed dataset into MongoDB."""
    if not Path(processed_path).exists():
        logging.warning("Processed dataset %s not found.", processed_path)
        return 0

    df = pd.read_csv(processed_path)
    if df.empty:
        logging.info("Processed dataset is empty - nothing to load.")
        return 0

    documents = df.to_dict(orient="records")
    hook = MongoHook(conn_id=mongo_conn_id)
    collection = hook.get_collection(mongo_db, mongo_collection)
    collection.delete_many({})
    result = collection.insert_many(documents)
    logging.info("Inserted %s documents into %s.%s", len(result.inserted_ids), mongo_db, mongo_collection)
    return len(result.inserted_ids)


@dag(
    dag_id="airflow_load_to_mongo",
    schedule=[PROCESSED_DATASET],
    catchup=False,
    start_date=datetime(2023, 1, 1),
    tags=["mongo", "datasets"],
)
def airflow_load_to_mongo():
    load_into_mongo_task(
        processed_path=str(PROCESSED_DATA_PATH),
        mongo_conn_id=MONGO_CONN_ID,
        mongo_db=MONGO_DB,
        mongo_collection=MONGO_COLLECTION,
    )


airflow_load_to_mongo()

