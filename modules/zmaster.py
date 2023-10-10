import pulumi_kubernetes as kubernetes

recipes_nginx_config_config_map = kubernetes.core.v1.ConfigMap(
    "recipes_nginx_configConfigMap",
    kind="ConfigMap",
    api_version="v1",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        labels={
            "app": "recipes",
        },
        name="recipes-nginx-config",
    ),
    data={
        "nginx-config": """-
    events {
      worker_connections 1024;
    }
    http {
      include mime.types;
      server {
        listen 80;
        server_name _;

        client_max_body_size 16M;

        # serve static files
        location /static/ {
          alias /static/;
        }
        # serve media files
        location /media/ {
          alias /media/;
        }
      }
    }
""",
    },
)
recipes_secret = kubernetes.core.v1.Secret(
    "recipesSecret",
    kind="Secret",
    api_version="v1",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="recipes",
    ),
    type="Opaque",
    data={
        "postgresql-password": "ZGItcGFzc3dvcmQ=",
        "postgresql-postgres-password": "cG9zdGdyZXMtdXNlci1wYXNzd29yZA==",
        "secret-key": "ODVkYmUxNWQ3NWVmOTMwOGM3YWUwZjMzYzdhMzI0Y2M2ZjRiZjUxOWEyZWQyZjMwMjdiZDMzYzE0MGE0ZjlhYQ==",
    },
)
recipes_service_account = kubernetes.core.v1.ServiceAccount(
    "recipesServiceAccount",
    api_version="v1",
    kind="ServiceAccount",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="recipes",
    ),
)
recipes_media_persistent_volume_claim = kubernetes.core.v1.PersistentVolumeClaim(
    "recipes_mediaPersistentVolumeClaim",
    api_version="v1",
    kind="PersistentVolumeClaim",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="recipes-media",
        labels={
            "app": "recipes",
        },
    ),
    spec=kubernetes.core.v1.PersistentVolumeClaimSpecArgs(
        access_modes=["ReadWriteOnce"],
        resources=kubernetes.core.v1.ResourceRequirementsArgs(
            requests={
                "storage": "1Gi",
            },
        ),
    ),
)
recipes_static_persistent_volume_claim = kubernetes.core.v1.PersistentVolumeClaim(
    "recipes_staticPersistentVolumeClaim",
    api_version="v1",
    kind="PersistentVolumeClaim",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="recipes-static",
        labels={
            "app": "recipes",
        },
    ),
    spec=kubernetes.core.v1.PersistentVolumeClaimSpecArgs(
        access_modes=["ReadWriteOnce"],
        resources=kubernetes.core.v1.ResourceRequirementsArgs(
            requests={
                "storage": "1Gi",
            },
        ),
    ),
)
data_stateful_set = kubernetes.apps.v1.StatefulSet(
    "dataStatefulSet",
    api_version="apps/v1",
    kind="StatefulSet",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        labels={
            "app": "recipes",
            "tier": "database",
        },
        name="recipes-postgresql",
    ),
    spec=kubernetes.apps.v1.StatefulSetSpecArgs(
        replicas=1,
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels={
                "app": "recipes",
            },
        ),
        service_name="recipes-postgresql",
        update_strategy=kubernetes.apps.v1.StatefulSetUpdateStrategyArgs(
            type="RollingUpdate",
        ),
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                annotations={
                    "backup.velero.io/backup-volumes": "data",
                },
                labels={
                    "app": "recipes",
                    "tier": "database",
                },
                name="recipes-postgresql",
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                containers=[
                    kubernetes.core.v1.ContainerArgs(
                        name="recipes-db",
                        env=[
                            kubernetes.core.v1.EnvVarArgs(
                                name="BITNAMI_DEBUG",
                                value="false",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRESQL_PORT_NUMBER",
                                value="5432",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRESQL_VOLUME_DIR",
                                value="/bitnami/postgresql",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="PGDATA",
                                value="/bitnami/postgresql/data",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_USER",
                                value="recipes",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_PASSWORD",
                                value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=kubernetes.core.v1.SecretKeySelectorArgs(
                                        name="recipes",
                                        key="postgresql-password",
                                    ),
                                ),
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRESQL_POSTGRES_PASSWORD",
                                value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=kubernetes.core.v1.SecretKeySelectorArgs(
                                        name="recipes",
                                        key="postgresql-postgres-password",
                                    ),
                                ),
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_DB",
                                value="recipes",
                            ),
                        ],
                        image="docker.io/bitnami/postgresql:11.5.0-debian-9-r60",
                        image_pull_policy="IfNotPresent",
                        liveness_probe=kubernetes.core.v1.ProbeArgs(
                            exec_=kubernetes.core.v1.ExecActionArgs(
                                command=[
                                    "sh",
                                    "-c",
                                    'exec pg_isready -U "postgres" -d "wiki" -h 127.0.0.1 -p 5432',
                                ],
                            ),
                            failure_threshold=6,
                            initial_delay_seconds=30,
                            period_seconds=10,
                            success_threshold=1,
                            timeout_seconds=5,
                        ),
                        ports=[
                            kubernetes.core.v1.ContainerPortArgs(
                                container_port=5432,
                                name="postgresql",
                                protocol="TCP",
                            )
                        ],
                        readiness_probe=kubernetes.core.v1.ProbeArgs(
                            exec_=kubernetes.core.v1.ExecActionArgs(
                                command=[
                                    "sh",
                                    "-c",
                                    "-e",
                                    """pg_isready -U "postgres" -d "wiki" -h 127.0.0.1 -p 5432
              [ -f /opt/bitnami/postgresql/tmp/.initialized ]
""",
                                ],
                            ),
                            failure_threshold=6,
                            initial_delay_seconds=5,
                            period_seconds=10,
                            success_threshold=1,
                            timeout_seconds=5,
                        ),
                        resources=kubernetes.core.v1.ResourceRequirementsArgs(
                            requests={
                                "cpu": "250m",
                                "memory": "256Mi",
                            },
                        ),
                        security_context=kubernetes.core.v1.SecurityContextArgs(
                            run_as_user=1001,
                        ),
                        termination_message_path="/dev/termination-log",
                        termination_message_policy="File",
                        volume_mounts=[
                            kubernetes.core.v1.VolumeMountArgs(
                                mount_path="/bitnami/postgresql",
                                name="data",
                            )
                        ],
                    )
                ],
                dns_policy="ClusterFirst",
                init_containers=[
                    kubernetes.core.v1.ContainerArgs(
                        command=[
                            "sh",
                            "-c",
                            """mkdir -p /bitnami/postgresql/data
          chmod 700 /bitnami/postgresql/data
          find /bitnami/postgresql -mindepth 0 -maxdepth 1 -not -name ".snapshot" -not -name "lost+found" | \
            xargs chown -R 1001:1001
""",
                        ],
                        image="docker.io/bitnami/minideb:stretch",
                        image_pull_policy="Always",
                        name="init-chmod-data",
                        resources=kubernetes.core.v1.ResourceRequirementsArgs(
                            requests={
                                "cpu": "250m",
                                "memory": "256Mi",
                            },
                        ),
                        security_context=kubernetes.core.v1.SecurityContextArgs(
                            run_as_user=0,
                        ),
                        volume_mounts=[
                            kubernetes.core.v1.VolumeMountArgs(
                                mount_path="/bitnami/postgresql",
                                name="data",
                            )
                        ],
                    )
                ],
                restart_policy="Always",
                security_context=kubernetes.core.v1.PodSecurityContextArgs(
                    fs_group=1001,
                ),
                service_account="recipes",
                service_account_name="recipes",
                termination_grace_period_seconds=30,
            ),
        ),
        volume_claim_templates=[
            kubernetes.core.v1.PersistentVolumeClaimArgs(
                api_version="v1",
                kind="PersistentVolumeClaim",
                metadata=kubernetes.meta.v1.ObjectMetaArgs(
                    name="data",
                ),
                spec=kubernetes.core.v1.PersistentVolumeClaimSpecArgs(
                    access_modes=["ReadWriteOnce"],
                    resources=kubernetes.core.v1.ResourceRequirementsArgs(
                        requests={
                            "storage": "2Gi",
                        },
                    ),
                    volume_mode="Filesystem",
                ),
            )
        ],
    ),
)
recipes_postgresql_service = kubernetes.core.v1.Service(
    "recipes_postgresqlService",
    api_version="v1",
    kind="Service",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        labels={
            "app": "recipes",
            "tier": "database",
        },
        name="recipes-postgresql",
    ),
    spec=kubernetes.core.v1.ServiceSpecArgs(
        ports=[
            kubernetes.core.v1.ServicePortArgs(
                name="postgresql",
                port=5432,
                protocol="TCP",
                target_port="postgresql",
            )
        ],
        selector={
            "app": "recipes",
            "tier": "database",
        },
        session_affinity="None",
        type="ClusterIP",
    ),
)
recipes_deployment = kubernetes.apps.v1.Deployment(
    "recipesDeployment",
    api_version="apps/v1",
    kind="Deployment",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="recipes",
        labels={
            "app": "recipes",
            "environment": "production",
            "tier": "frontend",
        },
    ),
    spec=kubernetes.apps.v1.DeploymentSpecArgs(
        replicas=1,
        strategy=kubernetes.apps.v1.DeploymentStrategyArgs(
            type="Recreate",
        ),
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels={
                "app": "recipes",
                "environment": "production",
            },
        ),
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                annotations={
                    "backup.velero.io/backup-volumes": "media,static",
                },
                labels={
                    "app": "recipes",
                    "tier": "frontend",
                    "environment": "production",
                },
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                restart_policy="Always",
                service_account="recipes",
                service_account_name="recipes",
                init_containers=[
                    kubernetes.core.v1.ContainerArgs(
                        name="init-chmod-data",
                        env=[
                            kubernetes.core.v1.EnvVarArgs(
                                name="SECRET_KEY",
                                value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=kubernetes.core.v1.SecretKeySelectorArgs(
                                        name="recipes",
                                        key="secret-key",
                                    ),
                                ),
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="DB_ENGINE",
                                value="django.db.backends.postgresql_psycopg2",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_HOST",
                                value="recipes-postgresql",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_PORT",
                                value="5432",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_USER",
                                value="postgres",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_DB",
                                value="recipes",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_PASSWORD",
                                value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=kubernetes.core.v1.SecretKeySelectorArgs(
                                        name="recipes",
                                        key="postgresql-postgres-password",
                                    ),
                                ),
                            ),
                        ],
                        image="vabene1111/recipes",
                        image_pull_policy="Always",
                        resources=kubernetes.core.v1.ResourceRequirementsArgs(
                            requests={
                                "cpu": "250m",
                                "memory": "64Mi",
                            },
                        ),
                        command=[
                            "sh",
                            "-c",
                            """set -e
          source venv/bin/activate
          echo "Updating database"
          python manage.py migrate
          python manage.py collectstatic_js_reverse
          python manage.py collectstatic --noinput
          echo "Setting media file attributes"
          chown -R 65534:65534 /opt/recipes/mediafiles
          find /opt/recipes/mediafiles -type d | xargs -r chmod 755
          find /opt/recipes/mediafiles -type f | xargs -r chmod 644
          echo "Done"
""",
                        ],
                        security_context=kubernetes.core.v1.SecurityContextArgs(
                            run_as_user=0,
                        ),
                        volume_mounts=[
                            kubernetes.core.v1.VolumeMountArgs(
                                mount_path="/opt/recipes/mediafiles",
                                name="media",
                                sub_path="files",
                            ),
                            kubernetes.core.v1.VolumeMountArgs(
                                mount_path="/opt/recipes/staticfiles",
                                name="static",
                                sub_path="files",
                            ),
                        ],
                    )
                ],
                containers=[
                    kubernetes.core.v1.ContainerArgs(
                        name="recipes-nginx",
                        image="nginx:latest",
                        image_pull_policy="IfNotPresent",
                        ports=[
                            kubernetes.core.v1.ContainerPortArgs(
                                container_port=80,
                                protocol="TCP",
                                name="http",
                            ),
                            kubernetes.core.v1.ContainerPortArgs(
                                container_port=8080,
                                protocol="TCP",
                                name="gunicorn",
                            ),
                        ],
                        resources=kubernetes.core.v1.ResourceRequirementsArgs(
                            requests={
                                "cpu": "250m",
                                "memory": "64Mi",
                            },
                        ),
                        volume_mounts=[
                            kubernetes.core.v1.VolumeMountArgs(
                                mount_path="/media",
                                name="media",
                                sub_path="files",
                            ),
                            kubernetes.core.v1.VolumeMountArgs(
                                mount_path="/static",
                                name="static",
                                sub_path="files",
                            ),
                            kubernetes.core.v1.VolumeMountArgs(
                                name="nginx-config",
                                mount_path="/etc/nginx/nginx.conf",
                                sub_path="nginx-config",
                                read_only=True,
                            ),
                        ],
                    ),
                    kubernetes.core.v1.ContainerArgs(
                        name="recipes",
                        image="vabene1111/recipes",
                        image_pull_policy="IfNotPresent",
                        command=[
                            "/opt/recipes/venv/bin/gunicorn",
                            "-b",
                            ":8080",
                            "--access-logfile",
                            "-",
                            "--error-logfile",
                            "-",
                            "--log-level",
                            "INFO",
                            "recipes.wsgi",
                        ],
                        liveness_probe=kubernetes.core.v1.ProbeArgs(
                            failure_threshold=3,
                            http_get=kubernetes.core.v1.HTTPGetActionArgs(
                                path="/",
                                port=8080,
                                scheme="HTTP",
                            ),
                            period_seconds=30,
                        ),
                        readiness_probe=kubernetes.core.v1.ProbeArgs(
                            http_get=kubernetes.core.v1.HTTPGetActionArgs(
                                path="/",
                                port=8080,
                                scheme="HTTP",
                            ),
                            period_seconds=30,
                        ),
                        resources=kubernetes.core.v1.ResourceRequirementsArgs(
                            requests={
                                "cpu": "250m",
                                "memory": "64Mi",
                            },
                        ),
                        volume_mounts=[
                            kubernetes.core.v1.VolumeMountArgs(
                                mount_path="/opt/recipes/mediafiles",
                                name="media",
                                sub_path="files",
                            ),
                            kubernetes.core.v1.VolumeMountArgs(
                                mount_path="/opt/recipes/staticfiles",
                                name="static",
                                sub_path="files",
                            ),
                        ],
                        env=[
                            kubernetes.core.v1.EnvVarArgs(
                                name="DEBUG",
                                value="0",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="ALLOWED_HOSTS",
                                value="*",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="SECRET_KEY",
                                value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=kubernetes.core.v1.SecretKeySelectorArgs(
                                        name="recipes",
                                        key="secret-key",
                                    ),
                                ),
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="GUNICORN_MEDIA",
                                value="0",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="DB_ENGINE",
                                value="django.db.backends.postgresql_psycopg2",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_HOST",
                                value="recipes-postgresql",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_PORT",
                                value="5432",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_USER",
                                value="postgres",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_DB",
                                value="recipes",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_PASSWORD",
                                value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=kubernetes.core.v1.SecretKeySelectorArgs(
                                        name="recipes",
                                        key="postgresql-postgres-password",
                                    ),
                                ),
                            ),
                        ],
                        security_context=kubernetes.core.v1.SecurityContextArgs(
                            run_as_user=65534,
                        ),
                    ),
                ],
                volumes=[
                    kubernetes.core.v1.VolumeArgs(
                        name="media",
                        persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                            claim_name="recipes-media",
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="static",
                        persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                            claim_name="recipes-static",
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="nginx-config",
                        config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
                            name="recipes-nginx-config",
                        ),
                    ),
                ],
            ),
        ),
    ),
)
recipes_service = kubernetes.core.v1.Service(
    "recipesService",
    api_version="v1",
    kind="Service",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="recipes",
        labels={
            "app": "recipes",
            "tier": "frontend",
        },
    ),
    spec=kubernetes.core.v1.ServiceSpecArgs(
        selector={
            "app": "recipes",
            "tier": "frontend",
            "environment": "production",
        },
        ports=[
            kubernetes.core.v1.ServicePortArgs(
                port=80,
                target_port="http",
                name="http",
                protocol="TCP",
            ),
            kubernetes.core.v1.ServicePortArgs(
                port=8080,
                target_port="gunicorn",
                name="gunicorn",
                protocol="TCP",
            ),
        ],
    ),
)
