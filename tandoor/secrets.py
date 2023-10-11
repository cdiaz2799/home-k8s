import modules.secrets as secrets
import tandoor.config as config

# Import Vars
namespace = config.tandoor_namespace.namespace.metadata["name"]
postgres_pw = config.tandoorConfig.require("postgres-pw")
secret_key = config.tandoorConfig.require("secret-key")

# Create Secrets
tandoor_secrets = secrets.K8sSecret(
    name=f"{config.app_name}-secrets",
    namespace=namespace,
    app_label=config.app_label,
    secrets={
        "postgresql-password": postgres_pw,
        "secret-key": secret_key,
    },
)
