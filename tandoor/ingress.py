import pulumi_kubernetes as kubernetes

import tandoor.config as config
import tandoor.tandoor as tandoor

# Setup Vars
name = config.app_name
namespace = config.tandoor_namespace.namespace.metadata["name"]
ingress_host = config.tandoorConfig.require("ingress-host")

# Setup Ingress
tandoor_ingress = kubernetes.networking.v1.Ingress(
    f"{name}-ingress",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name=name,
        namespace=namespace,
        annotations={"kubernetes.io/ingress.class": "nginx"},
    ),
    spec=kubernetes.networking.v1.IngressSpecArgs(
        ingress_class_name="nginx",
        rules=[
            kubernetes.networking.v1.IngressRuleArgs(
                host=ingress_host,
                http=kubernetes.networking.v1.HTTPIngressRuleValueArgs(
                    paths=[
                        kubernetes.networking.v1.HTTPIngressPathArgs(
                            backend=kubernetes.networking.v1.IngressBackendArgs(
                                service=kubernetes.networking.v1.IngressServiceBackendArgs(
                                    name=tandoor.tandoor_service.metadata["name"],
                                    port=kubernetes.networking.v1.ServiceBackendPortArgs(
                                        number=8080,
                                    ),
                                ),
                            ),
                            path="/",
                            path_type="Prefix",
                        ),
                        kubernetes.networking.v1.HTTPIngressPathArgs(
                            backend=kubernetes.networking.v1.IngressBackendArgs(
                                service=kubernetes.networking.v1.IngressServiceBackendArgs(
                                    name=tandoor.tandoor_service.metadata["name"],
                                    port=kubernetes.networking.v1.ServiceBackendPortArgs(
                                        number=80,
                                    ),
                                ),
                            ),
                            path="/media",
                            path_type="Prefix",
                        ),
                        kubernetes.networking.v1.HTTPIngressPathArgs(
                            backend=kubernetes.networking.v1.IngressBackendArgs(
                                service=kubernetes.networking.v1.IngressServiceBackendArgs(
                                    name=tandoor.tandoor_service.metadata["name"],
                                    port=kubernetes.networking.v1.ServiceBackendPortArgs(
                                        number=80,
                                    ),
                                ),
                            ),
                            path="/static",
                            path_type="Prefix",
                        ),
                    ],
                ),
            )
        ],
    ),
)
