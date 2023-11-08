import pulumi
from pulumi_kubernetes import apps, core

from mealie.config import app_label, app_name
from mealie.config import namespace as mealie_namespace
from mealie.config import namespace_name
from mealie.secrets import db_creds as secret
from modules import pvc

# Setup Vars
component_name = 'db'
component_label = {'component': component_name}
volume_name = 'mealie-db'
labels = {**app_label, **component_label}

# Setup PVC
db_pvc = pvc.K8sPVC(
    f'{app_name}-{component_name}-pvc',
    namespace=namespace_name,
    app_label=app_label,
    volume_size='1Gi',
    opts=pulumi.ResourceOptions(
        parent=mealie_namespace, delete_before_replace=True
    ),
)

# Setup Deployment
db_deployment = apps.v1.Deployment(
    f'{app_name}-{component_name}-deployment',
    metadata={
        'name': component_name,
        'namespace': namespace_name,
        'labels': labels,
    },
    spec={
        'selector': {'matchLabels': labels},
        'template': {
            'metadata': {'labels': labels},
            'spec': {
                'containers': [
                    {
                        'name': f'{app_name}-{component_name}',
                        'image': 'postgres:15',
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
    opts=pulumi.ResourceOptions(
        delete_before_replace=True, depends_on=db_pvc, parent=mealie_namespace
    ),
)

# Setup Service
db_service = core.v1.Service(
    f'{app_name}-{component_name}-service',
    metadata={
        'name': component_name,
        'namespace': namespace_name,
        'labels': labels,
    },
    spec=core.v1.ServiceSpecArgs(
        selector=labels,
        ports=[
            core.v1.ServicePortArgs(
                name='postgres',
                port=5432,
                target_port=5432,
            )
        ],
    ),
    opts=pulumi.ResourceOptions(
        delete_before_replace=True,
        depends_on=db_deployment,
        parent=mealie_namespace,
    ),
)
