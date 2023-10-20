import pulumi_kubernetes as kubernetes

from mealie.config import (
    app_label,
    app_name,
    namespace_name,
    config,
    config_map,
)
from mealie.secrets import db_creds, smtp

# Setup Vars
app_version = config.get('mealie-version', default='v1.0.0-RC1.1')
component_name = app_name
component_label = {'component': component_name}
labels = {**app_label, **component_label}
volume_name = 'mealie-data'

# Setup Deployment
deployment = kubernetes.apps.v1.Deployment(
    f'{app_name}-deployment',
    api_version='apps/v1',
    kind='Deployment',
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name=app_name,
        namespace=namespace_name,
    ),
    spec=kubernetes.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels=labels,
        ),
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                labels=labels,
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                containers=[
                    kubernetes.core.v1.ContainerArgs(
                        name=component_name,
                        image=f'ghcr.io/mealie-recipes/mealie:{app_version}',
                        ports=[
                            kubernetes.core.v1.ContainerPortArgs(
                                container_port=9000,
                            )
                        ],
                        resources=kubernetes.core.v1.ResourceRequirementsArgs(
                            limits={
                                'memory': '1000Mi',
                            },
                        ),
                        volume_mounts=[
                            kubernetes.core.v1.VolumeMountArgs(
                                name=volume_name,
                                mount_path='/app/data',
                            ),
                        ],
                        env_from=[
                            kubernetes.core.v1.EnvFromSourceArgs(
                                secret_ref=kubernetes.core.v1.SecretEnvSourceArgs(
                                    name=db_creds.secret.metadata['name']
                                )
                            ),
                            kubernetes.core.v1.EnvFromSourceArgs(
                                config_map_ref=kubernetes.core.v1.ConfigMapEnvSourceArgs(
                                    name=config_map.metadata['name']
                                )
                            ),
                            kubernetes.core.v1.EnvFromSourceArgs(
                                secret_ref=kubernetes.core.v1.SecretEnvSourceArgs(
                                    name=smtp.secret.metadata['name']
                                )
                            ),
                        ],
                    )
                ],
                volumes=[
                    kubernetes.core.v1.VolumeArgs(
                        name=volume_name,
                        host_path=kubernetes.core.v1.HostPathVolumeSourceArgs(
                            path='/opt/mealie'
                        ),
                    )
                ],
            ),
        ),
    ),
)

service = kubernetes.core.v1.Service(
    f'{app_name}-service',
    api_version='v1',
    kind='Service',
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name=app_name,
        namespace=namespace_name,
    ),
    spec=kubernetes.core.v1.ServiceSpecArgs(
        selector=labels,
        ports=[
            kubernetes.core.v1.ServicePortArgs(
                protocol='TCP',
                name=app_name,
                port=9000,
                target_port=9000,
            )
        ],
        type='NodePort',
    ),
)
