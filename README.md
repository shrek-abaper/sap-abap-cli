# sap-abap-cli

A command-line tool and AI agent skill for reading ABAP source code and metadata
from SAP systems via the [ADT (ABAP Development Tools) REST API](https://help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/about-abap-development-tools).

Supports programs, classes, function modules, interfaces, includes, DDIC objects,
packages, transactions, and object search — all from the terminal or from within
an AI agent workflow.

---

## Requirements

- Python 3.8+
- A SAP system (on-premise ECC / S/4HANA, or BTP ABAP) with ADT services activated
- A SAP dialog user with the `SAP_ADT_BASE` role (or equivalent)

Dependencies (`click`, `requests`, `urllib3`) are installed automatically on first run.

---

## Quickstart

```bash
# 1. Clone the repository
git clone https://github.com/your-org/sap-abap-cli
cd sap-abap-cli

# 2. Configure credentials (interactive wizard — password is not echoed)
python3 scripts/sap_abap_cli.py configure

# 3. Verify the connection
python3 scripts/sap_abap_cli.py status

# 4. Start reading ABAP objects
python3 scripts/sap_abap_cli.py get-program SAPMV45A
python3 scripts/sap_abap_cli.py get-class ZCL_MY_CLASS
python3 scripts/sap_abap_cli.py get-function BAPI_SALESORDER_CREATEFROMDAT2 --group BAPI_SD_SALESORDER
```

---

## Configuration

### Interactive wizard (recommended)

```bash
python3 scripts/sap_abap_cli.py configure
```

Credentials are saved to `~/.sap-abap-cli/config.json` with `0600` permissions.

> **Security note:** The config file stores credentials in plain text.
> Do not commit it to version control and restrict access to the file accordingly.

### Environment variables

Useful for CI/CD pipelines or one-off sessions. Environment variables take
precedence over the saved config file.

```bash
export SAP_URL=https://my-sap.example.com:8000
export SAP_USERNAME=MYUSER
export SAP_PASSWORD=secret          # prefer this over the --password flag
export SAP_CLIENT=100
export SAP_LANGUAGE=EN              # optional, default: EN
export SAP_VERIFY_SSL=0             # optional: set 0 for self-signed certificates
```

### Non-interactive flags (agent / automation workflows)

```bash
# Pass password via environment variable to avoid shell history exposure
SAP_PASSWORD="secret" python3 scripts/sap_abap_cli.py configure \
  --url      "https://my-sap.example.com:8000" \
  --username "MYUSER" \
  --client   "100"
```

---

## Commands

| Command | Description |
|---------|-------------|
| `configure` | Save connection credentials |
| `status` | Show current connection configuration |
| `get-program <NAME>` | ABAP program / report source code |
| `get-class <NAME>` | ABAP class source code |
| `get-function-group <NAME>` | Function group top-include source code |
| `get-function <NAME> --group <FG>` | Function module source code |
| `get-include <NAME>` | ABAP include source code |
| `get-interface <NAME>` | ABAP interface source code |
| `get-table <NAME>` | DDIC table field definitions (XML) |
| `get-structure <NAME>` | DDIC structure definition (XML) |
| `get-type-info <NAME>` | Domain or data element info (XML) |
| `get-package <NAME>` | Package object list (JSON) |
| `get-transaction <NAME>` | Transaction properties / package (XML) |
| `get-table-contents <NAME> [--max-rows N]` | Table row data *(requires custom service)* |
| `search-object <QUERY> [--max-results N]` | Object name search — `*` wildcard supported |

Run any command with `--help` for full details.

---

## Examples

```bash
CLI="scripts/sap_abap_cli.py"

# Source code
python3 $CLI get-program SAPMV45A
python3 $CLI get-class ZCL_MY_CLASS
python3 $CLI get-function BAPI_SALESORDER_CREATEFROMDAT2 --group BAPI_SD_SALESORDER
python3 $CLI get-include MV45AFZZ
python3 $CLI get-interface ZIF_MY_INTERFACE

# Dictionary objects
python3 $CLI get-table VBAK
python3 $CLI get-structure VBAKKOM
python3 $CLI get-type-info MATNR

# Discovery
python3 $CLI search-object "ZCL_ORDER*" --max-results 20
python3 $CLI get-package ZMYPACKAGE
python3 $CLI get-transaction VA01

# Table data (requires custom SAP service — see Prerequisites)
python3 $CLI get-table-contents T001 --max-rows 50
```

---

## SAP Prerequisites

### 1. Activate ADT services

In transaction `SICF`, activate the service tree at:
```
/sap/bc/adt
```

### 2. Assign user authorization

Assign the role `SAP_ADT_BASE` to the SAP user, or manually grant:
- `S_ADT_RES` — ADT resource access
- `S_RFC` — Remote function call access for ADT function groups

### 3. (Optional) Custom table content service

`get-table-contents` requires the custom REST service
`/z_mcp_abap_adt/z_tablecontent` deployed in the target SAP system.
All other commands work without it.

---

## Output Formats

| Commands | Output |
|----------|--------|
| Source code commands | Plain text ABAP source |
| `get-table`, `get-structure`, `get-type-info`, `get-transaction`, `search-object` | Raw ADT XML |
| `get-package` | JSON array |
| `status` | Plain text key-value pairs |

All output is written to **stdout**. Errors are written to **stderr** with a non-zero exit code.

---

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `Not configured` | No credentials saved | Run `configure` |
| `HTTP 401` | Wrong username or password | Re-run `configure` |
| `HTTP 403` | Missing `SAP_ADT_BASE` role | Ask Basis to assign authorization |
| `HTTP 404` | Object name not found | Try `search-object` to find the correct name |
| `HTTP 503` | `/sap/bc/adt` not active | Ask Basis to activate in `SICF` |
| SSL error | Self-signed certificate | Re-configure with `SAP_VERIFY_SSL=0` |

---

## Security Considerations

- Credentials are stored **in plain text** in `~/.sap-abap-cli/config.json` (permissions `0600`).
  This is consistent with common CLI tools (AWS CLI, Azure CLI). Restrict file access accordingly.
- Avoid passing passwords via `--password` — they appear in shell history and `ps` output.
  Prefer the interactive `configure` wizard or the `SAP_PASSWORD` environment variable.
- For shared or CI environments, use short-lived credentials and rotate them regularly.

---

## License

[MIT](LICENSE)
