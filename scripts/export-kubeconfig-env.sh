#!/usr/bin/env bash
set -euo pipefail

# Mints a short-lived TokenRequest for the bruno-reader ServiceAccount and writes
# local secrets into an untracked .env file for CLI smoke execution.

NAMESPACE="${1:-kube-system}"
SERVICE_ACCOUNT="${2:-bruno-reader}"
DURATION="${3:-1h}"
OUTPUT_FILE="${4:-.env}"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "error: kubectl is required on PATH" >&2
  exit 1
fi

API_SERVER="$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')"
TOKEN="$(kubectl -n "${NAMESPACE}" create token "${SERVICE_ACCOUNT}" --duration="${DURATION}")"

cat > "${OUTPUT_FILE}" <<EOF
K8S_API_URL=${API_SERVER}
K8S_TOKEN=${TOKEN}
EOF

chmod 600 "${OUTPUT_FILE}"
echo "Wrote ephemeral cluster token (${DURATION}) for ${NAMESPACE}/${SERVICE_ACCOUNT} to ${OUTPUT_FILE}"
