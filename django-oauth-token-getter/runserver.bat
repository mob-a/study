pushd "%~dp0"

set CLIENT_ID=aaaa
set CLIENT_SECRET=aaaa
set SERVER_PORT=8080

set OAUTHLIB_INSECURE_TRANSPORT=1
set REDIRECT_URI=http://localhost:%SERVER_PORT%/callback

dist\django\django.exe runserver localhost:%SERVER_PORT%
