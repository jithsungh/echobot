"""
Configuration management for single-tenant Azure Bot Service.
Handles environment variables and authentication setup.
"""
import os
import logging
from botbuilder.core import ConfigurationBotFrameworkAuthentication

logger = logging.getLogger(__name__)


class Config:
    """Bot Configuration for single-tenant deployment."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # Required for single-tenant authentication
        self.MICROSOFT_APP_TYPE = os.environ.get("MicrosoftAppType", "SingleTenant")
        self.MICROSOFT_APP_ID = os.environ.get("MicrosoftAppId", "")
        self.MICROSOFT_APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
        self.MICROSOFT_APP_TENANT_ID = os.environ.get("MicrosoftAppTenantId", "")
        
        # Optional configuration
        self.PORT = int(os.environ.get("PORT", 3978))
        
        # Logging configuration
        self.LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
        
        # Bot settings
        self.BOT_NAME = os.environ.get("BOT_NAME", "SingleTenantBot")
        self.BOT_VERSION = os.environ.get("BOT_VERSION", "1.0.0")
        
        # Azure App Service settings
        self.WEBSITE_HOSTNAME = os.environ.get("WEBSITE_HOSTNAME", "")
        self.WEBSITE_SITE_NAME = os.environ.get("WEBSITE_SITE_NAME", "")
    
    def validate(self):
        """Validate required configuration for single-tenant bot."""
        missing_vars = []
        
        if not self.MICROSOFT_APP_ID:
            missing_vars.append("MicrosoftAppId")
        if not self.MICROSOFT_APP_PASSWORD:
            missing_vars.append("MicrosoftAppPassword") 
        if not self.MICROSOFT_APP_TENANT_ID:
            missing_vars.append("MicrosoftAppTenantId")
            
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Validate app type
        if self.MICROSOFT_APP_TYPE not in ["SingleTenant", "MultiTenant", "UserAssignedMSI"]:
            raise ValueError(f"Invalid MicrosoftAppType: {self.MICROSOFT_APP_TYPE}")
        
        logger.info(f"Bot configured for {self.MICROSOFT_APP_TYPE} with App ID: {self.MICROSOFT_APP_ID}")
        logger.info(f"Tenant ID: {self.MICROSOFT_APP_TENANT_ID}")
        
        if self.WEBSITE_HOSTNAME:
            logger.info(f"Running on Azure App Service: {self.WEBSITE_HOSTNAME}")
    
    def get_auth_config(self) -> ConfigurationBotFrameworkAuthentication:
        """Get the authentication configuration for CloudAdapter."""
        return ConfigurationBotFrameworkAuthentication(
            app_id=self.MICROSOFT_APP_ID,
            app_password=self.MICROSOFT_APP_PASSWORD,
            app_tenant_id=self.MICROSOFT_APP_TENANT_ID,
            app_type=self.MICROSOFT_APP_TYPE
        )
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return not bool(self.WEBSITE_HOSTNAME)
    
    def get_bot_info(self) -> dict:
        """Get bot information dictionary."""
        return {
            "name": self.BOT_NAME,
            "version": self.BOT_VERSION,
            "app_type": self.MICROSOFT_APP_TYPE,
            "environment": "development" if self.is_development() else "production"
        }
