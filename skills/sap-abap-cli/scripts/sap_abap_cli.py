#!/usr/bin/env python3
import importlib.util
import os
import subprocess
import sys

_SKILL_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def _ensure_deps():
    deps = [
        ("click",    "click>=8.1.0"),
        ("requests", "requests>=2.31.0"),
        ("urllib3",  "urllib3>=2.0.0"),
    ]
    missing = [pip_spec for mod_name, pip_spec in deps if not importlib.util.find_spec(mod_name)]
    if not missing:
        return
    print(f"[setup] Installing missing packages: {', '.join(missing)}", file=sys.stderr)
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet"] + missing,
        check=True,
    )
    print("[setup] Done.", file=sys.stderr)


_ensure_deps()

sys.path.insert(0, _SKILL_SCRIPTS_DIR)

import click
from lib.config import run_configure_wizard, save_config_from_flags, load_config, CONFIG_FILE, SapConfig
from lib import handlers

__version__ = "1.0.0"


def _output(result) -> None:
    if result.is_error:
        click.echo(result.text, err=True)
        sys.exit(1)
    click.echo(result.text)


@click.group()
@click.version_option(version=__version__, prog_name="sap-abap-cli")
def cli():
    """Read ABAP source code and metadata from SAP systems via the ADT REST API.

    Credentials are loaded from environment variables (SAP_URL, SAP_USERNAME,
    SAP_PASSWORD, SAP_CLIENT) or from ~/.sap-abap-cli/config.json.

    Run 'configure' on first use to save your connection settings.
    """


@cli.command()
@click.option("--url",           default=None, help="SAP system URL (e.g. https://my-sap.example.com:8000)")
@click.option("--username",      default=None, help="SAP username")
@click.option("--password",      default=None, help="SAP password (see security warning below)")
@click.option("--client",        default=None, help="SAP client number (e.g. 100)")
@click.option("--language",      default=None, help="Language code (default: EN)")
@click.option("--no-verify-ssl", is_flag=True, default=False, help="Disable SSL certificate verification")
def configure(url, username, password, client, language, no_verify_ssl):
    """Save SAP connection credentials.

    When called with flags the credentials are saved non-interactively —
    useful for agent workflows. When called with no flags an interactive
    wizard is launched instead (recommended for human use in a terminal,
    as it avoids exposing the password in shell history).

    Security note: passing --password on the command line may expose it in
    shell history and process listings. Prefer the interactive wizard or
    the SAP_PASSWORD environment variable.
    """
    if any([url, username, password, client]):
        if password:
            click.echo(
                "Warning: passing --password on the command line may expose it in shell history "
                "and process listings. Consider using the interactive wizard (no flags) or "
                "the SAP_PASSWORD environment variable instead.",
                err=True,
            )
        save_config_from_flags(
            url=url,
            username=username,
            password=password,
            client=client,
            language=language,
            verify_ssl=not no_verify_ssl,
        )
    else:
        run_configure_wizard()


@cli.command()
def status():
    """Show the current SAP connection configuration."""
    config = load_config()
    if config is None:
        click.echo("Not configured. Run: sap_abap_cli.py configure", err=True)
        sys.exit(1)
    click.echo(f"URL:      {config.url}")
    click.echo(f"Username: {config.username}")
    click.echo(f"Client:   {config.client}")
    click.echo(f"Language: {config.language}")
    click.echo(f"SSL:      {'verify' if config.verify_ssl else 'skip (self-signed allowed)'}")
    click.echo(f"Config:   {CONFIG_FILE}")


@cli.command("get-program")
@click.argument("program_name")
def get_program(program_name):
    """Retrieve ABAP program (report) source code.

    PROGRAM_NAME is the ABAP object name, e.g. SAPMV45A or ZMYREPORT.
    Names are case-insensitive; uppercase is recommended.
    """
    _output(handlers.get_program(program_name))


@cli.command("get-class")
@click.argument("class_name")
def get_class(class_name):
    """Retrieve ABAP class source code.

    CLASS_NAME is the class name, e.g. ZCL_MY_CLASS or CL_SALV_TABLE.
    """
    _output(handlers.get_class(class_name))


