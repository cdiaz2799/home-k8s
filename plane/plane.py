import pulumi
from pulumi_kubernetes import apps, core

import modules.pvc as pvc
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
from plane.secrets import postgres_creds

# Deploy API
api_component = 'api'
api_label = {'component': api_component}
api_labels = {**app_label, **api_label}

api_deployment = apps.v1.Deployment(
    f'{app_name}-api-deployment',
    api_version='apps/v1',
    kind='Deployment',
    metadata=core.v1.ObjectMeta(
        labels=api_labels, name=app_name, namespace=namespace_name
    ),
    spec=apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=core.v1.LabelSelectorArgs(match_labels=api_labels),
        template=core.v1.PodTemplateSpecArgs(
            metadata=core.v1.ObjectMetaArgs(labels=api_labels),
            spec=core.v1.PodSpecArgs(
                containers=[
                    core.v1.ContainerArgs(
                        name=api_component,
                        image=f'makeplane/plane-backend:{app_version}',
                        restart_policy='Always',
                        command=['./bin/takeoff'],
                        env_from=core.v1.EnvFromSourceArgs(
                            config_map_ref=core.v1.ConfigMapEnvSourceArgs(
                                name=api_config_map.metadata['name']
                            )
                        ),
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


# Deploy Beat Worker
bw_component = 'beat-worker'
bw_label = {'component': bw_component}
bw_app_labels = {**app_label, **bw_label}

beat_worker_deployment = apps.v1.Deployment(
    f'{app_name}-beat-worker-deployment',
    api_version='apps/v1',
    kind='Deployment',
    metadata=core.v1.ObjectMeta(
        labels=bw_app_labels, name=app_name, namespace=namespace_name
    ),
    spec=apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=core.v1.LabelSelectorArgs(match_labels=bw_app_labels),
        template=core.v1.PodTemplateSpecArgs(
            metadata=core.v1.ObjectMetaArgs(labels=bw_app_labels),
            spec=core.v1.PodSpecArgs(
                containers=[
                    core.v1.ContainerArgs(
                        name=bw_component,
                        image=f'makeplane/plane-backend:{app_version}',
                        command=[
                            './bin/beat',
                        ],
                        env_from=core.v1.EnvFromSourceArgs(
                            config_map_ref=core.v1.ConfigMapEnvSourceArgs(
                                name=api_config_map.metadata['name']
                            )
                        ),
                        restart_policy='Always',
                    ),
                ],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(
        parent=namespace,
        delete_before_replace=True,
        depends_on=[api_deployment, db_deployment, redis_deployment],
    ),
)

# Deploy Worker
worker_component = 'worker'
worker_label = {'component': worker_component}
worker_labels = {**app_label, **worker_label}

worker_deployment = apps.v1.Deployment(
    f'{app_name}-worker-deployment',
    api_version='apps/v1',
    kind='Deployment',
    metadata=core.v1.ObjectMeta(
        labels=worker_labels, name=app_name, namespace=namespace_name
    ),
    spec=apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=core.v1.LabelSelectorArgs(match_labels=worker_labels),
        template=core.v1.PodTemplateSpecArgs(
            metadata=core.v1.ObjectMetaArgs(labels=worker_labels),
            spec=core.v1.PodSpecArgs(
                containers=[
                    core.v1.ContainerArgs(
                        name=worker_component,
                        restart_policy='Always',
                        image=f'makeplane/plane-backend:{app_version}',
                        command=[
                            './bin/worker',
                        ],
                        env_from=core.v1.EnvFromSourceArgs(
                            config_map_ref=core.v1.ConfigMapEnvSourceArgs(
                                name=api_config_map.metadata['name']
                            )
                        ),
                    ),
                ],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(
        parent=namespace,
        delete_before_replace=True,
        depends_on=[api_deployment, db_deployment, redis_deployment],
    ),
)
# Deploy Frontend
web_component = 'web'
web_label = {'component': web_component}
web_labels = {**app_label, **web_label}

web_deployment = (
    apps.v1.Deployment(
        f'{app_name}-web-deployment',
        api_version='apps/v1',
        kind='Deployment',
        metadata=core.v1.ObjectMeta(
            labels=web_labels, name=app_name, namespace=namespace_name
        ),
        spec=apps.v1.DeploymentSpecArgs(
            replicas=1,
            selector=core.v1.LabelSelectorArgs(match_labels=web_labels),
            template=core.v1.PodTemplateSpecArgs(
                metadata=core.v1.ObjectMetaArgs(labels=web_labels),
                spec=core.v1.PodSpecArgs(
                    containers=[
                        core.v1.ContainerArgs(
                            name=web_component,
                            image=f'makeplane/plane-frontend:{app_version}',
                            restart_policy='Always',
                            command=[
                                '/usr/local/bin/start.sh web/server.js web'
                            ],
                            env_from=core.v1.EnvFromSourceArgs(
                                config_map_ref=core.v1.ConfigMapEnvSourceArgs(
                                    name=web_config_map.metadata['name']
                                )
                            ),
                        ),
                    ],
                ),
            ),
        ),
        opts=pulumi.ResourceOptions(
            parent=namespace,
            delete_before_replace=True,
            depends_on=[api_deployment, worker_deployment],
        ),
    ),
)
# Deploy Space
space_component = 'space'
space_label = {'component': space_component}
space_labels = {**app_label, **space_label}

space_deployment = apps.v1.Deployment(
    f'{app_name}-space-deployment',
    api_version='apps/v1',
    kind='Deployment',
    metadata=core.v1.ObjectMeta(
        labels=space_labels, name=app_name, namespace=namespace_name
    ),
    spec=apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=core.v1.LabelSelectorArgs(match_labels=space_labels),
        template=core.v1.PodTemplateSpecArgs(
            metadata=core.v1.ObjectMetaArgs(labels=space_labels),
            spec=core.v1.PodSpecArgs(
                containers=[
                    core.v1.ContainerArgs(
                        name=space_component,
                        image=f'makeplane/plane-space:{app_version}',
                        restart_policy='Always',
                        command=[
                            '/usr/local/bin/start.sh space/server.js space'
                        ],
                        env_from=core.v1.EnvFromSourceArgs(
                            config_map_ref=core.v1.ConfigMapEnvSourceArgs(
                                name=space_config_map.metadata['name']
                            )
                        ),
                    ),
                ]
            ),
        ),
        opts=pulumi.ResourceOptions(
            parent=namespace,
            delete_before_replace=True,
            depends_on=[api_deployment, worker_deployment, web_deployment],
        ),
    ),
)
