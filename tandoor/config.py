import pulumi
import modules.namespace as namespace

# Retrieve Pulumi Config
tandoorConfig = pulumi.Config("tandoor")


# Setup Vars
app_name = "tandoor"
namespace_name = tandoorConfig.get("namespace", default="tandoor")
app_label = {"app": f"{app_name}"}
env_label = {"environment": "production"}
db_tier_label = {"tier": "database"}
svc_tier_label = {"tier": "frontend"}
db_name = tandoorConfig.get("db-name", default="tandoor")
db_username = tandoorConfig.get("db-username", default="tandoor")


# Setup Namespace
tandoor_namespace = namespace.K8Namespace(namespace_name)
