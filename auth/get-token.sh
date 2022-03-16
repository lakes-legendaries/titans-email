#!/bin/bash

# exit on error
set -e

# load secrets
. ~/secrets/titans-email-creds

# load code from file
CODE="$(cat secrets/code)"

# create curl data body
DATA=$(echo \
    "client_id=$CLIENT_ID" \
    "&client_secret=$CLIENT_SECRET" \
    "&scope=offline_access%20mail.send" \
    "&grant_type=authorization_code" \
    "&code=$CODE" \
)

# curl for new token
curl -sH "Content-Type: application/x-www-form-urlencoded" \
    -d "$DATA" https://login.microsoftonline.com/$TENANT/oauth2/v2.0/token \
> secrets/token
