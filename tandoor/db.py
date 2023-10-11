import pulumi_kubernetes as kubernetes

import tandoor.config as config
import tandoor.iam as iam
import tandoor.secrets as secrets

# Setup Vars
name = f"{config.app_name}-db"
namespace = config.tandoor_namespace.namespace.metadata["name"]
db_service_name = name
app_label = config.app_label
tier_label = config.db_tier_label
db_name = config.db_name
db_username = config.db_username
secret_name = secrets.tandoor_secrets.secret.metadata["name"]
service_account = iam.service_account.metadata["name"]

# Setup Stateful Set
db_sts = kubernetes.apps.v1.StatefulSet(
    "tandoor-db-statefulset",
    api_version="apps/v1",
    kind="StatefulSet",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        labels={**app_label, **tier_label},
        namespace=namespace,
        name=name,
    ),
    spec=kubernetes.apps.v1.StatefulSetSpecArgs(
        replicas=1,
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels=app_label,
        ),
        service_name=db_service_name,
        update_strategy=kubernetes.apps.v1.StatefulSetUpdateStrategyArgs(
            type="RollingUpdate",
        ),
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                annotations={
                    "backup.velero.io/backup-volumes": "data",
                },
                labels={**app_label, **tier_label},
                name=name,
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                containers=[
                    kubernetes.core.v1.ContainerArgs(
                        name=name,
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
                                value=db_username,
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
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRESQL_POSTGRES_PASSWORD",
                                value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=kubernetes.core.v1.SecretKeySelectorArgs(
                                        name=secret_name,
                                        key="postgresql-password",
                                    ),
                                ),
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="POSTGRES_DB",
                                value=db_name,
                            ),
                        ],
                        image="docker.io/bitnami/postgresql:15",
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
                service_account=service_account,
                service_account_name=service_account,
                termination_grace_period_seconds=30,
            ),
        ),
        volume_claim_templates=[
            kubernetes.core.v1.PersistentVolumeClaimArgs(
                api_version="v1",
                kind="PersistentVolumeClaim",
                metadata=kubernetes.meta.v1.ObjectMetaArgs(
                    name="data",
                    namespace=namespace,
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

db_service = kubernetes.core.v1.Service(
    "tandoor-db-service",
    api_version="v1",
    kind="Service",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        labels={**app_label, **tier_label},
        namespace=namespace,
        name=db_service_name,
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
        selector={**app_label, **tier_label},
        session_affinity="None",
        type="ClusterIP",
    ),
)
