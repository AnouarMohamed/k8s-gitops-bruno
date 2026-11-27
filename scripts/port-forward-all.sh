#!/usr/bin/env bash
set -euo pipefail

# Opens local kubectl port-forwards matching the local-kind Bruno environment URLs.
# Press Ctrl+C to tear down all background tunnels cleanly.

PIDS=()

cleanup() {
  for pid in "${PIDS[@]}"; do
    kill "${pid}" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

forward() {
  local ns="$1"
  local svc="$2"
  local ports="$3"
  if kubectl -n "${ns}" get "${svc}" >/dev/null 2>&1; then
    echo "Forwarding ${ns}/${svc} -> ${ports}"
    kubectl -n "${ns}" port-forward "${svc}" "${ports}" >/dev/null 2>&1 &
    PIDS+=("$!")
  else
    echo "Skipping ${ns}/${svc} (not found in current context)"
  fi
}

forward "argocd" "svc/argocd-server" "8080:443"
forward "flux-system" "svc/webhook-receiver" "9292:80"
forward "harbor" "svc/harbor-portal" "8085:80"
forward "monitoring" "svc/kube-prometheus-stack-prometheus" "9090:9090"
forward "monitoring" "svc/kube-prometheus-stack-alertmanager" "9093:9093"
forward "monitoring" "svc/kube-prometheus-stack-grafana" "3000:80"

if [[ ${#PIDS[@]} -eq 0 ]]; then
  echo "No target services found in current kubeconfig context." >&2
  exit 1
fi

echo "Active port-forwards running. Press Ctrl+C to stop."
wait
