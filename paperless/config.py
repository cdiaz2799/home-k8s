import pulumi
import pulumi_kubernetes as kubernetes

import modules.namespace as k8snamespace

# Setup Config
config = pulumi.Config('paperless')
global_config = pulumi.Config()

# Get the configuration values
app_name = 'paperless'
app_label = {'app': app_name}
app_url = config.require('paperless-fqdn')
tz = global_config.get('timezone')

# Setup Namespace
namespace = k8snamespace.K8Namespace(app_name)
namespace_name = namespace.namespace.metadata['name']

# Setup Config Map
paperless_config_map = kubernetes.core.v1.ConfigMap(
    f'{app_name}-config-map',
    kind='ConfigMap',
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name=f'{app_name}-config',
        namespace=namespace_name,
        labels=app_label,
    ),
    data={
        'PAPERLESS_URL': f'https://{app_url}',
        'PAPERLESS_FILENAME_FORMAT': '{created_year}/{correspondent}/{title}',
        'PAPERLESS_DATE_ORDER': 'MDY',
        'PAPERLESS_ENABLE_UPDATE_CHECK': 'true',
        'PAPERLESS_PORT': '8000',
        'PAPERLESS_TIME_ZONE': tz,
        'PAPERLESS_OCR_LANGUAGE': 'eng',
        'PAPERLESS_REDIS': 'redis://broker:6379',
    },
    opts=pulumi.ResourceOptions(parent=namespace, delete_before_replace=True),
)
