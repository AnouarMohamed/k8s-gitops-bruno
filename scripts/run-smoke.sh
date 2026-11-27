#!/usr/bin/env bash
set -euo pipefail

COLLECTION="${1:-}"
ENV_NAME="${2:-local-kind}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -z "${COLLECTION}" ]]; then
  echo "Usage: $0 <collection-dir-name> [environment-name]" >&2
  echo "Available collections:" >&2
  ls -1 "${ROOT_DIR}/collections" >&2
  exit 1
fi

COL_PATH="${ROOT_DIR}/collections/${COLLECTION}"
if [[ ! -d "${COL_PATH}" ]]; then
  echo "error: collection not found: ${COL_PATH}" >&2
  exit 1
fi

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.env"
  set +a
fi

mkdir -p "${ROOT_DIR}/reports"
REPORT_FILE="${ROOT_DIR}/reports/${COLLECTION}-${ENV_NAME}.json"

cd "${COL_PATH}"
npx --no-install bru run \
  --env "${ENV_NAME}" \
  --reporter-json "${REPORT_FILE}" \
  ${K8S_TOKEN:+--env-var "k8sToken=${K8S_TOKEN}"} \
  ${ARGOCD_TOKEN:+--env-var "argocdToken=${ARGOCD_TOKEN}"} \
  ${ARGOCD_PASSWORD:+--env-var "argocdPassword=${ARGOCD_PASSWORD}"} \
  ${FLUX_WEBHOOK_SECRET:+--env-var "fluxWebhookSecret=${FLUX_WEBHOOK_SECRET}"} \
  ${HARBOR_PASSWORD:+--env-var "harborPassword=${HARBOR_PASSWORD}"} \
  ${GRAFANA_TOKEN:+--env-var "grafanaToken=${GRAFANA_TOKEN}"}

echo "Report written to ${REPORT_FILE}"
