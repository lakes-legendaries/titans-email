#!/bin/bash

# exit on error
set -e

# check env vars
if [ -z "$SECRETS_DIR" ]; then
    echo "ERROR: No SECRETS_DIR env var set"
    exit 1
fi

# check arguments
if [ $# -lt 1 ]; then
    echo "Usage: send.sh email_json_fname [--ci]"
    exit 1
fi
EMAIL_JSON_FNAME="$1"

# create json-parsing function
get_field() {
    CMD=$(echo \
        "import json; " \
        "print(json.loads(" \
            "open('$SECRETS_DIR/titans-email-token', 'r').read()" \
        ")['$1'])" \
    )
    python -c "$CMD"
}

# download email token (to make sure we're up-to-date)
USE_CI=$( [ $# -gt 0 ] && [ "$2" == "--ci" ] && echo 1 || echo 0)
if [ "$USE_CI" == 1 ]; then
    SECRETS_URL=https://titansfileserver.blob.core.windows.net/webserver/secrets
    SECRETS_FILE=titans-email-token
    SECRETS_SAS=$(cat $SECRETS_DIR/titans-fileserver-sas)
    SECRETS_LOCAL=$SECRETS_DIR/$SECRETS_FILE
    azcopy cp "$SECRETS_URL/$SECRETS_FILE$SECRETS_SAS" "$SECRETS_LOCAL" &> /dev/null
fi

# load email credentials
. $SECRETS_DIR/titans-email-creds

# create curl data body
DATA=$(echo \
    "client_id=$CLIENT_ID" \
    "&client_secret=$CLIENT_SECRET" \
    "&scope=offline_access%20mail.send" \
    "&refresh_token=$(get_field refresh_token)" \
    "&grant_type=refresh_token" \
)

# refresh email token
curl -sH "Content-Type: application/x-www-form-urlencoded" \
    -d "$DATA" https://login.microsoftonline.com/$TENANT/oauth2/v2.0/token \
> $SECRETS_DIR/titans-email-token

# upload refreshed token
if [ "$USE_CI" == 1 ]; then
    azcopy cp "$SECRETS_LOCAL" "$SECRETS_URL/$SECRETS_FILE$SECRETS_SAS"  &> /dev/null
fi

# send email with new token
curl -sX POST \
    -H "Authorization: Bearer $(get_field access_token)" \
    -H "Content-type: application/json" \
    -H "Host: graph.microsoft.com" \
    -d @$EMAIL_JSON_FNAME \
    https://graph.microsoft.com/v1.0/me/sendMail
