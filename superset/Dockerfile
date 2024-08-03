FROM apache/superset:latest

COPY superset_config.py /app/pythonpath/superset_config.py

RUN pip install gunicorn google-auth google-auth-oauthlib google-api-python-client redis

CMD ["gunicorn", "-b", "0.0.0.0:8088", "superset.app:create_app()"]
