from pulumi_kubernetes import core, meta

from tandoor.config import app_label, tandoor_namespace, app_name

service_account = core.v1.ServiceAccount(
    f"{app_name}-service-account",
    api_version="v1",
    kind="ServiceAccount",
    metadata=meta.v1.ObjectMetaArgs(
        name=f"{app_name}-service-account",
        labels=app_label,
        namespace=tandoor_namespace.namespace.metadata["name"],
    ),
)
