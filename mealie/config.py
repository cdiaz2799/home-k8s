import pulumi
import pulumi_kubernetes as kubernetes

import modules.namespace as namespace_module

# Setup Config
config = pulumi.Config('mealie')
global_config = pulumi.Config()

# Setup Vars
app_name = 'mealie'
app_label = {'app': app_name}
app_url = config.require('mealie-fqdn')
tz = global_config.get('timezone')

# Setup Namespace
namespace = namespace_module.K8Namespace('mealie')
namespace_name = namespace.namespace.metadata['name']

# Retrieve values from Pulumi Config
default_group = config.get('default-group', default='Home')
default_email = config.get('default-email', default='changeme@example.com')
base_url = f'https://{app_url}'
token_time = config.get('token-time', default='48')
api_docs = config.get('api-docs', default='True')
allow_signup = config.get('allow-signup', default='true')
# Backend Configuration - Security
security_max_login_attempts = config.get(
    'security-max-login-attempts', default='5'
)
security_user_lockout_time = config.get(
    'security-user-lockout-time', default='24'
)
# Backend Configuration - Database
db_engine = config.get('db-engine', default='postgres')
postgres_server = config.get('postgres-server', default='db')
postgres_port = config.get('postgres-port', default='5432')
# Backend Configuration - Webworker
web_gunicorn = config.get('web-gunicorn', default='false')
workers_per_core = config.get('workers-per-core', default='1')
max_workers = config.get('max-workers', default='1')
web_concurrency = config.get('web-concurrency', default='1')

# Setup Config Map
config_map = kubernetes.core.v1.ConfigMap(
    f'{app_name}-config-map',
    api_version='v1',
    kind='ConfigMap',
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name=f'{app_name}-config',
        namespace=namespace_name,
    ),
    data={
        'DEFAULT_GROUP': default_group,  # The default group for users
        'DEFAULT_EMAIL': default_email,  # The default username for the superuser
        'BASE_URL': base_url,  # Used for Notifications
        'TOKEN_TIME': token_time,  # The time in hours that a login/auth token is valid
        'API_DOCS': api_docs,  # Turns on/off access to the API documentation locally.
        'TZ': tz,  # Must be set to get correct date/time on the server
        'ALLOW_SIGNUP': allow_signup,  # Allow user sign-up without token
        # Backend Configuration - Security
        'SECURITY_MAX_LOGIN_ATTEMPTS': security_max_login_attempts,  # Maximum times a user can provide an invalid password before their account is locked
        'SECURITY_USER_LOCKOUT_TIME': security_user_lockout_time,  # Time in hours for how long a user's account is locked
        # Backend Configuration - Database
        'DB_ENGINE': db_engine,  # 'sqlite' or 'postgres'
        'POSTGRES_SERVER': postgres_server,  # Postgres database server address
        'POSTGRES_PORT': postgres_port,  # Postgres database port
        # Backend Configuration - Webworker
        'WEB_GUNICORN': web_gunicorn,  # Enables Gunicorn to manage Uvicorn web for multiple workers
        'WORKERS_PER_CORE': workers_per_core,  # Set the number of workers to the number of CPU cores multiplied by this value (Value * CPUs).
        'MAX_WORKERS': max_workers,  # Set the maximum number of workers to use. Default is not set meaning unlimited.
        'WEB_CONCURRENCY': web_concurrency,  # Override the automatic definition of the number of workers.
    },
    opts=pulumi.ResourceOptions(parent=namespace, delete_before_replace=True),
)
