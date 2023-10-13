from typing import Dict

import pulumi
from pulumi_kubernetes.core.v1 import Secret, SecretInitArgs
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs


class K8sSecret(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        namespace: str,
        app_label: Dict[str, str],
        secrets: Dict[str, str],
        opts: pulumi.ResourceOptions = None,
    ):
        super().__init__('custom:k8s:secrets', name, {}, opts)

        # Create Secrets
        self.secret = Secret(
            name,
            args=SecretInitArgs(
                metadata=ObjectMetaArgs(
                    name=name,
                    namespace=namespace,
                    labels=app_label,
                ),
                type='Opaque',
                string_data=secrets,
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Register Outputs
        self.register_outputs({'secrets': self.secret.metadata['name']})
