# from pulumi import ResourceOptions, ComponentResource, Input
# from pulumi_kubernetes.core.v1 import (
#     ObjectMetaArgs,
# )
#
#
# class PvcArgs:
#     def __init__(
#         name: Input[str],
#         app_label: Input[str],
#         volume_size: Input[str],
#     ):
#         self.name = (name,)
#         self.app_label = (app_label,)
#         self.volume_size = (volume_size,)
#
#
# class PVC(ComponentResource):
#     def __init__(self, name: str, args: PvcArgs, opts: ResourceOptions = None):
#         super().__init__("custom:k8:PersistentVolumeClaim", name, {}, opts)
#
#         child_opts = ResourceOptions(parent=self)
#
#         self.pvc = PersistentVolumeClaim(
#             name,
#             metadata=ObjectMetaArgs(
#                 name=name,
#                 labels=(
#                     {
#                         "app": args.app_label,
#                     },
#                 ),
#             ),
#             spec=
#             opts=child_opts,
#         )
#         self.register_outputs({})
