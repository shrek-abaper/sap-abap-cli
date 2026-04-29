# PROJECT KNOWLEDGE BASE

**Generated:** 2026-04-29
**Branch:** main

## OVERVIEW
Python CLI + AI agent skill for reading SAP ABAP source code and DDIC metadata from SAP systems via the ADT (ABAP Development Tools) REST API. Designed to be dropped into AI agent skill directories (opencode, Claude Code, Cursor).

## STRUCTURE
```
sap-abap-cli/
├── skills/sap-adt-cli/    # Entire implementation lives here (see skills/sap-adt-cli/AGENTS.md)
│   ├── SKILL.md            # Agent framework integration metadata
│   ├── scripts/            # Python CLI + library
│   └── references/         # ADT API reference docs
├── setup-opencode-abap-cli.bat  # Windows one-click installer for opencode + skill
├── README.md               # Full docs (EN)
└── README.zh-CN.md         # Full docs (ZH)
```

## WHERE TO LOOK
| Task | Location |
|------|----------|
| Run the CLI | `skills/sap-adt-cli/scripts/sap_adt_cli.py` |
| Add a new SAP object type command | `scripts/lib/handlers.py` + `scripts/sap_adt_cli.py` |
| Change credential storage/loading | `scripts/lib/config.py` |
| Change HTTP/CSRF behavior | `scripts/lib/client.py` |
| Agent skill description/trigger | `skills/sap-adt-cli/SKILL.md` |
| ADT endpoint reference | `skills/sap-adt-cli/references/adt_api.md` |
| Windows installer logic | `setup-opencode-abap-cli.bat` |

## COMMANDS
```bash
# Configure credentials (interactive)
python3 skills/sap-adt-cli/scripts/sap_adt_cli.py configure

# Or non-interactively (agent workflows)
SAP_PASSWORD="secret" python3 skills/sap-adt-cli/scripts/sap_adt_cli.py configure \
  --url "https://my-sap.example.com:8000" --username MYUSER --client 100

# Check connection
python3 skills/sap-adt-cli/scripts/sap_adt_cli.py status

# Fetch ABAP objects
python3 skills/sap-adt-cli/scripts/sap_adt_cli.py get-class ZCL_MY_CLASS
python3 skills/sap-adt-cli/scripts/sap_adt_cli.py get-function BAPI_SALESORDER_CREATEFROMDAT2 --group BAPI_SD_SALESORDER
python3 skills/sap-adt-cli/scripts/sap_adt_cli.py search-object "ZCL_ORDER*"

# Install Python deps manually
pip install -r skills/sap-adt-cli/scripts/requirements.txt
```

## CONVENTIONS
- **SAP object names ALWAYS UPPERCASE** — `VBAK` not `vbak`, `ZCL_MY_CLASS` not `zcl_my_class`
- All stdout = data output; all errors → stderr + `sys.exit(1)`
- Credentials stored in `~/.sap-adt-cli/config.json` (0600 perms, plain text)
- Env vars (`SAP_URL`, `SAP_USERNAME`, `SAP_PASSWORD`, `SAP_CLIENT`) override config file
- Pass passwords via env var (`SAP_PASSWORD=...`), NOT `--password` flag (shell history risk)
- Dependencies (click, requests, urllib3) auto-install on first run via `_ensure_deps()`

## ANTI-PATTERNS
- Never pass `--password` on command line — exposes in shell history and `ps`
- Never commit `~/.sap-adt-cli/config.json` — gitignore already excludes it
- Do NOT import `lib.*` from outside `scripts/` — `sys.path.insert` in entry point makes it work only from that dir

## NOTES
- No tests, no CI, no pyproject.toml — intentional minimal footprint for agent skill use
- NOT a pip-installable package; invoke directly with `python3 path/to/sap_adt_cli.py`
- `get-type-info` tries domain first, falls back to data element silently
- HTTP session is module-level (not thread-safe — single invocation only)
- AI agent installation path: `~/.agents/skills/sap-adt-cli/` (symlink or Windows junction)
