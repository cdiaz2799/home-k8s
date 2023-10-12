import pulumi
import pulumi_kubernetes as kubernetes
import actual_budget
import actual_budget.service as service

# Setup Vars
app_name = actual_budget.app_name
namespace = actual_budget.namespace.namespace.metadata["name"]
hostname = actual_budget.config.require("actual-hostname")

# Setup Ingress
ingress = kubernetes.networking.v1.Ingress(
    f"{app_name}-ingress",
    api_version="networking.k8s.io/v1",
    kind="Ingress",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        namespace=namespace,
    ),
    spec=kubernetes.networking.v1.IngressSpecArgs(
        ingress_class_name="nginx",
        rules=[
            kubernetes.networking.v1.IngressRuleArgs(
                host=hostname,
                http=kubernetes.networking.v1.HTTPIngressRuleValueArgs(
                    paths=[
                        kubernetes.networking.v1.HTTPIngressPathArgs(
                            path_type="Prefix",
                            path="/",
                            backend=kubernetes.networking.v1.IngressBackendArgs(
                                service=kubernetes.networking.v1.IngressServiceBackendArgs(
                                    name=service.service.metadata["name"],
                                    port=kubernetes.networking.v1.ServiceBackendPortArgs(
                                        number=service.app_port,
                                    ),
                                )
                            ),
                        )
                    ],
                ),
            )
        ],
    ),
)
