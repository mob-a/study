#!/bin/bash

assertion () {
if [ -z $1 ]
then
    exit 1
fi
}

envfile=$1
source $envfile

assertion $CLIENT_ID
assertion $CLIENT_SECRET
assertion $SERVER_HOST

export REDIRECT_URI="http://$SERVER_HOST:$SERVER_PORT/callback"

export OAUTHLIB_INSECURE_TRANSPORT=1

cd django
uwsgi --http 0.0.0.0:$SERVER_PORT --module oauthtoken.wsgi
