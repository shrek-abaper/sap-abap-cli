# LIB: Core Library

## OVERVIEW
Three-layer library: `config.py` (credentials) → `client.py` (HTTP) → `handlers.py` (SAP object fetchers).

## LAYERS
| File | Responsibility | Key exports |
|------|----------------|-------------|
| `config.py` | Load/save/validate SAP credentials | `SapConfig`, `get_config()`, `load_config()`, `save_config()`, `run_configure_wizard()`, `save_config_from_flags()` |
| `client.py` | HTTP session, auth, CSRF token | `make_adt_request(url, method, ...)` |
| `handlers.py` | One function per SAP object type | `get_program()`, `get_class()`, `get_function()`, etc. — all return `AdtResult` |

## KEY TYPES
```python
@dataclass
class SapConfig:
    url: str; username: str; password: str; client: str
    language: str = "EN"; verify_ssl: bool = True
    def base_url() -> str  # strips path, returns scheme://host:port

@dataclass
class AdtResult:
    text: str
    is_error: bool = False  # True = write to stderr + exit(1)
```

## CONVENTIONS
- `handlers.py`: every function is `try/except Exception → _err(e)` — never propagates
- `client.py`: CSRF token + session are module-level globals (not thread-safe, single-process only)
- CSRF token fetched lazily on first POST/PUT; auto-retried on 403+CSRF response
- URL encoding: always use `_enc(name)` = `quote(name, safe="")` for SAP object names
- Config resolution: env vars (`SAP_URL`, `SAP_USERNAME`, `SAP_PASSWORD`, `SAP_CLIENT`) win over `~/.sap-adt-cli/config.json`

## ADDING A NEW SAP OBJECT TYPE
1. Find ADT endpoint in `../references/adt_api.md`
2. Add handler in `handlers.py`: `def get_foo(name) -> AdtResult: try: return _ok(make_adt_request(...)) except Exception as e: return _err(e)`
3. Add `@cli.command` in `../sap_adt_cli.py` calling `_output(handlers.get_foo(name))`

## ANTI-PATTERNS
- Never call `sys.exit()` or `print()` from this lib — use `AdtResult(is_error=True)` only
- Never import from `sap_adt_cli.py` (circular) — lib is leaf layer
- `__init__.py` is empty — import modules directly (`from lib.config import ...`)
