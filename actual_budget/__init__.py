import pulumi

import modules.namespace as k8snamespace

# Import Config
config = pulumi.Config('actual')


# Setup Vars
app_name = 'actual'
app_label = {'app': f'{app_name}'}
app_version = config.get('actual-version', default='latest')

# Setup Namespace
namespace = k8snamespace.K8Namespace(
    name=app_name,
)

# Outputs
pulumi.export('actual-namespace', namespace.namespace.metadata['name'])
