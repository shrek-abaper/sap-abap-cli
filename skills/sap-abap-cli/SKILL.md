---
name: sap-abap-cli
description: "Read ABAP source code and metadata from SAP systems via the ADT (ABAP Development Tools) REST API. Use when the user asks to read, view, or analyze ABAP programs, classes, function modules, function groups, interfaces, includes, DDIC tables, structures, data elements, domains, transactions, or packages. Also handles searching for ABAP objects by name. On first use, guides the user through SAP credential setup interactively."
---

# SAP ABAP CLI Skill

Read ABAP source code and metadata from SAP via `scripts/sap_abap_cli.py`.

## CLI Location

The CLI is `scripts/sap_abap_cli.py` inside this skill's directory.
Resolve the skill directory at runtime using the skill tool's path, then build the CLI path:

```bash
SKILL_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]:-$0}")")"
SAP_CLI="$SKILL_DIR/scripts/sap_abap_cli.py"
python3 "$SAP_CLI" <command> [args]
```

If you already know the absolute path to the skill directory (e.g. from the skill loader), use it directly:

```bash
SAP_CLI="/home/user/.agents/skills/sap-abap-cli/scripts/sap_abap_cli.py"
python3 "$SAP_CLI" <command> [args]
```

First run auto-installs `click`, `requests`, and `urllib3`. All source code output goes to stdout. Errors go to stderr with exit code 1.

## CRITICAL: Credential Check Before First Command

**Always run this before the first ABAP query in a session:**

```bash
python3 "$SAP_CLI" status
```

### Credentials configured → proceed

Output example:
```
URL:      https://my-sap.example.com:8000
Username: DEVELOPER
Client:   100
Language: EN
SSL:      verify
```

### Credentials NOT configured → collect and save non-interactively

You will see:
```
Not configured. Run: python3 sap_abap_cli.py configure
```

Or any ABAP command will print to stderr:
```
SAP credentials not configured.
...
```

**Ask the user for credentials** using the `question` tool — one question per field:

```
1. SAP System URL   — e.g. https://my-sap.example.com:8000  (include port)
2. SAP Username     — dialog user, e.g. DEVELOPER
3. SAP Password     — SAP logon password
4. SAP Client       — 3-digit number, e.g. 100
5. Skip SSL check?  — yes/no  (yes = self-signed / internal systems, no = production with valid cert)
```

**After collecting all answers, save with a single non-interactive command:**

```bash
python3 "$SAP_CLI" configure \
  --url      "https://my-sap.example.com:8000" \
  --username "DEVELOPER" \
  --client   "100" \
  --language "EN"
  # add --no-verify-ssl if user said yes to skipping SSL
```

Pass the password via environment variable to avoid shell history exposure:

```bash
SAP_PASSWORD="mysecret" python3 "$SAP_CLI" configure \
  --url "https://my-sap.example.com:8000" \
  --username "DEVELOPER" \
  --client "100"
```

Then verify:

```bash
python3 "$SAP_CLI" status
```

Credentials are saved to `~/.sap-abap-cli/config.json` (permissions 0600) and reused in all future sessions.

> **Security note:** inform the user that credentials are stored in plain text in `~/.sap-abap-cli/config.json`.
> The file is protected with `0600` permissions but is not encrypted.

**Alternative — env vars per invocation** (no file written, useful for one-off sessions):

```bash
SAP_URL="https://..." SAP_USERNAME="USER" SAP_PASSWORD="pass" SAP_CLIENT="100" python3 "$SAP_CLI" status
```

Env vars take precedence over the saved config file.

---

## Commands Quick Reference

| Command | Usage | Description |
|---------|-------|-------------|
| `configure` | `configure` | Interactive credential setup wizard |
| `status` | `status` | Show current connection config |
| `get-program` | `get-program <NAME>` | ABAP program (report) source code |
| `get-class` | `get-class <NAME>` | ABAP class source code |
| `get-function-group` | `get-function-group <NAME>` | Function group top-include source |
| `get-function` | `get-function <NAME> --group <FG>` | Function module source code |
| `get-include` | `get-include <NAME>` | ABAP include source code |
| `get-interface` | `get-interface <NAME>` | ABAP interface source code |
| `get-table` | `get-table <NAME>` | DDIC table field definitions |
| `get-structure` | `get-structure <NAME>` | DDIC structure definition |
| `get-type-info` | `get-type-info <NAME>` | Domain or data element (tries domain first) |
| `get-package` | `get-package <NAME>` | Package object list → JSON array |
| `get-transaction` | `get-transaction <NAME>` | Transaction properties/package info |
| `get-table-contents` | `get-table-contents <NAME> [--max-rows N]` | Table row data (needs custom service) |
| `search-object` | `search-object <QUERY> [--max-results N]` | Quick object search (`*` wildcard) |

