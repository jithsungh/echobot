# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # optional: loads .env for local dev

class DefaultConfig:
    """
    Configuration object consumed by ConfigurationBotFrameworkAuthentication
    (The SDK reads keys by attribute name or dict-like access).
    Put these env vars in your App Service configuration or .env for local dev.
    """

    def __init__(self):
        self.microsoft_app_id = os.getenv("MicrosoftAppId", "")
        self.microsoft_app_password = os.getenv("MicrosoftAppPassword", "")
        # new in 2024–2025: App type and tenant support
        # Allowed values: MultiTenant | SingleTenant | UserAssignedMSI
        self.microsoft_app_type = os.getenv("MicrosoftAppType", "MultiTenant")
        # required when using SingleTenant
        self.microsoft_app_tenant_id = os.getenv("MicrosoftAppTenantId", "")
        # optional: region / other keys the SDK may read
        self.port = int(os.getenv("PORT", "3978"))

    # allow dict-like access (ConfigurationBotFrameworkAuthentication uses this)
    def __getitem__(self, key):
        return getattr(self, key.lower(), None)

    def get(self, key, default=None):
        return getattr(self, key.lower(), default)
