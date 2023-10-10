import pulumi_kubernetes as k8s

import tandoor.config as config

service_account = k8s.core.v1.ServiceAccount(
    "tandoor-service-account",
    api_version="v1",
    kind="ServiceAccount",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="tandoor-service-account",
        namespace=config.tandoor_namespace.namespace.metadata["name"],
    ),
)
