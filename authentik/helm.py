import pulumi
import pulumi_kubernetes.core.v1 as k8s
import pulumi_kubernetes.helm.v3 as helm
import pulumi_kubernetes.meta.v1 as meta
import pulumi_random as random

import modules.namespace as k8snamespace

# Setup Config
config = pulumi.Config('authentik')

# Setup Vars
secret_key = config.require_secret('secret-key')
ingress_domain = config.require('ingress-domain')
app_version = config.get('app-version', default='2023.10.2')

# Setup Namespace
namespace = k8snamespace.K8Namespace(
    name='authentik',
)

# Setup Authentik

## Setup Config Map
config_map = k8s.ConfigMap(
    'authentik-user-settings',
    metadata=meta.ObjectMetaArgs(
        name='user-settings',
        namespace=namespace.namespace.metadata['name'],
    ),
    data={
        'user_settings.py': f'CSRF_TRUSTED_ORIGINS = ["https://{ingress_domain}"]',
    },
)

## Generate Random Password for Database
db_pw = random.RandomPassword(
    'authentik-db-pw',
    length=16,
    special=True,
    override_special='_%@',
    opts=pulumi.ResourceOptions(parent=namespace),
)

## Deploy from Helm Chart
chart = helm.Chart(
    'authentik',
    helm.ChartOpts(
        chart='authentik',
        fetch_opts=helm.FetchOpts(
            repo=f'https://charts.goauthentik.io',
            version=app_version,
        ),
        namespace='authentik',
        values={
            'authentik': {
                'secret_key': secret_key,
                'error_reporting': {
                    'enabled': 'true',
                },
                'postgresql': {
                    'password': db_pw.result,
                },
            },
            'image': {
                'tag': app_version,
            },
            'ingress': {
                'annotation': {},
                'ingressClassName': 'nginx',
                'enabled': 'true',
                'hosts': [
                    {
                        'host': ingress_domain,
                        'paths': [{'path': '/', 'pathType': 'Prefix'}],
                    },
                ],
            },
            'postgresql': {
                'enabled': 'true',
                'postgresqlPassword': db_pw.result,
            },
            'redis': {
                'enabled': 'true',
            },
            'volumes': [
                {
                    'name': 'user-settings',
                    'configMap': {
                        'name': config_map.metadata['name'],
                    },
                },
            ],
            'volumeMounts': [
                {
                    'name': 'user-settings',
                    'mountPath': '/data',
                    'readOnly': True,
                }
            ],
        },
    ),
    opts=pulumi.ResourceOptions(parent=namespace),
)
