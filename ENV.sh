# By default everything is set as an example make
# sure to update all the variables to suit your setup
export KEY_REQUEST_INTERFACE='004'

# ETSI 014 specific
export ROOT_CA='ssl/root_CA.pem'

# Both for ETSI 014 & 004
export KMS_URI='127.0.0.1:25575'
export SENDER_SAE_CRT='ssl/127.0.0.1.pem'
export SENDER_SAE_KEY='ssl/127.0.0.1.key'
export RECEIVER_SAE_CRT='ssl/127.0.0.1.pem'
export RECEIVER_SAE_KEY='ssl/127.0.0.1.key'

# Extra for ETSI 004
export SENDER_SAE_ID='qkd//app1@aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
export RECEIVER_SAE_ID='qkd//app2@bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
