# import pulumi
# import pulumi_kubernetes as k8s
# import modules.pvc as Pvc
#
# # Get Config
# config = pulumi.Config("tandoor")
#
# # Setup Vars
# label = "tandoor"
#
# # Create PVCs
# media_pvc = Pvc.PVC(
#     name="tandoor-media-pvc",
#     args=Pvc.PvcArgs(
#         name="tandoor-media",
#         app_label=label,
#         volume_size="1Gi",
#     ),
# )
