from pulumi_kubernetes import core, meta

import tandoor.config as config

config_map = core.v1.ConfigMap(
    "tandoor-config-map",
    kind="ConfigMap",
    api_version="v1",
    metadata=meta.v1.ObjectMetaArgs(
        labels=config.app_label,
        name="tandoor-nginx-config",
        namespace=config.tandoor_namespace.namespace.metadata["name"],
    ),
    data={
        "nginx-config": """
    events {
      worker_connections 1024;
    }
    http {
      include mime.types;
      server {
        listen 80;
        server_name _;

        client_max_body_size 16M;

        # serve static files
        location /static/ {
          alias /static/;
        }
        # serve media files
        location /media/ {
          alias /media/;
        }
      }
    }
""",
    },
)
