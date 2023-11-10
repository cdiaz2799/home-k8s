import pulumi
from pulumi_kubernetes import apps, core

import modules.pvc as pvc
from plane.config import app_label, app_name, namespace, namespace_name

# Setup Vars
component_name = 'redis'
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
redis_deployment = apps.v1.Deployment(
    f'{app_name}-{component_name}-deployment',
    metadata={
        'name': f'{app_name}-{component_name}',
        'namespace': namespace_name,
        'labels': app_labels,
    },
    spec=apps.v1.DeploymentSpecArgs(
        selector=core.v1.LabelSelectorArgs(match_labels=app_labels),
        replicas=1,
        template=core.v1.PodTemplateSpecArgs(
            metadata=core.v1.ObjectMetaArgs(labels=app_labels),
            spec=core.v1.PodSpecArgs(
                containers=core.v1.ContainerArgs(
                    name=component_name,
                    image='redis:6.2.7-alpine',
                    ports=core.v1.ContainerPortArgs(
                        container_port=6379, name='redis'
                    ),
                    volume_mounts=[
                        core.v1.VolumeMountArgs(
                            mount_path='/data',
                            name=volume_name,
                        ),
                    ],
                ),
                volumes=core.v1.VolumeArgs(
                    name=volume_name,
                    persistent_volume_claim=core.v1.PersistentVolumeClaimVolumeSourceArgs(
                        claim_name=redis_pvc.pvc.metadata['name'],
                    ),
                ),
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(parent=namespace, delete_before_replace=True),
)

redis_service = core.v1.Service(
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
