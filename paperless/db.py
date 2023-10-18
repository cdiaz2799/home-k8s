from pulumi_kubernetes import apps, core

import modules.pvc as pvc
from paperless.config import app_label, app_name, namespace_name
from paperless.secrets import db_creds as secret

# Setup Vars
namespace = namespace_name
component_name = 'db'
component_label = {'component': component_name}
tier_label = {'tier': 'backend'}
app_labels = {**app_label, **component_label, **tier_label}
volume_name = 'pg-data'

db_pvc = pvc.K8sPVC(
    f'{app_name}-{component_name}-pvc',
    namespace=namespace,
    app_label=app_label,
    volume_size='5Gi',
)

db_deployment = apps.v1.Deployment(
    f'{app_name}-{component_name}-deployment',
    metadata={
        'name': component_name,
        'namespace': namespace,
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
                        'image': 'docker.io/library/postgres:15',
                        'ports': [{'containerPort': 5432, 'name': 'postgres'}],
                        'envFrom': [
                            {
                                'secretRef': {
                                    'name': secret.secret.metadata['name']
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
)

db_service = core.v1.Service(
    f'{app_name}-{component_name}-service',
    metadata={
        'name': component_name,
        'namespace': namespace,
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
)
