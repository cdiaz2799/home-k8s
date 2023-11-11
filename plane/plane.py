import pulumi
from pulumi_kubernetes import apps, core, meta

from plane.config import (
    api_config_map,
    app_label,
    app_name,
    app_version,
    namespace,
    namespace_name,
    space_config_map,
    web_config_map,
)
from plane.db import db_deployment
from plane.redis import redis_deployment
from plane.secrets import (
    db_creds,
    default_creds,
    openai_secret,
    smtp_creds,
)

# Deploy API
api_component = 'api'
api_label = {'component': api_component}
api_labels = {**app_label, **api_label}
bw_component = 'beat-worker'
worker_component = 'worker'
space_component = 'space'

api_env = [
    core.v1.EnvFromSourceArgs(
        config_map_ref=core.v1.ConfigMapEnvSourceArgs(
            name=api_config_map.metadata['name']
        ),
    ),
    core.v1.EnvFromSourceArgs(
        secret_ref=core.v1.SecretEnvSourceArgs(
            name=db_creds.secret.metadata['name']
        )
    ),
    core.v1.EnvFromSourceArgs(
        secret_ref=core.v1.SecretEnvSourceArgs(
            name=smtp_creds.secret.metadata['name']
        )
    ),
    core.v1.EnvFromSourceArgs(
        secret_ref=core.v1.SecretEnvSourceArgs(
            name=openai_secret.secret.metadata['name']
        )
    ),
    core.v1.EnvFromSourceArgs(
        secret_ref=core.v1.SecretEnvSourceArgs(
            name=default_creds.secret.metadata['name']
        )
    ),
]

backend_deployment = apps.v1.Deployment(
    f'{app_name}-backend-deployment',
    api_version='apps/v1',
    kind='Deployment',
    metadata=meta.v1.ObjectMetaArgs(
        labels=api_labels, name=f'{app_name}-backend', namespace=namespace_name
    ),
    spec=apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=meta.v1.LabelSelectorArgs(match_labels=api_labels),
        template=core.v1.PodTemplateSpecArgs(
            metadata=meta.v1.ObjectMetaArgs(labels=api_labels),
            spec=core.v1.PodSpecArgs(
                containers=[
                    core.v1.ContainerArgs(
                        name=api_component,
                        image=f'makeplane/plane-backend:{app_version}',
                        image_pull_policy='IfNotPresent',
                        command=['./bin/takeoff'],
                        env_from=api_env,
                        ports=[
                            core.v1.ContainerPortArgs(
                                container_port=8000,
                                name='http',
                                protocol='TCP',
                            )
                        ],
                    ),
                    core.v1.ContainerArgs(
                        name=bw_component,
                        image=f'makeplane/plane-backend:{app_version}',
                        image_pull_policy='IfNotPresent',
                        command=[
                            './bin/beat',
                        ],
                        env_from=api_env,
                    ),
                    core.v1.ContainerArgs(
                        name=worker_component,
                        image=f'makeplane/plane-backend:{app_version}',
                        image_pull_policy='IfNotPresent',
                        command=[
                            './bin/worker',
                        ],
                        env_from=api_env,
                    ),
                    core.v1.ContainerArgs(
                        name=space_component,
                        image=f'makeplane/plane-space:{app_version}',
                        image_pull_policy='IfNotPresent',
                        command=[
                            '/usr/local/bin/start.sh',
                        ],
                        args=['space/server.js', 'space'],
                        env_from=[
                            core.v1.EnvFromSourceArgs(
                                config_map_ref=core.v1.ConfigMapEnvSourceArgs(
                                    name=space_config_map.metadata['name']
                                )
                            )
                        ],
                        ports=[
                            core.v1.ContainerPortArgs(
                                container_port=3000,
                                host_port=3001,
                                name='http',
                                protocol='TCP',
                            )
                        ],
                    ),
                ],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(
        parent=namespace,
        delete_before_replace=True,
        depends_on=[db_deployment, redis_deployment],
    ),
)

# Deploy Frontend
frontend_component = 'frontend'
frontend_label = {'component': frontend_component}
frontend_labels = {**app_label, **frontend_label}

frontend_deployment = apps.v1.Deployment(
    f'{app_name}-frontend-deployment',
    api_version='apps/v1',
    kind='Deployment',
    metadata=meta.v1.ObjectMetaArgs(
        labels=frontend_labels,
        name=f'{app_name}-frontend',
        namespace=namespace_name,
    ),
    spec=apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=meta.v1.LabelSelectorArgs(match_labels=frontend_labels),
        template=core.v1.PodTemplateSpecArgs(
            metadata=meta.v1.ObjectMetaArgs(labels=frontend_labels),
            spec=core.v1.PodSpecArgs(
                containers=[
                    core.v1.ContainerArgs(
                        name=frontend_component,
                        image=f'makeplane/plane-frontend:{app_version}',
                        image_pull_policy='IfNotPresent',
                        command=[
                            '/usr/local/bin/start.sh',
                        ],
                        args=['web/server.js', 'web'],
                        env_from=[
                            core.v1.EnvFromSourceArgs(
                                config_map_ref=core.v1.ConfigMapEnvSourceArgs(
                                    name=web_config_map.metadata['name']
                                )
                            )
                        ],
                        ports=[
                            core.v1.ContainerPortArgs(
                                container_port=3000,
                                name='http',
                                protocol='TCP',
                            )
                        ],
                    ),
                ],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(
        parent=namespace,
        delete_before_replace=True,
    ),
)


frontend_service = core.v1.Service(
    f'{app_name}-{frontend_component}-service',
    metadata=meta.v1.ObjectMetaArgs(
        name=app_name,
        labels=frontend_labels,
        namespace=namespace_name,
    ),
    spec=core.v1.ServiceSpecArgs(
        type='ClusterIP',
        selector=frontend_labels,
        ports=[
            core.v1.ServicePortArgs(
                name=app_name,
                port=3000,
                target_port=3000,
            )
        ],
    ),
    opts=pulumi.ResourceOptions(
        parent=frontend_deployment,
        delete_before_replace=True,
    ),
)

api_service = core.v1.Service(
    f'{app_name}-{api_component}-service',
    metadata=meta.v1.ObjectMetaArgs(
        name=f'{app_name}-api',
        labels=api_labels,
        namespace=namespace_name,
    ),
    spec=core.v1.ServiceSpecArgs(
        type='ClusterIP',
        selector=api_labels,
        ports=[
            core.v1.ServicePortArgs(
                name='http',
                port=8000,
                target_port=8000,
                protocol='TCP',
            )
        ],
    ),
    opts=pulumi.ResourceOptions(
        parent=backend_deployment,
        delete_before_replace=True,
    ),
)


spaces_service = core.v1.Service(
    f'{app_name}-{space_component}-service',
    metadata=meta.v1.ObjectMetaArgs(
        name=f'{app_name}-spaces',
        labels=api_labels,
        namespace=namespace_name,
    ),
    spec=core.v1.ServiceSpecArgs(
        type='ClusterIP',
        selector=api_labels,
        ports=[
            core.v1.ServicePortArgs(
                name='http',
                port=3001,
                target_port=3001,
                protocol='TCP',
            )
        ],
    ),
    opts=pulumi.ResourceOptions(
        parent=backend_deployment,
        delete_before_replace=True,
    ),
)
