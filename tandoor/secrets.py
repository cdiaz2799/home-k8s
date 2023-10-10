import modules.secrets as secrets
import tandoor.config as config

# Import Vars
postgres_pw = config.tandoorConfig.require("postgres-pw")
secret_key = config.tandoorConfig.require("secret-key")

# Create Secrets
tandoor_secrets = secrets.K8sSecret(
    name="tandoor-secrets",
    namespace=config.tandoor_namespace.namespace.metadata["name"],
    app_label=config.app_label,
    secrets={
        "postgresql-password": postgres_pw,
        "secret-key": secret_key,
    },
)
