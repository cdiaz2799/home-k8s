import pulumi
from pulumi_kubernetes.core.v1 import Namespace


class K8Namespace(pulumi.ComponentResource):
    def __init__(self, name, opts=None):
        super().__init__("custom:k8s:namespace", name, {}, opts)

        # Create Namespace
        self.namespace = Namespace(
            name, metadata={"name": name}, opts=pulumi.ResourceOptions(parent=self)
        )

        # Register Output
        self.register_outputs(
            {
                "namespace": self.namespace,
            }
        )
