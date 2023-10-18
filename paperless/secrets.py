import pulumi
import pulumi_kubernetes

import modules.secrets as secrets
from paperless.config import app_label, app_name, config, namespace_name

# Setup Vars
namespace = namespace_name
db_name = config.get('paperless-db-name', default='paperless')
db_user = config.get('paperless-db-user', default='paperless')
db_pw = config.require_secret('paperless-db-pw')
secret_key = config.require_secret('paperless-secret-key')
paperless_user = config.require('paperless-admin-user')
paperless_mail = config.require('paperless-admin-email')
paperless_pw = config.require_secret('paperless-admin-password')

# Setup Secrets

db_creds = secrets.K8sSecret(
    f'{app_name}-db-creds',
    namespace=namespace_name,
    app_label=app_label,
    secrets={
        'POSTGRES_DB': db_name,
        'POSTGRES_USER': db_user,
        'POSTGRES_PASSWORD': db_pw,
    },
)

paperless_db = secrets.K8sSecret(
    f'{app_name}-db-config',
    namespace=namespace_name,
    app_label=app_label,
    secrets={
        'PAPERLESS_DBENGINE': 'postgresql',
        'PAPERLESS_DBHOST': 'db',
        'PAPERLESS_DBPORT': '5432',
        'PAPERLESS_DBNAME': db_name,
        'PAPERLESS_DBUSER': db_user,
        'PAPERLESS_DBPASS': db_pw,
    },
)

paperless_secrets = secrets.K8sSecret(
    f'{app_name}-secrets',
    namespace=namespace_name,
    app_label=app_label,
    secrets={
        'PAPERLESS_SECRET_KEY': secret_key,
        'PAPERLESS_ADMIN_USER': paperless_user,
        'PAPERLESS_ADMIN_MAIL': paperless_mail,
        'PAPERLESS_ADMIN_PASSWORD': paperless_pw,
    },
)
