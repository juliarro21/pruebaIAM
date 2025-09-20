# IAM Microservice
## Cómo correr
cp .env.example .env
docker compose up -d --build
./tests/smoke.sh
## Endpoints
SCIM (/scim/v2/Users), Auth (/auth/token, /auth/me), ABAC (/authz/evaluate)
