#!/bin/bash

# exit on error
set -e

# load secrets
. ~/secrets/titans-email-creds

# load token from file
TOKEN=$(python -c \
    "import json; print(json.loads(open('secrets/token', 'r').read())['access_token'])" \
)

# curl for new token
curl -sX POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-type: application/json" \
    -H "Host: graph.microsoft.com" \
    -d "$(cat test/simple-message.json)" \
    https://graph.microsoft.com/v1.0/me/sendMail \
