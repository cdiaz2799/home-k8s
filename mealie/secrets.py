from mealie.config import app_label, app_name, config, namespace_name
from modules import secrets

# Setup Vars
namespace = namespace_name
db_name = config.get('mealie-db-name', default='mealie')
db_user = config.get('mealie-db-user', default='mealie')
db_pw = config.require_secret('mealie-db-pw')
# Backend Configuration - Email
smtp_host = config.get('smtp-host', default='None')
smtp_port = config.get('smtp-port', default='587')
smtp_from_name = config.get('smtp-from-name', default='Mealie')
smtp_auth_strategy = config.get('smtp-auth-strategy', default='TLS')
smtp_from_email = config.get('smtp-from-email', default='None')
smtp_user = config.get('smtp-user', default='None')
smtp_password = config.get('smtp-password', default='None')

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

smtp = secrets.K8sSecret(
    f'{app_name}-smtp-creds',
    namespace=namespace_name,
    app_label=app_label,
    secrets={
        'SMTP_HOST': smtp_host,  # Required For email
        'SMTP_PORT': smtp_port,  # Required For email
        'SMTP_FROM_NAME': smtp_from_name,  # Required For email
        'SMTP_AUTH_STRATEGY': smtp_auth_strategy,  # Required For email, Options: 'TLS', 'SSL', 'NONE'
        'SMTP_FROM_EMAIL': smtp_from_email,  # Required For email
        'SMTP_USER': smtp_user,  # Required if SMTP_AUTH_STRATEGY is 'TLS' or 'SSL'
        'SMTP_PASSWORD': smtp_password,  # Required if SMTP_AUTH_STRATEGY is 'TLS' or 'SSL'
    },
)