@cli.command("get-function-group")
@click.argument("function_group")
def get_function_group(function_group):
    """Retrieve ABAP function group top-include source code.

    FUNCTION_GROUP is the function group name, e.g. BAPI_SD_SALESORDER.
    Use get-function to retrieve a specific function module within the group.
    """
    _output(handlers.get_function_group(function_group))


@cli.command("get-function")
@click.argument("function_name")
@click.option("--group", required=True, help="Function group that contains the function module")
def get_function(function_name, group):
    """Retrieve ABAP function module source code.

    FUNCTION_NAME is the function module name,
    e.g. BAPI_SALESORDER_CREATEFROMDAT2.

    --group is required and must be the parent function group name,
    e.g. BAPI_SD_SALESORDER.
    """
    _output(handlers.get_function(function_name, group))


@cli.command("get-structure")
@click.argument("structure_name")
def get_structure(structure_name):
    """Retrieve ABAP DDIC structure definition.

    STRUCTURE_NAME is the dictionary structure name, e.g. VBAKKOM.
    Returns the field list in XML format.
    """
    _output(handlers.get_structure(structure_name))


@cli.command("get-table")
@click.argument("table_name")
def get_table(table_name):
    """Retrieve ABAP DDIC transparent table field definitions.

    TABLE_NAME is the dictionary table name, e.g. VBAK or MARA.
    Returns the field list in XML format.
    Use get-table-contents to read actual table row data.
    """
    _output(handlers.get_table(table_name))


@cli.command("get-table-contents")
@click.argument("table_name")
@click.option("--max-rows", default=100, show_default=True, help="Maximum number of rows to return")
def get_table_contents(table_name, max_rows):
    """Retrieve rows from a DDIC transparent table.

    TABLE_NAME is the dictionary table name, e.g. T001.

    Requires the custom REST service /z_mcp_abap_adt/z_tablecontent to be
    deployed and active in the target SAP system (transaction SICF).
    Returns HTTP 404 if the service is not installed — use get-table for
    structure information instead.
    """
    _output(handlers.get_table_contents(table_name, max_rows))


@cli.command("get-package")
@click.argument("package_name")
def get_package(package_name):
    """List all objects in an ABAP package.

    PACKAGE_NAME is the development package name, e.g. ZMYPACKAGE.
    Returns a JSON array of objects with keys:
    OBJECT_TYPE, OBJECT_NAME, OBJECT_DESCRIPTION, OBJECT_URI.
    """
    _output(handlers.get_package(package_name))


@cli.command("get-type-info")
@click.argument("type_name")
def get_type_info(type_name):
    """Retrieve domain or data element information from DDIC.

    TYPE_NAME is the domain or data element name, e.g. MATNR or BUKRS.
    Tries domain first; falls back to data element if not found.
    Returns XML.
    """
    _output(handlers.get_type_info(type_name))


@cli.command("get-include")
@click.argument("include_name")
def get_include(include_name):
    """Retrieve ABAP include source code.

    INCLUDE_NAME is the include program name, e.g. MV45AFZZ or LZMY_TOPINC.
    """
    _output(handlers.get_include(include_name))


@cli.command("get-interface")
@click.argument("interface_name")
def get_interface(interface_name):
    """Retrieve ABAP interface source code.

    INTERFACE_NAME is the interface name, e.g. ZIF_MY_INTERFACE or IF_SALV_MODEL.
    """
    _output(handlers.get_interface(interface_name))


@cli.command("get-transaction")
@click.argument("transaction_name")
def get_transaction(transaction_name):
    """Retrieve transaction properties (package, application component).

    TRANSACTION_NAME is the transaction code, e.g. VA01 or MM60.
    Returns XML with package and application component information.
    """
    _output(handlers.get_transaction(transaction_name))


@cli.command("search-object")
@click.argument("query")
@click.option("--max-results", default=100, show_default=True, help="Maximum number of results to return")
def search_object(query, max_results):
    """Search for ABAP objects by name (supports * wildcard).

    QUERY is a name pattern, e.g. ZCL_ORDER* or BAPI_SALES*.
    Returns XML with matching object names, types, and URIs.

    Examples:
      search-object "ZCL_*"
      search-object "BAPI_SALESORDER*" --max-results 20
    """
    _output(handlers.search_object(query, max_results))


if __name__ == "__main__":
    cli()
