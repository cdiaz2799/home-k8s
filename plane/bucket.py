import pulumi
import pulumi_cloudflare as cloudflare

from modules import secrets
from plane.config import app_label, config, namespace, namespace_name

# Setup Vars
global_config = pulumi.Config()
cf_account_id = config.get_secret('cloudflare_account_id')
cf_location = config.get('r2_bucket_region')

# Setup Bucket
bucket = cloudflare.R2Bucket(
    'plane-r2-bucket',
    account_id=cf_account_id,
    name='plane',
    location=cf_location,
)


# Construct Cloudflare endpoint URL and handle exceptions
cf_endpoint = cf_account_id.apply(
    lambda url: f'https://{url}.r2.cloudflarestorage.com'
)


# Create Secret
access_key_id = config.require_secret('r2-access-key-id')
secret_access_key = config.require_secret('r2-secret-access-key')
s3_secret = secrets.K8sSecret(
    'plane-r2-bucket-secret',
    namespace=namespace_name,
    app_label=app_label,
    secrets={
        'AWS_REGION': bucket.location,
        'AWS_ACCESS_KEY_ID': access_key_id,
        'AWS_SECRET_ACCESS_KEY': secret_access_key,
        'AWS_ENDPOINT': cf_endpoint,
        'AWS_S3_FORCE_PATH_STYLE': 'true',
        'AWS_S3_BUCKET_NAME': bucket.name,
    },
    opts=pulumi.ResourceOptions(
        parent=namespace, delete_before_replace=True, depends_on=[bucket]
    ),
)
