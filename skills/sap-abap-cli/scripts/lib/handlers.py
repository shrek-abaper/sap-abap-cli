import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from urllib.parse import quote

import requests

from .client import make_adt_request
from .config import get_config


@dataclass
class AdtResult:
    text: str
    is_error: bool = False


def _base() -> str:
    return get_config().base_url()


def _enc(name: str) -> str:
    return quote(name, safe="")


def _ok(resp: requests.Response) -> AdtResult:
    return AdtResult(text=resp.text)


def _err(exc: Exception) -> AdtResult:
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        return AdtResult(
            text=f"HTTP {exc.response.status_code}: {exc.response.text or str(exc)}",
            is_error=True,
        )
    return AdtResult(text=str(exc), is_error=True)


def get_program(program_name: str) -> AdtResult:
    try:
        return _ok(make_adt_request(f"{_base()}/sap/bc/adt/programs/programs/{_enc(program_name)}/source/main"))
    except Exception as e:
        return _err(e)


def get_class(class_name: str) -> AdtResult:
    try:
        return _ok(make_adt_request(f"{_base()}/sap/bc/adt/oo/classes/{_enc(class_name)}/source/main"))
    except Exception as e:
        return _err(e)


def get_function_group(function_group: str) -> AdtResult:
    try:
        return _ok(make_adt_request(f"{_base()}/sap/bc/adt/functions/groups/{_enc(function_group)}/source/main"))
    except Exception as e:
        return _err(e)


def get_function(function_name: str, function_group: str) -> AdtResult:
    try:
        url = (
            f"{_base()}/sap/bc/adt/functions/groups/{_enc(function_group)}"
            f"/fmodules/{_enc(function_name)}/source/main"
        )
        return _ok(make_adt_request(url))
    except Exception as e:
        return _err(e)


def get_structure(structure_name: str) -> AdtResult:
    try:
        return _ok(make_adt_request(f"{_base()}/sap/bc/adt/ddic/structures/{_enc(structure_name)}/source/main"))
    except Exception as e:
        return _err(e)


def get_table(table_name: str) -> AdtResult:
    try:
        return _ok(make_adt_request(f"{_base()}/sap/bc/adt/ddic/tables/{_enc(table_name)}/source/main"))
    except Exception as e:
        return _err(e)


def get_table_contents(table_name: str, max_rows: int = 100) -> AdtResult:
    try:
        url = f"{_base()}/z_sap_abap_cli/z_tablecontent/{_enc(table_name)}?maxRows={max_rows}"
        return _ok(make_adt_request(url))
    except Exception as e:
        return _err(e)


def get_package(package_name: str) -> AdtResult:
    try:
        resp = make_adt_request(
            f"{_base()}/sap/bc/adt/repository/nodestructure",
            method="POST",
            params={
                "parent_type": "DEVC/K",
                "parent_name": _enc(package_name),
                "withShortDescriptions": "true",
            },
        )
        root = ET.fromstring(resp.text)
        ns_obj = "{http://www.sap.com/abapxml}"
        items = []
        for node in root.findall(f".//{ns_obj}SEU_ADT_REPOSITORY_OBJ_NODE"):
            name_el = node.find(f"{ns_obj}OBJECT_NAME")
            uri_el = node.find(f"{ns_obj}OBJECT_URI")
            if name_el is None or uri_el is None:
                continue
            type_el = node.find(f"{ns_obj}OBJECT_TYPE")
            desc_el = node.find(f"{ns_obj}DESCRIPTION")
            items.append({
                "OBJECT_TYPE": type_el.text if type_el is not None else "",
                "OBJECT_NAME": name_el.text,
                "OBJECT_DESCRIPTION": desc_el.text if desc_el is not None else "",
                "OBJECT_URI": uri_el.text,
            })
        return AdtResult(text=json.dumps(items, indent=2))
    except Exception as e:
        return _err(e)


def get_type_info(type_name: str) -> AdtResult:
    try:
        return _ok(make_adt_request(f"{_base()}/sap/bc/adt/ddic/domains/{_enc(type_name)}/source/main"))
    except Exception:
        pass
    try:
        return _ok(make_adt_request(f"{_base()}/sap/bc/adt/ddic/dataelements/{_enc(type_name)}"))
    except Exception as e:
        return _err(e)


def get_include(include_name: str) -> AdtResult:
    try:
        return _ok(make_adt_request(f"{_base()}/sap/bc/adt/programs/includes/{_enc(include_name)}/source/main"))
    except Exception as e:
        return _err(e)


def get_interface(interface_name: str) -> AdtResult:
    try:
        return _ok(make_adt_request(f"{_base()}/sap/bc/adt/oo/interfaces/{_enc(interface_name)}/source/main"))
    except Exception as e:
        return _err(e)


def get_transaction(transaction_name: str) -> AdtResult:
    try:
        url = (
            f"{_base()}/sap/bc/adt/repository/informationsystem/objectproperties/values"
            f"?uri=%2Fsap%2Fbc%2Fadt%2Fvit%2Fwb%2Fobject_type%2Ftrant%2Fobject_name%2F{_enc(transaction_name)}"
            f"&facet=package&facet=appl"
        )
        return _ok(make_adt_request(url))
    except Exception as e:
        return _err(e)


def search_object(query: str, max_results: int = 100) -> AdtResult:
    try:
        url = (
            f"{_base()}/sap/bc/adt/repository/informationsystem/search"
            f"?operation=quickSearch&query={_enc(query)}&maxResults={max_results}"
        )
        return _ok(make_adt_request(url))
    except Exception as e:
        return _err(e)
