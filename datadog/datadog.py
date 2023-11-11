import pulumi
import pulumi_kubernetes.core.v1 as k8s
import pulumi_kubernetes.helm.v3 as helm
import pulumi_kubernetes.meta.v1 as meta
import pulumi_random as random

import modules.namespace as k8snamespace
import modules.secrets as secrets

# Set Config
config = pulumi.Config('datadog')

# Setup Vars
dd_site = config.get('site', default='us3.datadoghq.com')
api_key = config.require_secret('api-key')
app_key = config.require_secret('app-key')
app_label = {'app': 'datadog'}

# Setup Namespace
namespace = k8snamespace.K8Namespace(
    name='datadog',
)

# Setup Helm Chart
agent = helm.Chart(
    'datadog-chart',
    helm.ChartOpts(
        chart='datadog',
        fetch_opts=helm.FetchOpts(repo=f'https://helm.datadoghq.com'),
        namespace=namespace.namespace.metadata['name'],
        values={
            'datadog': {
                'apiKey': api_key,
                'appKey': app_key,
                'site': dd_site,
                'clusterName': 'cdiaz.cloud',
                'clusterChecks': {
                    'enabled': 'true',
                },
            },
            'processAgent': {
                'enabled': 'true',
                'processCollection': 'true',
            },
            'orchestratorExplorer': {
                'enabled': 'true',
            },
            'clusterAgent': {
                'enabled': 'true',
            },
        },
    ),
    opts=pulumi.ResourceOptions(
        parent=namespace,
    ),
)
