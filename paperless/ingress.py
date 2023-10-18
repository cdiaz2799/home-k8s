import pulumi
import pulumi_kubernetes as kubernetes

import paperless.config as config
import paperless.paperless as paperless

# Setup Vars
app_name = config.app_name
app_label = config.app_label
namespace = config.namespace_name
hostname = config.app_url
service = paperless.service

# Ingress
ingress = kubernetes.networking.v1.Ingress(
    f'{app_name}-ingress',
    api_version='networking.k8s.io/v1',
    kind='Ingress',
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        namespace=namespace,
        labels=app_label,
        annotations={'nginx.ingress.kubernetes.io/proxy-body-size': '50M'},
    ),
    spec=kubernetes.networking.v1.IngressSpecArgs(
        ingress_class_name='nginx',
        rules=[
            kubernetes.networking.v1.IngressRuleArgs(
                host=hostname,
                http=kubernetes.networking.v1.HTTPIngressRuleValueArgs(
                    paths=[
                        kubernetes.networking.v1.HTTPIngressPathArgs(
                            path_type='Prefix',
                            path='/',
                            backend=kubernetes.networking.v1.IngressBackendArgs(
                                service=kubernetes.networking.v1.IngressServiceBackendArgs(
                                    name=service.metadata['name'],
                                    port=kubernetes.networking.v1.ServiceBackendPortArgs(
                                        name='http',
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
