---
name: nas-sshpass
description: Connect to a NAS (e.g. Synology) via SSH/SCP using `sshpass` with credentials stored in a project `.env` (NAS_SSH_HOST, NAS_SSH_PORT, NAS_SSH_USER, NAS_SSH_PASSWORD); use to run remote commands and copy files without interactive password prompts.
---

# NAS SSH via sshpass

## Configure `.env`

Add these variables (shell-style `KEY=value` lines):

```env
NAS_SSH_HOST=your_nas_host
NAS_SSH_PORT=22
NAS_SSH_USER=your_nas_user
NAS_SSH_PASSWORD=your_nas_password
```

## Use the bundled script

The bundled script `scripts/nas.sh` reads `.env` from your current directory by default:

```bash
# interactive session
bash scripts/nas.sh ssh

# run remote command
bash scripts/nas.sh run docker ps

# run remote command via sudo (useful for Docker on Synology)
bash scripts/nas.sh sudo-run /usr/local/bin/docker ps

# copy files
bash scripts/nas.sh scp-pull /path/on/nas/file ./file
bash scripts/nas.sh scp-push ./local-file /path/on/nas/local-file
```

If your env file is not `./.env`:

```bash
bash scripts/nas.sh --env-file /path/to/.env run df -h
```

## Notes

- Install `sshpass` first (macOS/Homebrew example): `brew install hudochenkov/sshpass/sshpass`.
- By default the script disables strict host key checking; pass `--strict-host-key-checking` to keep SSH host checks enabled.
