#!/usr/bin/env bash
set -euo pipefail

# Deploy do bot para Azure Container Apps (sem ingress, 1 replica fixa).
# Requisitos: Azure CLI logado (az login) e permissao na assinatura.

RESOURCE_GROUP="${RESOURCE_GROUP:-rg-patologias-bot}"
LOCATION="${LOCATION:-brazilsouth}"
ACR_NAME="${ACR_NAME:-}"
CONTAINERAPPS_ENV="${CONTAINERAPPS_ENV:-cae-patologias-bot}"
APP_NAME="${APP_NAME:-patologias-bot}"
IMAGE_TAG="${IMAGE_TAG:-$(date +%Y%m%d%H%M%S)}"
CPU="${CPU:-0.5}"
MEMORY="${MEMORY:-1.0Gi}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
GEMINI_MODEL="${GEMINI_MODEL:-gemini-flash-latest}"
GOOGLE_API_KEY="${GOOGLE_API_KEY:-${GEMINI_API_KEY:-}}"

if [[ -z "${TELEGRAM_TOKEN:-}" ]]; then
  echo "Erro: variavel TELEGRAM_TOKEN nao definida." >&2
  exit 1
fi

if [[ -z "${GOOGLE_API_KEY:-}" ]]; then
  echo "Erro: variavel GOOGLE_API_KEY (ou GEMINI_API_KEY) nao definida." >&2
  exit 1
fi

if ! command -v az >/dev/null 2>&1; then
  echo "Erro: Azure CLI (az) nao encontrado no PATH." >&2
  exit 1
fi

echo "[1/6] Validando autenticacao Azure..."
az account show >/dev/null

echo "Preparando extensao e providers do Azure Container Apps..."
az extension add --name containerapp --upgrade >/dev/null
az provider register --namespace Microsoft.App >/dev/null
az provider register --namespace Microsoft.OperationalInsights >/dev/null

echo "[2/6] Criando Resource Group (se necessario): ${RESOURCE_GROUP}"
az group create --name "${RESOURCE_GROUP}" --location "${LOCATION}" >/dev/null

if [[ -z "${ACR_NAME}" ]]; then
  ACR_NAME="$(az acr list --resource-group "${RESOURCE_GROUP}" --query "[0].name" -o tsv)"
fi

if [[ -z "${ACR_NAME}" ]]; then
  suffix="$(date +%s | tail -c 6)"
  ACR_NAME="acrpatologias${suffix}"
fi

echo "[3/6] Criando ACR (se necessario): ${ACR_NAME}"
if ! az acr show --name "${ACR_NAME}" --resource-group "${RESOURCE_GROUP}" >/dev/null 2>&1; then
  az acr create \
    --name "${ACR_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --sku Basic \
    --admin-enabled true >/dev/null
fi

echo "[4/6] Build da imagem no ACR"
az acr build \
  --registry "${ACR_NAME}" \
  --image "${APP_NAME}:${IMAGE_TAG}" \
  . >/dev/null

ACR_LOGIN_SERVER="$(az acr show --name "${ACR_NAME}" --resource-group "${RESOURCE_GROUP}" --query loginServer -o tsv)"
ACR_USERNAME="$(az acr credential show --name "${ACR_NAME}" --query username -o tsv)"
ACR_PASSWORD="$(az acr credential show --name "${ACR_NAME}" --query passwords[0].value -o tsv)"
IMAGE="${ACR_LOGIN_SERVER}/${APP_NAME}:${IMAGE_TAG}"

echo "[5/6] Criando ambiente Container Apps (se necessario): ${CONTAINERAPPS_ENV}"
if ! az containerapp env show --name "${CONTAINERAPPS_ENV}" --resource-group "${RESOURCE_GROUP}" >/dev/null 2>&1; then
  az containerapp env create \
    --name "${CONTAINERAPPS_ENV}" \
    --resource-group "${RESOURCE_GROUP}" \
    --location "${LOCATION}" >/dev/null
fi

echo "[6/6] Criando/Atualizando Container App: ${APP_NAME}"
if az containerapp show --name "${APP_NAME}" --resource-group "${RESOURCE_GROUP}" >/dev/null 2>&1; then
  az containerapp secret set \
    --name "${APP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --secrets telegram-token="${TELEGRAM_TOKEN}" google-api-key="${GOOGLE_API_KEY}" >/dev/null

  az containerapp registry set \
    --name "${APP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --server "${ACR_LOGIN_SERVER}" \
    --username "${ACR_USERNAME}" \
    --password "${ACR_PASSWORD}" >/dev/null

  az containerapp update \
    --name "${APP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --image "${IMAGE}" \
    --set-env-vars \
      TELEGRAM_TOKEN=secretref:telegram-token \
      GOOGLE_API_KEY=secretref:google-api-key \
      LOG_LEVEL="${LOG_LEVEL}" \
      GEMINI_MODEL="${GEMINI_MODEL}" >/dev/null
else
  az containerapp create \
    --name "${APP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --environment "${CONTAINERAPPS_ENV}" \
    --image "${IMAGE}" \
    --cpu "${CPU}" \
    --memory "${MEMORY}" \
    --min-replicas 1 \
    --max-replicas 1 \
    --registry-server "${ACR_LOGIN_SERVER}" \
    --registry-username "${ACR_USERNAME}" \
    --registry-password "${ACR_PASSWORD}" \
    --secrets telegram-token="${TELEGRAM_TOKEN}" google-api-key="${GOOGLE_API_KEY}" \
    --env-vars \
      TELEGRAM_TOKEN=secretref:telegram-token \
      GOOGLE_API_KEY=secretref:google-api-key \
      LOG_LEVEL="${LOG_LEVEL}" \
      GEMINI_MODEL="${GEMINI_MODEL}" >/dev/null
fi

echo "Deploy concluido."
echo "Imagem ativa: ${IMAGE}"
echo "Logs (follow):"
echo "az containerapp logs show --name ${APP_NAME} --resource-group ${RESOURCE_GROUP} --follow"
