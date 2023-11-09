import pulumi
import pulumi_kubernetes.helm.v3 as helm
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

# Deploy Authentik
db_pw = random.RandomPassword(
    'authentik-db-pw',
    length=16,
    special=True,
    override_special='_%@',
    opts=pulumi.ResourceOptions(parent=namespace),
)
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
        },
    ),
    opts=pulumi.ResourceOptions(parent=namespace),
)
