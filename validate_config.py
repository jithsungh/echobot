#!/usr/bin/env python3
"""
Configuration validation script for Azure Bot Service
Run this script to verify your environment is properly configured before deployment.
"""

import os
import sys
from dotenv import load_dotenv

def validate_config():
    """Validate bot configuration."""
    
    # Load environment variables
    load_dotenv()
    
    print("🤖 Azure Bot Service Configuration Validator")
    print("=" * 50)
    
    # Required environment variables
    required_vars = {
        'MicrosoftAppId': os.getenv('MicrosoftAppId'),
        'MicrosoftAppPassword': os.getenv('MicrosoftAppPassword'), 
        'MicrosoftAppTenantId': os.getenv('MicrosoftAppTenantId'),
        'MicrosoftAppType': os.getenv('MicrosoftAppType', 'SingleTenant')
    }
    
    # Optional variables
    optional_vars = {
        'PORT': os.getenv('PORT', '3978'),
        'BOT_NAME': os.getenv('BOT_NAME', 'EchoBot'),
    }
    
    errors = []
    warnings = []
    
    # Check required variables
    for var_name, var_value in required_vars.items():
        if not var_value or var_value.startswith('your-'):
            errors.append(f"❌ {var_name}: Missing or not configured")
        else:
            # Mask sensitive values
            if 'Password' in var_name:
                display_value = '***' + var_value[-4:] if len(var_value) > 4 else '***'
            elif 'Id' in var_name:
                display_value = var_value[:8] + '...' if len(var_value) > 8 else var_value
            else:
                display_value = var_value
            print(f"✅ {var_name}: {display_value}")
    
    # Check optional variables
    print("\nOptional Configuration:")
    for var_name, var_value in optional_vars.items():
        print(f"ℹ️  {var_name}: {var_value}")
    
    # Validate App Type
    app_type = required_vars.get('MicrosoftAppType', '').lower()
    if app_type != 'singletenant':
        warnings.append(f"⚠️  MicrosoftAppType is '{app_type}', expected 'SingleTenant'")
    
    # Check for common GUID patterns
    app_id = required_vars.get('MicrosoftAppId', '')
    tenant_id = required_vars.get('MicrosoftAppTenantId', '')
    
    if app_id and len(app_id) != 36:
        warnings.append("⚠️  MicrosoftAppId doesn't look like a valid GUID (should be 36 characters)")
    
    if tenant_id and len(tenant_id) != 36:
        warnings.append("⚠️  MicrosoftAppTenantId doesn't look like a valid GUID (should be 36 characters)")
    
    # Print results
    print("\n" + "=" * 50)
    
    if errors:
        print("❌ ERRORS FOUND:")
        for error in errors:
            print(f"   {error}")
        print("\n💡 Please update your .env file with the correct values from Azure Portal.")
        return False
    
    if warnings:
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   {warning}")
    
    if not errors:
        print("✅ Configuration looks good!")
        print("\n🚀 Next steps:")
        print("   1. Deploy to Azure App Service")
        print("   2. Set the same environment variables in Azure App Service Configuration")
        print("   3. Use startup command: gunicorn --bind 0.0.0.0 --worker-class aiohttp.worker.GunicornWebWorker --timeout 600 app:APP")
        print("   4. Test the health endpoint: https://your-app.azurewebsites.net/health")
        print("   5. Test in Bot Framework Web Chat")
        
        return True


def test_imports():
    """Test if all required packages can be imported."""
    print("\n📦 Testing Package Imports:")
    print("-" * 30)
    
    required_packages = [
        ('aiohttp', 'aiohttp'),
        ('botbuilder.core', 'botbuilder-core'),
        ('botbuilder.schema', 'botbuilder-schema'),
        ('botbuilder.integration.aiohttp', 'botbuilder-integration-aiohttp'),
        ('dotenv', 'python-dotenv'),
        ('gunicorn', 'gunicorn')
    ]
    
    missing_packages = []
    
    for package, pip_name in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (install with: pip install {pip_name})")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n💡 Install missing packages: pip install {' '.join(missing_packages)}")
        return False
    
    return True


if __name__ == "__main__":
    print("Starting validation...\n")
    
    # Test imports first
    imports_ok = test_imports()
    
    # Test configuration
    config_ok = validate_config()
    
    if imports_ok and config_ok:
        print("\n🎉 All checks passed! Your bot is ready for deployment.")
        sys.exit(0)
    else:
        print("\n❌ Some issues found. Please fix them before deployment.")
        sys.exit(1)
