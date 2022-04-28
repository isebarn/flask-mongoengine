import boto3

import os
from flask import request
from endpoints import Resource

client = boto3.client("cognito-idp")
client_id = os.environ.get("AWS_COGNITO_CLIENT_ID")
pool_id = os.environ.get("AWS_COGNITO_USER_POOL_NAME")

schema_attributes = client.describe_user_pool(UserPoolId=pool_id)["UserPool"][
    "SchemaAttributes"
]


def dispatch_request(self, *args, **kwargs):
    pass


Resource.dispatch_requests.append(dispatch_request)
