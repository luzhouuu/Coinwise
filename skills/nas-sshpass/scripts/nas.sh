#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash scripts/nas.sh [--env-file PATH] [--strict-host-key-checking] <command> [...]

Commands:
  ssh [ssh_args...]                 Open an interactive SSH session
  run <remote_command...>           Run a remote command
  sudo-run <remote_command...>      Run a remote command via sudo (uses NAS_SSH_PASSWORD)
  scp-pull <remote_path> <local>    Copy from NAS to local
  scp-push <local_path> <remote>    Copy from local to NAS

Env (read from .env by default):
  NAS_SSH_HOST, NAS_SSH_PORT (default 22), NAS_SSH_USER, NAS_SSH_PASSWORD
USAGE
}

ENV_FILE=".env"
STRICT_HOST_KEY_CHECKING="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env-file)
      ENV_FILE="${2:-}"
      shift 2
      ;;
    --strict-host-key-checking)
      STRICT_HOST_KEY_CHECKING="1"
      shift 1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: env file not found: $ENV_FILE" >&2
  exit 2
fi

if ! command -v sshpass >/dev/null 2>&1; then
  echo "ERROR: sshpass not found. Install it first (e.g. brew install hudochenkov/sshpass/sshpass)." >&2
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found (needed to parse $ENV_FILE safely)." >&2
  exit 2
fi

nas_host=""
nas_port=""
nas_user=""
nas_password=""

while IFS= read -r -d '' key && IFS= read -r -d '' value; do
  case "$key" in
    NAS_SSH_HOST) nas_host="$value" ;;
    NAS_SSH_PORT) nas_port="$value" ;;
    NAS_SSH_USER) nas_user="$value" ;;
    NAS_SSH_PASSWORD) nas_password="$value" ;;
  esac
done < <(
  python3 - "$ENV_FILE" <<'PY'
import ast
import re
import sys

path = sys.argv[1]
wanted = ["NAS_SSH_HOST", "NAS_SSH_PORT", "NAS_SSH_USER", "NAS_SSH_PASSWORD"]
env: dict[str, str] = {}

def parse_value(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    if raw[0] in ("'", '"') and len(raw) >= 2 and raw[-1] == raw[0]:
        try:
            return ast.literal_eval(raw)
        except Exception:
            return raw[1:-1]
    m = re.match(r"^(.*?)(?:\s+#.*)?$", raw)
    return (m.group(1) if m else raw).strip()

with open(path, "r", encoding="utf-8") as f:
    for line in f:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("export "):
            s = s[len("export ") :].lstrip()
        if "=" not in s:
            continue
        key, raw_value = s.split("=", 1)
        key = key.strip()
        if key in wanted:
            env[key] = parse_value(raw_value)

out = sys.stdout
for key in wanted:
    out.write(key)
    out.write("\0")
    out.write(env.get(key, ""))
    out.write("\0")
PY
)

if [[ -z "$nas_host" || -z "$nas_user" || -z "$nas_password" ]]; then
  echo "ERROR: missing NAS SSH env vars in $ENV_FILE. Need NAS_SSH_HOST, NAS_SSH_USER, NAS_SSH_PASSWORD." >&2
  exit 2
fi

if [[ -z "$nas_port" ]]; then
  nas_port="22"
fi

ssh_common_opts=()
if [[ "$STRICT_HOST_KEY_CHECKING" != "1" ]]; then
  ssh_common_opts+=(
    -o StrictHostKeyChecking=no
    -o UserKnownHostsFile=/dev/null
  )
fi

target="${nas_user}@${nas_host}"
export SSHPASS="$nas_password"

cmd="$1"
shift 1

case "$cmd" in
  ssh)
    exec sshpass -e ssh -tt -p "$nas_port" "${ssh_common_opts[@]}" "$target" "$@"
    ;;
  run)
    if [[ $# -lt 1 ]]; then
      echo "ERROR: run requires a remote command" >&2
      exit 2
    fi
    exec sshpass -e ssh -p "$nas_port" "${ssh_common_opts[@]}" "$target" -- "$@"
    ;;
  sudo-run)
    if [[ $# -lt 1 ]]; then
      echo "ERROR: sudo-run requires a remote command" >&2
      exit 2
    fi
    remote_cmd="$(
      python3 - "$@" <<'PY'
import shlex
import sys
print(" ".join(shlex.quote(a) for a in sys.argv[1:]))
PY
    )"
    printf '%s\n' "$nas_password" | sshpass -e ssh -tt -p "$nas_port" "${ssh_common_opts[@]}" "$target" -- "sudo -S -p '' -- $remote_cmd"
    ;;
  scp-pull)
    if [[ $# -ne 2 ]]; then
      echo "ERROR: scp-pull requires <remote_path> <local_path>" >&2
      exit 2
    fi
    exec sshpass -e scp -P "$nas_port" "${ssh_common_opts[@]}" "${target}:$1" "$2"
    ;;
  scp-push)
    if [[ $# -ne 2 ]]; then
      echo "ERROR: scp-push requires <local_path> <remote_path>" >&2
      exit 2
    fi
    exec sshpass -e scp -P "$nas_port" "${ssh_common_opts[@]}" "$1" "${target}:$2"
    ;;
  *)
    echo "ERROR: unknown command: $cmd" >&2
    usage
    exit 2
    ;;
esac
