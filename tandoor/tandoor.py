import pulumi_kubernetes as kubernetes

import tandoor.config as config
import tandoor.config_map as config_map
import tandoor.db as db
import tandoor.iam as iam
import tandoor.pvc as pvc
import tandoor.secrets as secrets

# Setup Vars
name = "tandoor"
namespace = config.tandoor_namespace.namespace.metadata["name"]
app_label = config.app_label
env_label = config.env_label
tier_label = config.svc_tier_label
service_account = iam.service_account.metadata["name"]
secret_name = secrets.tandoor_secrets.secret.metadata["name"]

tandoor_version = config.tandoorConfig.get("tandoor-version", default="latest")
tandoor_image = f"vabene1111/recipes:{tandoor_version}"

# Setup Deployment
tandoor_deployment = kubernetes.apps.v1.Deployment(
    f"{name}-deployment",
    api_version="apps/v1",
    kind="Deployment",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name=name,
        namespace=namespace,
        labels={
            **app_label,
            **env_label,
            **tier_label,
        },
    ),
    spec=kubernetes.apps.v1.DeploymentSpecArgs(
        replicas=1,
        strategy=kubernetes.apps.v1.DeploymentStrategyArgs(
            type="Recreate",
        ),
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels={
                **app_label,
                **env_label,
            },
        ),
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                namespace=namespace,
                annotations={
                    "backup.velero.io/backup-volumes": "media,static",
                },
                labels={
                    **app_label,
                    **env_label,
                    **tier_label,
                },
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                restart_policy="Always",
                service_account=service_account,
                service_account_name=service_account,
                init_containers=[
                    kubernetes.core.v1.ContainerArgs(
                        name="init-chmod-data",
                        env=[
                            kubernetes.core.v1.EnvVarArgs(
                                name="SECRET_KEY",
                                value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=kubernetes.core.v1.SecretKeySelectorArgs(
                                        name=secret_name,
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
                                value=db.db_service_name,
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_PORT",
                                value="5432",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_USER",
                                value=db.db_username,
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_DB",
                                value=db.db_name,
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_PASSWORD",
                                value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=kubernetes.core.v1.SecretKeySelectorArgs(
                                        name=secret_name,
                                        key="postgresql-password",
                                    ),
                                ),
                            ),
                        ],
                        image=tandoor_image,
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
                        name=name,
                        image=tandoor_image,
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
                                        name=secret_name,
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
                                value=db.db_service_name,
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_PORT",
                                value="5432",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_USER",
                                value=db.db_username,
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_DB",
                                value=db.db_name,
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_PASSWORD",
                                value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=kubernetes.core.v1.SecretKeySelectorArgs(
                                        name=secret_name,
                                        key="postgresql-password",
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
                            claim_name=pvc.media_pvc.pvc.metadata["name"],
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="static",
                        persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                            claim_name=pvc.static_pvc.pvc.metadata["name"],
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="nginx-config",
                        config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
                            name=config_map.config_map.metadata["name"],
                        ),
                    ),
                ],
            ),
        ),
    ),
)

tandoor_service = kubernetes.core.v1.Service(
    f"{name}-service",
    api_version="v1",
    kind="Service",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name=name,
        namespace=namespace,
        labels={**app_label, **tier_label},
    ),
    spec=kubernetes.core.v1.ServiceSpecArgs(
        selector={
            **app_label,
            **tier_label,
            **env_label,
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
