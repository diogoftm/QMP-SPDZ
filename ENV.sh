# By default everything is set as an example make
# sure to update all the variables to suit your setup
export KEY_REQUEST_INTERFACE='014'

# ETSI 014 specific
export ROOT_CA='ssl/root.crt'

# Both for ETSI 014 & 004
export KMS_URI='127.0.0.1:8443'
export SENDER_SAE_CRT='ssl/sae_001.crt'
export SENDER_SAE_KEY='ssl/sae_001.key'
export RECEIVER_SAE_CRT='ssl/sae_001.crt'
export RECEIVER_SAE_KEY='ssl/sae_001.key'

# Extra for ETSI 004
export SENDER_SAE_ID='qkd//app1@aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
export RECEIVER_SAE_ID='qkd//app2@bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
