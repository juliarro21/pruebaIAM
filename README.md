# IAM Microservice

## Pre-requisitos
- Docker + Docker Compose v2
- Bash, `curl` y `jq`
- (Opcional) OpenSSL si usas RS256

## Variables de entorno
Ejemplo (`.env.example`):
```
APP_PORT=8080
JWT_ALG=HS256
JWT_SECRET=change_me
JWT_PRIVATE_KEY_PATH=/run/keys/jwtRS256.key
JWT_PUBLIC_KEY_PATH=/run/keys/jwtRS256.key.pub
SEED_USERS_PATH=/app/app/data/seed_users.json
POLICIES_PATH=/app/app/data/policies.json
CLIENT_ID=demo
CLIENT_SECRET=demo123
JWT_EXP_SECONDS=3600
```
Notas:
- `JWT_ALG`: `HS256` por defecto. Para `RS256`, provee llaves y monta `./keys` en `/run/keys`.
- `SEED_USERS_PATH` y `POLICIES_PATH` apuntan a archivos en `app/data/`.

## Cómo ejecutar (Docker)
```bash
cp .env.example .env

# (Opcional RS256)
# openssl genrsa -out keys/jwtRS256.key 2048
# openssl rsa -in keys/jwtRS256.key -pubout -out keys/jwtRS256.key.pub

docker compose up -d --build

# Verificación
curl -s http://localhost:8080/health
# Docs OpenAPI: http://localhost:8080/docs
```

## Endpoints
- SCIM Users:
  - `POST /scim/v2/Users`
  - `GET /scim/v2/Users/{id}`
  - `PATCH /scim/v2/Users/{id}`
  - `GET /scim/v2/Users?filter=userName eq "..."`  
- Auth:
  - `POST /auth/token` (`password` | `client_credentials`)
  - `GET /auth/me`
- ABAC:
  - `POST /authz/evaluate`

## Ejemplos cURL

### SCIM
```bash
# Crear usuario
curl -s -X POST http://localhost:8080/scim/v2/Users   -H 'Content-Type: application/json'   -d '{"userName":"tuser","name":{"givenName":"Test","familyName":"User"},"active":true,"emails":[{"value":"tuser@example.com","primary":true}],"groups":["HR_READERS"]}'

# Buscar por userName
curl -s 'http://localhost:8080/scim/v2/Users?filter=userName%20eq%20"jdoe"'

# Obtener por id
USER_ID=$(curl -s 'http://localhost:8080/scim/v2/Users?filter=userName%20eq%20"tuser"' | jq -r '.Resources[0].id')
curl -s "http://localhost:8080/scim/v2/Users/$USER_ID"

# Patch (desactivar)
curl -s -X PATCH "http://localhost:8080/scim/v2/Users/$USER_ID"   -H 'Content-Type: application/json' -d '{"active":false}'
```

### Auth / JWT
```bash
# Password grant (mock)
TOKEN=$(curl -s -X POST http://localhost:8080/auth/token   -H 'Content-Type: application/json'   -d '{"grant_type":"password","username":"jdoe","password":"x","scope":"read"}' | jq -r .access_token)

# Client credentials
CTOKEN=$(curl -s -X POST http://localhost:8080/auth/token   -H 'Content-Type: application/json'   -d '{"grant_type":"client_credentials","client_id":"demo","client_secret":"demo123","scope":"admin"}' | jq -r .access_token)

# Validar token
curl -s -H "Authorization: Bearer $TOKEN"  http://localhost:8080/auth/me
curl -s -H "Authorization: Bearer $CTOKEN" http://localhost:8080/auth/me
```

### ABAC
```bash
curl -s -X POST http://localhost:8080/authz/evaluate   -H 'Content-Type: application/json'   -d '{
    "subject":{"dept":"HR","groups":["HR_READERS"],"riskScore":20},
    "resource":{"type":"payroll","env":"prod"},
    "context":{"geo":"CL","deviceTrusted":true,"timeOfDay":"10:30"}
  }'
```

## Colección Postman
- Puedes importar `openapi.json` desde `http://localhost:8080/openapi.json` para generar la colección.
- Alternativa: usar los cURL anteriores.

## Supuestos
- IdP/directorio mock embebido; no hay verificación real de contraseña, solo usuario activo.
- Almacenamiento en memoria; se resetea al reiniciar el contenedor.
- JWT firmado con `HS256` po_r defecto vía `JWT_SECRET`. `RS256` soportado con llaves montadas.
- ABAC con políticas estáticas en `POLICIES_PATH`.
- Principio de mínimo privilegio ilustrado en políticas y scopes.

## Pruebas rápidas
```bash
./tests/smoke.sh
```

## OpenAPI
```bash
curl -s http://localhost:8080/openapi.json -o openapi.json
```
