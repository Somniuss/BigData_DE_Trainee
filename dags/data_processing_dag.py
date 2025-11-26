from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from airflow.datasets import Dataset
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.sensors.python import PythonSensor
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule

DATA_DIR = Path("/opt/airflow/data")
RAW_DATA_PATH = DATA_DIR / "airflow_data.csv"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DATA_PATH = PROCESSED_DIR / "airflow_data_clean.csv"

PROCESSED_DATASET = Dataset(PROCESSED_DATA_PATH.as_uri())


def _file_available() -> bool:
    """Return True when the raw data file exists."""
    exists = RAW_DATA_PATH.exists()
    logging.info("Checking for %s -> %s", RAW_DATA_PATH, exists)
    return exists


def _choose_branch() -> str:
    """Route execution depending on whether the file contains any data."""
    if not RAW_DATA_PATH.exists():
        return "file_empty"

    if RAW_DATA_PATH.stat().st_size == 0:
        logging.info("Raw file exists but is empty.")
        return "file_empty"

    df = pd.read_csv(RAW_DATA_PATH)
    if df.dropna(how="all").empty:
        logging.info("Raw file contains only empty rows.")
        return "file_empty"

    logging.info("Raw file contains %s rows, continuing with processing.", len(df))
    return "transform_data.replace_nulls"


@task(task_id="replace_nulls")
def replace_nulls_task(source_path: str, destination_path: str) -> None:
    """Replace literal 'null' strings and NaNs with '-'."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(source_path)
    df = df.fillna("-")
    df = df.applymap(lambda value: "-" if str(value).strip().lower() == "null" else value)
    df.to_csv(destination_path, index=False)


@task(task_id="sort_by_date")
def sort_by_date_task(target_path: str) -> None:
    """Sort the dataset by created_date column."""
    df = pd.read_csv(target_path)
    df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
    df = df.sort_values("created_date").reset_index(drop=True)
    df["created_date"] = df["created_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv(target_path, index=False)


@task(task_id="clean_content", outlets=[PROCESSED_DATASET])
def clean_content_task(target_path: str) -> str:
    df = pd.read_csv(target_path)

    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002700-\U000027BF"
        "\U0001F900-\U0001F9FF"
        "]+",
        flags=re.UNICODE,
    )

    allowed_text = re.compile(r"[^0-9A-Za-zА-Яа-яёЁ\s\.,!?;:\-'\"]+")

    def clean(text):
        text = str(text)
        text = emoji_pattern.sub("", text)
        text = allowed_text.sub("", text)
        return text.strip()

    df["content"] = df["content"].fillna("-").map(clean)

    df.to_csv(target_path, index=False)
    return target_path



@dag(
    dag_id="airflow_data_processing",
    start_date=datetime(2023, 1, 1),
    schedule=None,
    catchup=False,
    tags=["data-processing", "datasets", "mongo"],
    default_args={
        "owner": "data-eng",
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
    },
)
def airflow_data_processing():
    wait_for_file = PythonSensor(
        task_id="wait_for_raw_file",
        python_callable=_file_available,
        poke_interval=30,
        timeout=60 * 60,
        mode="reschedule",
    )

    branch = BranchPythonOperator(
        task_id="route_based_on_file_state",
        python_callable=_choose_branch,
    )

    file_empty = BashOperator(
        task_id="file_empty",
        bash_command=(
            "mkdir -p /opt/airflow/logs/data_processing && "
            'echo "$(date) - airflow_data.csv is empty" '
            ">> /opt/airflow/logs/data_processing/empty_file.log"
        ),
    )

    with TaskGroup(group_id="transform_data") as transform_data:
        replace_nulls = replace_nulls_task(
            source_path=str(RAW_DATA_PATH),
            destination_path=str(PROCESSED_DATA_PATH),
        )
        sort_by_date = sort_by_date_task(target_path=str(PROCESSED_DATA_PATH))
        clean_content = clean_content_task(target_path=str(PROCESSED_DATA_PATH))

        replace_nulls >> sort_by_date >> clean_content

    pipeline_finished = EmptyOperator(
        task_id="pipeline_finished",
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    wait_for_file >> branch
    branch >> file_empty >> pipeline_finished
    branch >> transform_data >> pipeline_finished


airflow_data_processing()

