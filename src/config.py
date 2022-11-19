import os


def get_postgres_uri():
    host = os.environ.get('DB_HOST', 'localhost')
    port = 5432 if host == 'localhost' else 54321
    # password = os.environ.get('DB_PASSWORD', '')
    user, db_name = 'postgres', 'postgres'
    return f'postgresql://{user}@{host}:{port}/{db_name}'

def get_api_url():
    return 'mya_api_ip'