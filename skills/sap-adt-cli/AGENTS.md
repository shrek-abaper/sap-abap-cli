# SKILL PACKAGE: sap-adt-cli

## OVERVIEW
Self-contained AI agent skill. `SKILL.md` = agent discovery metadata. `scripts/` = Python implementation. `references/` = upstream API docs.

## STRUCTURE
```
sap-adt-cli/
├── SKILL.md           # Agent framework integration spec (name, description, trigger conditions)
├── scripts/
│   ├── sap_adt_cli.py   # CLI entry point — Click @cli.command definitions only
│   ├── requirements.txt  # click>=8.1.0, requests>=2.31.0, urllib3>=2.0.0
│   └── lib/              # Core library (see lib/AGENTS.md)
└── references/
    └── adt_api.md        # ADT REST endpoint reference — read before adding new handlers
```

## WHERE TO LOOK
| Task | File |
|------|------|
| Add new SAP object command | `handlers.py` (logic) + `sap_adt_cli.py` (Click wrapper) |
| Change agent trigger description | `SKILL.md` frontmatter `description:` field |
| ADT URL patterns for new object types | `references/adt_api.md` |
| Credential flow / config file location | `lib/config.py` |

## CONVENTIONS
- `sap_adt_cli.py` is a thin Click shell — no business logic, just `_output(handlers.xxx())` calls
- Every handler returns `AdtResult(text, is_error)` — never raises, never prints directly
- New commands: add handler in `lib/handlers.py` → add `@cli.command` in `sap_adt_cli.py` → document in `SKILL.md`
- Output format by command type: source code → plain text, DDIC/search/transaction → raw XML, `get-package` → JSON

## ANTI-PATTERNS
- Do NOT add business logic to `sap_adt_cli.py` Click commands — logic goes in `handlers.py`
- Do NOT call `sys.exit()` from `lib/` — only entry point does that via `_output()`
- Do NOT add new dependencies without updating `requirements.txt`
