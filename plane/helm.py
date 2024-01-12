import pulumi
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts
from pulumi_kubernetes.core.v1 import Namespace

# Setup Vars
config = pulumi.Config('plane')
chart_version = config.get('chart-version') or '1.0.7'
plane_version = config.get('plane-version') or 'latest'
fqdn = config.require('fqdn')

# Retrieve SMTP Vars
smtp_host = config.require('smtp-host')
smtp_from = config.require('smtp-from')
smtp_port = config.require_int('smtp-port')
smtp_username = config.require('smtp-user')
smtp_password = config.require('smtp-password')

# Setup Namespace
namespace = Namespace(
    'plane-namespace',
    metadata={
        'name': 'plane',
    },
)

# Setup Chart
plane_repo = ChartOpts(
    chart='plane-ce',
    version=chart_version,
    namespace=namespace.metadata.name,
    fetch_opts=FetchOpts(repo='https://helm.plane.so'),
    values={
        'planeVersion': plane_version,
        'ingress': {
            'appHost': fqdn,
            'ingressClass': 'nginx',
        },
        'smtp': {
            'host': smtp_host,
            'port': smtp_port,
            'user': smtp_username,
            'password': smtp_password,
            'from': smtp_from,
        },
    },
)

chart = Chart(
    release_name='plane',
    config=plane_repo,
    opts=pulumi.ResourceOptions(
        parent=namespace,
    ),
)
