import pulumi
from pulumi_kubernetes import apps, core

import modules.pvc as pvc
from plane.config import app_label, app_name, namespace, namespace_name
from plane.secrets import postgres_creds

# Setup Vars
component_name = 'db'
component_label = {'component': component_name}
tier_label = {'tier': 'backend'}
app_labels = {**app_label, **component_label, **tier_label}
volume_name = f'{app_name}-{component_name}-pvc'

db_pvc = pvc.K8sPVC(
    volume_name,
    namespace=namespace_name,
    app_label=app_label,
    volume_size='1Gi',
    opts=pulumi.ResourceOptions(parent=namespace, protect=True),
)

db_deployment = apps.v1.Deployment(
    f'{app_name}-{component_name}-deployment',
    metadata={
        'name': component_name,
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
                        'image': 'postgres:15.2-alpine',
                        'ports': [{'containerPort': 5432, 'name': 'postgres'}],
                        'envFrom': [
                            {
                                'secretRef': {
                                    'name': postgres_creds.secret.metadata[
                                        'name'
                                    ]
                                }
                            }
                        ],
                        'volumeMounts': [
                            {
                                'mountPath': '/var/lib/postgresql/data',
                                'name': volume_name,
                            }
                        ],
                    }
                ],
                'volumes': [
                    {
                        'name': volume_name,
                        'persistentVolumeClaim': {
                            'claimName': db_pvc.pvc.metadata['name']
                        },
                    }
                ],
            },
        },
    },
    opts=pulumi.ResourceOptions(parent=namespace, delete_before_replace=True),
)

db_service = core.v1.Service(
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
                name='postgres',
                port=5432,
                target_port=5432,
            )
        ],
    ),
    opts=pulumi.ResourceOptions(
        parent=db_deployment, delete_before_replace=True
    ),
)
