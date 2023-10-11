import modules.pvc as pvc
import tandoor.config as config

# Import Vars
volume_size = config.tandoorConfig.get("volume-size", default="1Gi")
namespace = config.tandoor_namespace.namespace.metadata["name"]

# Create PVCs
media_pvc = pvc.K8sPVC(
    name=f"{config.app_name}-media",
    namespace=namespace,
    app_label=config.app_label,
    volume_size=volume_size,
)

static_pvc = pvc.K8sPVC(
    name=f"{config.app_name}-static",
    namespace=namespace,
    app_label=config.app_label,
    volume_size=volume_size,
)
