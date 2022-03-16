#!/bin/bash

# exit on error
set -e

# load secrets
. ~/secrets/titans-email-creds

# load token from file
REFRESH_TOKEN=$(python -c \
    "import json; print(json.loads(open('secrets/token', 'r').read())['refresh_token'])" \
)

# create curl data body
DATA=$(echo \
    "client_id=$CLIENT_ID" \
    "&client_secret=$CLIENT_SECRET" \
    "&scope=offline_access%20mail.send" \
    "&refresh_token=$REFRESH_TOKEN" \
    "&grant_type=refresh_token" \
)

# curl for new token
curl -sH "Content-Type: application/x-www-form-urlencoded" \
    -d "$DATA" https://login.microsoftonline.com/$TENANT/oauth2/v2.0/token \
> secrets/token
