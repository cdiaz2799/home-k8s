import pulumi
import pulumi_kubernetes as kubernetes

import plane.config as plane
from plane.plane import frontend_service, api_service, spaces_service

# Setup Ingressingress =
ingress = kubernetes.networking.v1.Ingress(
    f'{plane.app_name}-ingress',
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name=f'{plane.app_name}-ingress',
        annotations={'kubernetes.io/ingress.class': 'nginx'},
        namespace=plane.namespace_name,
    ),
    spec=kubernetes.networking.v1.IngressSpecArgs(
        ingress_class_name='nginx',
        rules=[
            kubernetes.networking.v1.IngressRuleArgs(
                host=plane.fqdn,
                http=kubernetes.networking.v1.HTTPIngressRuleValueArgs(
                    paths=[
                        kubernetes.networking.v1.HTTPIngressPathArgs(
                            path='/',
                            path_type='Prefix',
                            backend=kubernetes.networking.v1.IngressBackendArgs(
                                service=kubernetes.networking.v1.IngressServiceBackendArgs(
                                    name=frontend_service.metadata['name'],
                                    port=kubernetes.networking.v1.ServiceBackendPortArgs(
                                        number=frontend_service.spec.ports[
                                            0
                                        ].port,
                                    ),
                                )
                            ),
                        ),
                        kubernetes.networking.v1.HTTPIngressPathArgs(
                            path='/api',
                            path_type='Prefix',
                            backend=kubernetes.networking.v1.IngressBackendArgs(
                                service=kubernetes.networking.v1.IngressServiceBackendArgs(
                                    name=api_service.metadata['name'],
                                    port=kubernetes.networking.v1.ServiceBackendPortArgs(
                                        number=api_service.spec.ports[0].port,
                                    ),
                                )
                            ),
                        ),
                        kubernetes.networking.v1.HTTPIngressPathArgs(
                            path='/spaces',
                            path_type='Prefix',
                            backend=kubernetes.networking.v1.IngressBackendArgs(
                                service=kubernetes.networking.v1.IngressServiceBackendArgs(
                                    name=spaces_service.metadata['name'],
                                    port=kubernetes.networking.v1.ServiceBackendPortArgs(
                                        number=spaces_service.spec.ports[
                                            0
                                        ].port,
                                    ),
                                )
                            ),
                        ),
                    ]
                ),
            )
        ],
    ),
    opts=pulumi.ResourceOptions(
        parent=plane.namespace, delete_before_replace=True
    ),
)
