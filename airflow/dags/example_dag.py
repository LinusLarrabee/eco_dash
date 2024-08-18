from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# 定义 DAG 参数
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 创建 DAG 实例
dag = DAG(
    'example_dag',
    default_args=default_args,
    description='An example DAG for scheduling',
    schedule_interval=timedelta(days=1),  # 定时任务的执行间隔
    start_date=days_ago(1),  # 定义任务开始的时间
    catchup=False,  # 设置为 False 以防止捕获和执行历史任务
)

# 定义任务
start_task = DummyOperator(task_id='start_task', dag=dag)

# 可以定义更多任务并设置任务依赖
end_task = DummyOperator(task_id='end_task', dag=dag)

# 设置任务依赖关系
start_task >> end_task
