import pulumi_random as random
from pulumi import ResourceOptions

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
smtp_host = config.require_secret('smtp-host')
smtp_user = config.require_secret('smtp-user')
smtp_password = config.require_secret('smtp-password')
smtp_port = config.require('smtp-port')
smtp_from = config.require_secret('smtp-from')
smtp_tls = config.get('smtp-tls', default='1')
smtp_ssl = config.get('smtp-ssl', default='0')

# Setup Secrets
secret_key = secrets.K8sSecret(
    f'{app_name}-secret-key',
    namespace=namespace_name,
    app_label=app_label,
    secrets={'secret_key': secret_key},
    opts=ResourceOptions(parent=plane_namespace, delete_before_replace=True),
)

# Setup Database Credentials
db_pw = random.RandomPassword(
    resource_name=f'{app_name}-db-pw',
    length=20,
    special=False,
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
        'PGHOST': 'db',
        'DATABASE_URL': db_pw.result.apply(
            lambda pw: f'postgresql://{db_user}:{pw}@db:5432/{db_name}'
        ),
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

smtp_creds = secrets.K8sSecret(
    'smtp-creds-secret',
    namespace=namespace_name,
    app_label=app_label,
    secrets={
        'EMAIL_HOST': smtp_host,
        'EMAIL_HOST_USER': smtp_user,
        'EMAIL_HOST_PASSWORD': smtp_password,
        'EMAIL_PORT': smtp_port,
        'EMAIL_FROM': smtp_from,
        'EMAIL_USE_TLS': smtp_tls,
        'EMAIL_USE_SSL': smtp_ssl,
    },
    opts=ResourceOptions(parent=plane_namespace, delete_before_replace=True),
)
