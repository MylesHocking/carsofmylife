# /utils/gcp_utils.py

import os
import json
from google.cloud import storage

GCP_CREDENTIALS_JSON_STRING = os.environ.get("GCP_CREDENTIALS_JSON_STRING")

if GCP_CREDENTIALS_JSON_STRING:
    creds_json = json.loads(GCP_CREDENTIALS_JSON_STRING)
    storage_client = storage.Client.from_service_account_info(creds_json)
else:
    storage_client = storage.Client()
