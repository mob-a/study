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

export REDIRECT_URI="https://$SERVER_HOST:$SERVER_PORT/callback"

tmpdir=`mktemp -d`
openssl genrsa -out $tmpdir/server.key 2048
openssl req -new -key $tmpdir/server.key -out $tmpdir/server.csr -subj "/C=JP/ST=Tokyo/L=Tokyo/O=sample/OU=sample/CN=$SERVER_HOST"
openssl x509 -req -days 365 -in $tmpdir/server.csr -signkey $tmpdir/server.key -out $tmpdir/server.crt

cd django
uwsgi --https 0.0.0.0:$SERVER_PORT,$tmpdir/server.crt,$tmpdir/server.key --module oauthtoken.wsgi
