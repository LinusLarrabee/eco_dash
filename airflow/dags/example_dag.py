from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def print_hello():
    print("Hello from Airflow!")

dag = DAG(
    'daily_hello_world',
    default_args=default_args,
    description='A simple daily DAG',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
)

run_this = PythonOperator(
    task_id='say_hello',
    python_callable=print_hello,
    dag=dag,
)

run_this
