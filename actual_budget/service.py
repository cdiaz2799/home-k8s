import pulumi_kubernetes as kubernetes
from pulumi import ResourceOptions

import actual_budget
import actual_budget.pvc as pvc

# Setup Vars
namespace = actual_budget.namespace.namespace.metadata['name']
app_name = actual_budget.app_name
app_label = actual_budget.app_label
app_port = actual_budget.config.get_int('app-port', default=5006)
pvc_name = pvc.actual_pvc.pvc.metadata['name']

# Setup Service
service = kubernetes.core.v1.Service(
    f'{app_name}-service',
    api_version='v1',
    kind='Service',
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        labels=app_label,
        name=app_name,
        namespace=namespace,
    ),
    spec=kubernetes.core.v1.ServiceSpecArgs(
        ports=[
            kubernetes.core.v1.ServicePortArgs(
                name=app_name,
                port=app_port,
                target_port=5006,
            )
        ],
        selector=app_label,
    ),
    opts=ResourceOptions(parent=actual_budget.namespace, delete_before_replace=True),
)
