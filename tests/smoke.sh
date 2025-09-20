#!/usr/bin/env bash
set -euo pipefail
BASE=${BASE:-http://localhost:8080}
USERN=${USERN:-labuser$RANDOM}
curl -s ${BASE}/health | jq -e '.status=="ok"'
curl -s -X POST ${BASE}/scim/v2/Users -H 'Content-Type: application/json' \
 -d '{"userName":"'"$USERN"'","name":{"givenName":"Lab","familyName":"User"},"active":true,"emails":[{"value":"'"$USERN"'@example.com","primary":true}],"groups":["HR_READERS"]}' | jq -e '.id'
USER_ID=$(curl -s "${BASE}/scim/v2/Users?filter=userName%20eq%20\"$USERN\"" | jq -r '.Resources[0].id')
curl -s ${BASE}/scim/v2/Users/${USER_ID} | jq -e '.userName=="'"$USERN"'"'
curl -s -X PATCH ${BASE}/scim/v2/Users/${USER_ID} -H 'Content-Type: application/json' -d '{"active":false}' | jq -e '.active==false'
TOKEN=$(curl -s -X POST ${BASE}/auth/token -H 'Content-Type: application/json' \
 -d '{"grant_type":"password","username":"jdoe","password":"x","scope":"read"}' | jq -r .access_token)
curl -s -H "Authorization: Bearer $TOKEN" ${BASE}/auth/me | jq -e '.sub=="jdoe"'
curl -s -X POST ${BASE}/authz/evaluate -H 'Content-Type: application/json' \
 -d '{"subject":{"dept":"HR","groups":["HR_READERS"],"riskScore":20},"resource":{"type":"payroll","env":"prod"},"context":{"geo":"CL","deviceTrusted":true}}' | jq -e '.decision=="Permit"'
echo "OK"
