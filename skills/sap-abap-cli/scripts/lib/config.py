import json
import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".sap-abap-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"

SETUP_GUIDE = """\
SAP credentials not configured.

To set up your SAP connection, run:
  python3 sap_abap_cli.py configure

Or set environment variables:
  SAP_URL        - SAP system URL (e.g. https://my-sap.example.com:8000)
  SAP_USERNAME   - SAP username
  SAP_PASSWORD   - SAP password
  SAP_CLIENT     - SAP client number (e.g. 100)

Optional:
  SAP_LANGUAGE   - Language code (default: EN)
  SAP_VERIFY_SSL - Set to 0 to disable SSL verification (default: 1)
"""


@dataclass
class SapConfig:
    url: str
    username: str
    password: str
    client: str
    language: str = "EN"
    verify_ssl: bool = True

    def base_url(self) -> str:
        from urllib.parse import urlparse
        parsed = urlparse(self.url.rstrip("/"))
        return f"{parsed.scheme}://{parsed.netloc}"


def load_config() -> Optional[SapConfig]:
    url = os.getenv("SAP_URL")
    username = os.getenv("SAP_USERNAME")
    password = os.getenv("SAP_PASSWORD")
    client = os.getenv("SAP_CLIENT")

    if url and username and password and client:
        return SapConfig(
            url=url,
            username=username,
            password=password,
            client=client,
            language=os.getenv("SAP_LANGUAGE", "EN"),
            verify_ssl=os.getenv("SAP_VERIFY_SSL", "1") != "0",
        )

    if not CONFIG_FILE.exists():
        return None

    try:
        with open(CONFIG_FILE) as f:
            data = json.load(f)
        return SapConfig(
            url=data["url"],
            username=data["username"],
            password=data["password"],
            client=data["client"],
            language=data.get("language", "EN"),
            verify_ssl=data.get("verify_ssl", True),
        )
    except (json.JSONDecodeError, KeyError):
        return None


def save_config(config: SapConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(asdict(config), f, indent=2)
    CONFIG_FILE.chmod(0o600)


def get_config() -> SapConfig:
    config = load_config()
    if config is None:
        print(SETUP_GUIDE, file=sys.stderr)
        sys.exit(1)
    return config


def save_config_from_flags(
    url: Optional[str],
    username: Optional[str],
    password: Optional[str],
    client: Optional[str],
    language: Optional[str] = None,
    verify_ssl: bool = True,
) -> SapConfig:
    existing = load_config()
    resolved_url = url or getattr(existing, "url", None)
    resolved_username = username or getattr(existing, "username", None)
    resolved_password = password or getattr(existing, "password", None)
    resolved_client = client or getattr(existing, "client", None)
    resolved_language = language or getattr(existing, "language", None) or "EN"

    missing = [name for name, val in [
        ("--url", resolved_url),
        ("--username", resolved_username),
        ("--password", resolved_password),
        ("--client", resolved_client),
    ] if not val]

    if missing:
        print(f"Error: missing required fields: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    config = SapConfig(
        url=resolved_url,
        username=resolved_username,
        password=resolved_password,
        client=resolved_client,
        language=resolved_language,
        verify_ssl=verify_ssl,
    )
    save_config(config)
    print(f"Configuration saved to {CONFIG_FILE}")
    print("Warning: credentials are stored in plain text. Ensure this file remains private (permissions: 600).")
    return config


def run_configure_wizard() -> SapConfig:
    existing = load_config()

    def _prompt(label: str, default: Optional[str] = None, secret: bool = False) -> str:
        hint = f" [{default}]" if default else ""
        prompt_text = f"{label}{hint}: "
        if secret:
            import getpass
            value = getpass.getpass(prompt_text)
        else:
            value = input(prompt_text)
        return value.strip() or (default or "")

    print("\nSAP ABAP CLI — Connection Setup")
    print("=" * 40)

    url = _prompt("SAP System URL (e.g. https://my-sap.example.com:8000)", getattr(existing, "url", None))
    username = _prompt("SAP Username", getattr(existing, "username", None))
    password = _prompt("SAP Password", secret=True)
    client = _prompt("SAP Client (e.g. 100)", getattr(existing, "client", None))
    language = _prompt("Language code", getattr(existing, "language", "EN") or "EN")
    verify_ssl_raw = _prompt(
        "Verify SSL certificate? (y/n)",
        "y" if getattr(existing, "verify_ssl", True) else "n",
    )
    verify_ssl = verify_ssl_raw.lower() not in ("n", "no", "0", "false")

    config = SapConfig(
        url=url,
        username=username,
        password=password,
        client=client,
        language=language or "EN",
        verify_ssl=verify_ssl,
    )
    save_config(config)
    print(f"\nConfiguration saved to {CONFIG_FILE}")
    return config
