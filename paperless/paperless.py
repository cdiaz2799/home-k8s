import pulumi
import pulumi_kubernetes as k8s

import modules.pvc as pvc
import paperless.config as config
import paperless.secrets as secrets

# Setup Vars
paperless_config = config.config
namespace = config.namespace_name
app_name = config.app_name
app_label = config.app_label
component_name = 'paperless'
component_label = {'component': component_name}
tier_label = {'tier': 'frontend'}
app_labels = {**app_label, **component_label, **tier_label}
app_version = paperless_config.get('paperless-version', default='latest')
data_volume = f'{app_name}-data-pvc'
media_volume = f'{app_name}-media-pvc'

# Setup PVCs
data_pvc = pvc.K8sPVC(
    data_volume,
    namespace=namespace,
    app_label=app_label,
    volume_size='1Gi',
    opts=pulumi.ResourceOptions(parent=config.namespace),
)

media_pvc = pvc.K8sPVC(
    media_volume,
    namespace=namespace,
    app_label=app_label,
    volume_size='1Gi',
    opts=pulumi.ResourceOptions(parent=config.namespace),
)

# Setup Deployment
paperless_deployment = k8s.apps.v1.Deployment(
    f'{app_name}-deployment',
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name=component_name, namespace=namespace, labels=app_labels
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(match_labels=app_labels),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(labels=app_labels),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[
                    k8s.core.v1.ContainerArgs(
                        name=component_name,
                        image=f'ghcr.io/paperless-ngx/paperless-ngx:{app_version}',
                        ports=[
                            k8s.core.v1.ContainerPortArgs(container_port=8000)
                        ],
                        env_from=[
                            k8s.core.v1.EnvFromSourceArgs(
                                config_map_ref=k8s.core.v1.ConfigMapEnvSourceArgs(
                                    name=config.paperless_config_map.metadata[
                                        'name'
                                    ]
                                )
                            ),
                            k8s.core.v1.EnvFromSourceArgs(
                                secret_ref=k8s.core.v1.SecretEnvSourceArgs(
                                    name=secrets.paperless_secrets.secret.metadata[
                                        'name'
                                    ]
                                )
                            ),
                            k8s.core.v1.EnvFromSourceArgs(
                                secret_ref=k8s.core.v1.SecretEnvSourceArgs(
                                    name=secrets.paperless_db.secret.metadata[
                                        'name'
                                    ]
                                )
                            ),
                        ],
                        volume_mounts=[
                            k8s.core.v1.VolumeMountArgs(
                                name='paperless-data',
                                mount_path='/usr/src/paperless/data',
                            ),
                            k8s.core.v1.VolumeMountArgs(
                                name='paperless-media',
                                mount_path='/usr/src/paperless/media',
                            ),
                            k8s.core.v1.VolumeMountArgs(
                                name='export',
                                mount_path='/usr/src/paperless/export',
                            ),
                            k8s.core.v1.VolumeMountArgs(
                                name='consume',
                                mount_path='/usr/src/paperless/consume',
                            ),
                        ],
                    )
                ],
                volumes=[
                    k8s.core.v1.VolumeArgs(
                        name='paperless-data',
                        persistent_volume_claim=k8s.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                            claim_name=data_pvc.pvc.metadata['name'],
                        ),
                    ),
                    k8s.core.v1.VolumeArgs(
                        name='paperless-media',
                        persistent_volume_claim=k8s.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                            claim_name=media_pvc.pvc.metadata['name'],
                        ),
                    ),
                    k8s.core.v1.VolumeArgs(
                        name='export',
                        host_path=k8s.core.v1.HostPathVolumeSourceArgs(
                            path='/opt/paperless/export'
                        ),
                    ),
                    k8s.core.v1.VolumeArgs(
                        name='consume',
                        host_path=k8s.core.v1.HostPathVolumeSourceArgs(
                            path='/opt/paperless/consume'
                        ),
                    ),
                ],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(parent=config.namespace),
)

service = k8s.core.v1.Service(
    f'{app_name}-service',
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name=component_name,
        namespace=namespace,
        labels=app_labels,
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector=app_labels,
        ports=[
            k8s.core.v1.ServicePortArgs(
                name='http',
                port=8000,
                target_port=8000,
            )
        ],
    ),
    opts=pulumi.ResourceOptions(parent=paperless_deployment),
)