---

## Usage Examples

```bash
SAP_CLI="<skill_dir>/scripts/sap_abap_cli.py"

# Source code
python3 "$SAP_CLI" get-program SAPMV45A
python3 "$SAP_CLI" get-class ZCL_MY_CLASS
python3 "$SAP_CLI" get-function BAPI_SALESORDER_CREATEFROMDAT2 --group BAPI_SD_SALESORDER
python3 "$SAP_CLI" get-include MV45AFZZ
python3 "$SAP_CLI" get-interface ZIF_MY_INTERFACE

# Dictionary
python3 "$SAP_CLI" get-table VBAK
python3 "$SAP_CLI" get-structure VBAKKOM
python3 "$SAP_CLI" get-type-info MATNR

# Discovery
python3 "$SAP_CLI" search-object "ZCL_*" --max-results 20
python3 "$SAP_CLI" get-package ZMYPACKAGE
python3 "$SAP_CLI" get-transaction VA01

# Table contents (requires custom SAP service)
python3 "$SAP_CLI" get-table-contents T001 --max-rows 50
```

---

## Key Behaviors & Gotchas

- **Object names**: SAP names are case-insensitive but always use **UPPERCASE** for reliability (e.g. `VBAK`, `ZCL_MY_CLASS`, not `vbak`)
- **Source output**: `get-program`, `get-class`, `get-function`, etc. return raw ABAP source text
- **XML output**: `get-table`, `get-structure`, `get-type-info`, `get-transaction`, `search-object` return raw XML from ADT — parse it or read it as-is
- **JSON output**: `get-package` is the only command that returns a parsed JSON array
- **`get-type-info` fallback**: tries domain first; if not found, falls back to data element
- **`get-table-contents`**: requires a custom REST service `/z_mcp_abap_adt/z_tablecontent` deployed in the SAP system — if it returns HTTP 404, the service is not installed; use `get-table` for structure instead
- **SSL**: for internal SAP systems with self-signed certs, configure with SSL disabled (`SAP_VERIFY_SSL=0` or answer "n" in wizard)
- **Session reuse**: the HTTP session is reused within a single script invocation; each `python3 "$SAP_CLI" ...` call starts fresh
- **Credentials precedence**: env vars > `~/.sap-abap-cli/config.json`

---

## Output Format

| Command | Output Format |
|---------|---------------|
| Source code commands | Plain text ABAP source |
| `get-table`, `get-structure`, `get-type-info`, `get-transaction`, `search-object` | Raw XML |
| `get-package` | JSON array of `{OBJECT_TYPE, OBJECT_NAME, OBJECT_DESCRIPTION, OBJECT_URI}` |
| `status` | Plain text key-value pairs |

---

## Error Handling

| Error Output | Cause | Action |
|--------------|-------|--------|
| `Not configured` | No saved credentials | Guide user through `configure` |
| `HTTP 401` | Wrong username/password | Ask user to re-run `configure` |
| `HTTP 403` | Missing ADT authorization | User needs `SAP_ADT_BASE` role or equivalent |
| `HTTP 404` | Object name not found | Try `search-object` to find the correct name |
| `HTTP 503` | ADT service not active | SAP Basis must activate `/sap/bc/adt` in transaction SICF |
| SSL error | Certificate issue | Re-configure with `SAP_VERIFY_SSL=0` |

---

## Workflows

**Read an unknown class:**
```bash
python3 "$SAP_CLI" search-object "ZCL_ORDER*"
python3 "$SAP_CLI" get-class ZCL_ORDER_HANDLER
```

**Explore a package:**
```bash
python3 "$SAP_CLI" get-package ZMYPACKAGE
# → JSON list of all objects; pick the ones you need
python3 "$SAP_CLI" get-program ZMYREPORT
python3 "$SAP_CLI" get-class ZCL_MYCLASS
```

**Look up a BAPI signature:**
```bash
python3 "$SAP_CLI" get-function BAPI_SALESORDER_CREATEFROMDAT2 --group BAPI_SD_SALESORDER
```

**Understand a table structure:**
```bash
python3 "$SAP_CLI" get-table VBAK
python3 "$SAP_CLI" get-type-info VBELN   # look up field type
```

**Find a transaction's package/application:**
```bash
python3 "$SAP_CLI" get-transaction VA01
```

---

## SAP Prerequisites

- ADT services active: transaction `SICF` → path `/sap/bc/adt` → Activate
- User authorization: role `SAP_ADT_BASE` or objects `S_ADT_RES`, `S_RFC`
- `get-table-contents` additionally needs custom service `/z_mcp_abap_adt/z_tablecontent`
  (see [original project](https://github.com/mario-andreschak/mcp-abap-adt) for setup)
