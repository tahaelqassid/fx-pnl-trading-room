from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "you",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="fx_pnl_eod",
    default_args=default_args,
    schedule="0 18 * * *",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    tags=["fx-pnl"],
) as dag:

    load_data = BashOperator(
        task_id="load_trades_and_rates",
        bash_command="cd /opt/airflow/project && python ingestion/load_csv.py",
    )

    run_dbt = BashOperator(
        task_id="run_dbt_staging_and_marts",
        bash_command="cd /opt/airflow/fx_pnl_dbt && dbt run",
    )

    run_engine = BashOperator(
        task_id="run_fifo_wac_engine",
        bash_command="cd /opt/airflow/project && python engine/run_daily_pnl.py",
    )

    run_dbt_tests = BashOperator(
        task_id="run_dbt_tests",
        bash_command="cd /opt/airflow/fx_pnl_dbt && dbt test",
    )

    load_data >> run_dbt >> run_engine >> run_dbt_tests

    