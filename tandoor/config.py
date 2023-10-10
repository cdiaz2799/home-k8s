import pulumi
import modules.namespace as namespace

# Retrieve Pulumi Config
tandoorConfig = pulumi.Config("tandoor")


# Setup Vars
namespace_name = tandoorConfig.get("namespace", default="tandoor")
app_label = {"app": "tandoor"}

# Setup Namespace
tandoor_namespace = namespace.K8Namespace(namespace_name)
