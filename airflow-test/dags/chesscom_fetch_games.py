import datetime
import airflow
from airflow.decorators import task, dag

default_args = {
    "owner": "airflow",
    "retries": 0,
    "retry_delay": datetime.timedelta(minutes=8)
}

    
@dag(
    dag_id="chesscom_fetch_games",
    default_args=default_args,
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval="0 12 * * *",
    max_active_runs=1,
    catchup=False,
    tags=["BE"]
)
def generate_dag():
    @task
    def print():
        print("aaaa")
generate_dag()
