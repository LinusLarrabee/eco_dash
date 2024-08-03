import os

SECRET_KEY = os.getenv('SECRET_KEY', 'CSJdw81i2E1nGchC35GAinwqKBSTBrqUaelSPeQcCzLX0aWTRRC5Y86k')

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://superset:superset@postgres/superset'

# Redis configuration for rate limiting
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Flask-Limiter configuration
RATELIMIT_STORAGE_URI = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'