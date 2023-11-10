from pulumi import ResourceOptions
from pulumi_random import RandomPassword

from modules import secrets
from plane.config import app_label, app_name, config
from plane.config import namespace as plane_namespace
from plane.config import namespace_name

# Setup Vars
secret_key = config.require_secret('secret-key')
db_user = config.get('db-user', default='plane')
db_name = config.get('db-name', default='plane')
openai_key = config.get_secret('openai-key')
gpt_engine = config.get('gpt-engine', default='gpt-3.5-turbo')
default_email = config.require_secret('default-email')
default_password = config.require_secret('default-password')

# Setup Secrets
secret_key = secrets.K8sSecret(
    f'{app_name}-secret-key',
    namespace=namespace_name,
    app_label=app_label,
    secrets={'secret_key': secret_key},
    opts=ResourceOptions(parent=plane_namespace, delete_before_replace=True),
)

# Setup Database Credentials
db_pw = RandomPassword(
    'plane-db-pw',
    length=20,
    special=True,
    opts=ResourceOptions(parent=plane_namespace),
)

postgres_creds = secrets.K8sSecret(
    f'{app_name}-postgres-creds',
    namespace=namespace_name,
    app_label=app_label,
    secrets={
        'POSTGRES_USER': db_user,
        'POSTGRES_PASSWORD': db_pw.result,
        'POSTGRES_DB': db_name,
    },
    opts=ResourceOptions(parent=plane_namespace, delete_before_replace=True),
)

db_creds = secrets.K8sSecret(
    f'{app_name}-db-creds',
    namespace=namespace_name,
    app_label=app_label,
    secrets={
        'PGUSER': db_user,
        'PGPASSWORD': db_pw.result,
        'PGDATABASE': db_name,
        'PGHOST': 'plane-db',
        'DATABASE_URL': f'postgresql://{db_user}:{db_pw.result}@plane-db/{db_name}',
    },
    opts=ResourceOptions(parent=plane_namespace, delete_before_replace=True),
)

openai_secret = secrets.K8sSecret(
    f'{app_name}-openai-secret',
    namespace=namespace_name,
    app_label=app_label,
    secrets={
        'OPENAI_API_KEY': openai_key,
        'GPT_ENGINE': gpt_engine,
    },
    opts=ResourceOptions(parent=plane_namespace, delete_before_replace=True),
)

default_creds = secrets.K8sSecret(
    f'{app_name}-default-creds',
    namespace=namespace_name,
    app_label=app_label,
    secrets={
        'DEFAULT_EMAIL': default_email,
        'DEFAULT_PASSWORD': default_password,
    },
    opts=ResourceOptions(parent=plane_namespace, delete_before_replace=True),
)
