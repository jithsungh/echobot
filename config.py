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
    APP_ID = os.environ.get("MicrosoftAppId", "6d9ae75d-ddd2-479c-8845-5ee08e4a6391")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "AWw8Q~SM6arIUHRAwdPYMuEYxnW8U8OfHJkC7cLE")
    APP_TYPE = os.environ.get("MicrosoftAppType", "SingleTenant")
    APP_TENANT_ID = os.environ.get("MicrosoftAppTenantId", "6f1ac041-698d-4fc7-984b-4a040764d7a2")
