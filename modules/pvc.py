from typing import Dict

from pulumi import ResourceOptions, ComponentResource
from pulumi_kubernetes.core.v1 import (
    PersistentVolumeClaim,
    PersistentVolumeClaimInitArgs,
    PersistentVolumeClaimSpecArgs,
    ResourceRequirementsArgs,
)
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs


class K8sPVC(ComponentResource):
    def __init__(
        self,
        name: str,
        namespace: str,
        app_label: Dict[str, str],
        volume_size: str,
        opts: ResourceOptions = None,
    ):
        super().__init__("custom:k8s:pvc", name, {}, opts)

        # Create PVC
        self.pvc = PersistentVolumeClaim(
            name,
            args=PersistentVolumeClaimInitArgs(
                api_version="v1",
                metadata=ObjectMetaArgs(
                    name=name,
                    namespace=namespace,
                    labels=app_label,
                ),
                spec=PersistentVolumeClaimSpecArgs(
                    access_modes=["ReadWriteOnce"],
                    resources=ResourceRequirementsArgs(
                        requests={
                            "storage": volume_size,
                        },
                    ),
                ),
            ),
            opts=ResourceOptions(parent=self),
        )

        # Register Outputs
        self.register_outputs({"pvc": self.pvc.metadata["name"]})
