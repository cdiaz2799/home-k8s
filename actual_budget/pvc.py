import pulumi

import actual_budget
import modules.pvc as pvc

# Get Vars
config = actual_budget.config
volume_size = config.get('volume-size', default='100Mi')
namespace = actual_budget.namespace.namespace.metadata['name']


actual_pvc = pvc.K8sPVC(
    'actual-pvc',
    namespace=namespace,
    app_label=actual_budget.app_label,
    volume_size=volume_size,
)

# Output
pulumi.export('actual-pvc', actual_pvc.pvc.metadata['name'])
