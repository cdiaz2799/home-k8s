import pulumi
import pulumi_kubernetes as kubernetes

import actual_budget
import actual_budget.pvc as pvc

# Setup Vars
namespace = actual_budget.namespace.namespace.metadata['name']
app_name = actual_budget.app_name
app_label = actual_budget.app_label
app_port = actual_budget.config.get_int('app-port', default=5006)
pvc_name = pvc.actual_pvc.pvc.metadata['name']

deployment = kubernetes.apps.v1.Deployment(
    f'{app_name}-deployment',
    api_version='apps/v1',
    kind='Deployment',
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        labels=app_label,
        name=app_name,
        namespace=namespace,
    ),
    spec=kubernetes.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels=app_label,
        ),
        strategy=kubernetes.apps.v1.DeploymentStrategyArgs(
            type='Recreate',
        ),
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                labels=app_label,
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                containers=[
                    kubernetes.core.v1.ContainerArgs(
                        image=f'actualbudget/actual-server:{actual_budget.app_version}',
                        name=app_name,
                        ports=[
                            kubernetes.core.v1.ContainerPortArgs(
                                name='http',
                                container_port=5006,
                                host_port=app_port,
                                protocol='TCP',
                            )
                        ],
                        resources=kubernetes.core.v1.ResourceRequirementsArgs(),
                        env=[
                            kubernetes.core.v1.EnvVarArgs(
                                name='DEBUG',
                                value='actual:config',
                            )
                        ],
                        volume_mounts=[
                            kubernetes.core.v1.VolumeMountArgs(
                                mount_path='/data',
                                name='actual-data',
                            ),
                        ],
                    )
                ],
                restart_policy='Always',
                volumes=[
                    kubernetes.core.v1.VolumeArgs(
                        name='actual-data',
                        persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                            claim_name=pvc_name,
                        ),
                    )
                ],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(parent=actual_budget.namespace, delete_before_replace=True),
)
