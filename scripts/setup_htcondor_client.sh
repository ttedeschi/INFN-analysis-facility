export _condor_AUTH_SSL_CLIENT_CAFILE=/ca.crt
export _condor_SEC_DEFAULT_AUTHENTICATION_METHODS=SCITOKENS
export _condor_SCITOKENS_FILE=/tmp/token                          # token from CMS-IAM
export _condor_COLLECTOR_HOST=$1.xip.io:$2
export _condor_SCHEDD_HOST=$3
export _condor_TOOL_DEBUG=D_FULLDEBUG,D_SECURITY
