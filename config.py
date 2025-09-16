#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = int(os.environ.get("PORT", 8000))
    APP_ID = os.environ.get("MicrosoftAppId", "1a0d5572-e3f6-421d-a9e4-068cfc0d421e")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "X4U8Q~a0_xnkoe2Wu7yVb_oHgcF.mR93M3vAuaO_")
    APP_TYPE = os.environ.get("MicrosoftAppType", "SingleTenant")
    APP_TENANT_ID = os.environ.get("MicrosoftAppTenantId", "6f1ac041-698d-4fc7-984b-4a040764d7a2")
