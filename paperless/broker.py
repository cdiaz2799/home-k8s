import pulumi
from pulumi_kubernetes import apps, core

import modules.pvc as pvc
from paperless.config import app_label, app_name, namespace, namespace_name

# Setup Vars
component_name = 'broker'
component_label = {'component': component_name}
tier_label = {'tier': 'backend'}
app_labels = {**app_label, **component_label, **tier_label}
volume_name = 'redis-data'

# Setup PVC
redis_pvc = pvc.K8sPVC(
    f'{app_name}-{component_name}-pvc',
    namespace=namespace_name,
    app_label=app_label,
    volume_size='5Gi',
    opts=pulumi.ResourceOptions(parent=namespace, delete_before_replace=True),
)

# Setup Deployment
broker_deployment = apps.v1.Deployment(
    f'{app_name}-{component_name}-deployment',
    metadata={
        'name': f'{app_name}-{component_name}',
        'namespace': namespace_name,
        'labels': app_labels,
    },
    spec={
        'selector': {'matchLabels': app_labels},
        'template': {
            'metadata': {'labels': app_labels},
            'spec': {
                'containers': [
                    {
                        'name': component_name,
                        'image': 'docker.io/library/redis:7',
                        'ports': [{'containerPort': 6379, 'name': 'redis'}],
                        'volumeMounts': [
                            {'mountPath': '/data', 'name': volume_name}
                        ],
                    }
                ],
                'volumes': [
                    {
                        'name': volume_name,
                        'persistentVolumeClaim': {
                            'claimName': redis_pvc.pvc.metadata['name']
                        },
                    }
                ],
            },
        },
    },
    opts=pulumi.ResourceOptions(parent=namespace, delete_before_replace=True),
)

broker_service = core.v1.Service(
    f'{app_name}-{component_name}-service',
    metadata={
        'name': component_name,
        'namespace': namespace_name,
        'labels': app_labels,
    },
    spec=core.v1.ServiceSpecArgs(
        selector=app_labels,
        ports=[
            core.v1.ServicePortArgs(
                protocol='TCP',
                port=6379,
                target_port=6379,
            )
        ],
    ),
    opts=pulumi.ResourceOptions(parent=namespace, delete_before_replace=True),
)
