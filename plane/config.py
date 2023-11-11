import pulumi
import pulumi_kubernetes as k8s

import modules.namespace as k8snamespace

# Import Config
config = pulumi.Config('plane')

# Setup Vars
app_name = 'plane'
app_label = {'app': f'{app_name}'}
app_version = config.get('plane-version', default='latest')
enable_openauth = config.get_int('enable-openauth', default=0)
fqdn = config.require('fqdn')
redis_host = 'redis'
redis_port = '6379'

# Setup Namespace
namespace = k8snamespace.K8Namespace(
    name=app_name,
)
namespace_name = namespace.namespace.metadata['name']


# Setup Config Maps
web_config_map = k8s.core.v1.ConfigMap(
    f'{app_name}-web-config-map',
    api_version='v1',
    kind='ConfigMap',
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name='web-config', namespace=namespace_name
    ),
    data={
        'NEXT_PUBLIC_ENABLE_OAUTH': '0',
        'NEXT_PUBLIC_DEPLOY_URL': f'{fqdn}/spaces',
    },
    opts=pulumi.ResourceOptions(parent=namespace, delete_before_replace=True),
)

space_config_map = k8s.core.v1.ConfigMap(
    f'{app_name}-spaces-config-map',
    api_version='v1',
    kind='ConfigMap',
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name='spaces-config', namespace=namespace_name
    ),
    data={
        'NEXT_PUBLIC_ENABLE_OAUTH': '0',
    },
    opts=pulumi.ResourceOptions(parent=namespace, delete_before_replace=True),
)

api_config_map = k8s.core.v1.ConfigMap(
    f'{app_name}-api-config-map',
    api_version='v1',
    kind='ConfigMap',
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name='api-config', namespace=namespace_name
    ),
    data={
        'DEBUG': '0',
        'DJANGO_SETTINGS_MODULE': 'plane.settings.selfhosted',
        'DOCKERIZED': '1',
        'NGINX_PORT': '80',
        'ENABLE_SIGNUP': '1',
        'WEB_URL': fqdn,
        'REDIS_HOST': redis_host,
        'REDIS_PORT': redis_port,
        'REDIS_URL': f'redis://{redis_host}:{redis_port}',
    },
    opts=pulumi.ResourceOptions(parent=namespace, delete_before_replace=True),
)
