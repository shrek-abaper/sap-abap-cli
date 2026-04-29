# SAP ADT REST API — Quick Reference

SAP ABAP Development Tools (ADT) exposes a REST API under `/sap/bc/adt/`.
Authentication is HTTP Basic Auth with the `X-SAP-Client` header for client selection.

## Authentication

Every request requires:

```
Authorization: Basic base64(username:password)
X-SAP-Client: <client_number>
```

For POST/PUT requests, first fetch a CSRF token:

```
GET <any ADT URL>
x-csrf-token: fetch
→ Response header: x-csrf-token: <token>

Then include in POST/PUT:
x-csrf-token: <token>
```

## Source Code Endpoints (Read)

| Object Type | Method | URL Pattern |
|-------------|--------|-------------|
| Program (report) | GET | `/sap/bc/adt/programs/programs/{name}/source/main` |
| Class | GET | `/sap/bc/adt/oo/classes/{name}/source/main` |
| Interface | GET | `/sap/bc/adt/oo/interfaces/{name}/source/main` |
| Function Group | GET | `/sap/bc/adt/functions/groups/{fg_name}/source/main` |
| Function Module | GET | `/sap/bc/adt/functions/groups/{fg_name}/fmodules/{fm_name}/source/main` |
| Include | GET | `/sap/bc/adt/programs/includes/{name}/source/main` |
| CDS View (DDL) | GET | `/sap/bc/adt/ddic/ddl/sources/{name}/source/main` |
| Type Group | GET | `/sap/bc/adt/typegroups/groups/{name}/source/main` |
| DDIC Table | GET | `/sap/bc/adt/ddic/tables/{name}/source/main` |
| DDIC Structure | GET | `/sap/bc/adt/ddic/structures/{name}/source/main` |
| Domain | GET | `/sap/bc/adt/ddic/domains/{name}/source/main` |
| Data Element | GET | `/sap/bc/adt/ddic/dataelements/{name}` |

Object names must be URL-encoded. Responses are plain text (ABAP source) or XML.

## Write Source — Lock / PUT / Unlock

Three-step flow; unlock must always run (use `finally`).

### 1. Lock

```
POST /sap/bc/adt/{object_uri}?method=lock
X-sap-adt-sessiontype: stateful
→ Response header: com.sap.adt.lock.handle: <handle>
```

If the header is absent, fall back to parsing `<handle>` or `<lockHandle>` from the XML response body.

### 2. Write (PUT)

```
PUT /sap/bc/adt/{object_uri}/source/main
Content-Type: text/plain; charset=utf-8
X-sap-adt-lock-handle: <handle>

[optional] ?sap-cts-request=<TRKORR>    ← assign to specific transport
```

Body: plain text ABAP source.

### 3. Unlock

```
POST /sap/bc/adt/{object_uri}?method=unlock
X-sap-adt-lock-handle: <handle>
```

## Activation

```
POST /sap/bc/adt/activation
Content-Type: application/vnd.sap.adt.activation.request+xml; charset=utf-8

<?xml version="1.0" encoding="utf-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:objectReference adtcore:uri="{object_uri}" adtcore:name="{OBJECT_NAME}"/>
</adtcore:objectReferences>
```

Response: empty (200) = success. Non-empty XML body = activation errors — parse `severity`, `text` attributes.

## Syntax Check

```
POST /sap/bc/adt/abapsource/syntaxcheck
Content-Type: application/vnd.sap.adt.abapsource.syntaxcheckresult+xml; charset=utf-8

<?xml version="1.0" encoding="utf-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:objectReference adtcore:uri="{object_uri}" adtcore:name="{OBJECT_NAME}"/>
</adtcore:objectReferences>
```

Response: XML with `severity` (`error`/`warning`/`info`), `text`, and `line` attributes. Empty body = no issues.

## Where-Used

```
GET /sap/bc/adt/repository/informationsystem/whereused
    ?uri=<full_object_url>        ← full URL including scheme+host
    &maxResults=50
Accept: application/vnd.sap.adt.repository.informationsystem.whereused+xml
```

Response: XML with `adtcore:objectReference` elements (namespace `http://www.sap.com/adt/core`), attributes: `adtcore:name`, `adtcore:type`, `adtcore:uri`.

## Open SQL Data Preview

```
GET /sap/bc/adt/datapreview/freestyle
    ?rowNumber=<max_rows>
    &sqlCommand=<url-encoded-SELECT>
Accept: application/xml
```

Response: XML with `<column name="...">` elements containing row data. Requires `/sap/bc/adt/datapreview` activated in SICF.

Only `SELECT` is valid. DML (`INSERT`, `UPDATE`, `DELETE`, `MERGE`, `MODIFY`, `TRUNCATE`) must be blocked at the CLI layer.

## Search

```
GET /sap/bc/adt/repository/informationsystem/search
    ?operation=quickSearch
    &query=<url-encoded-query>      ← supports * wildcard
    &maxResults=100
```

Response: XML with matching objects.

## Package Contents

```
POST /sap/bc/adt/repository/nodestructure
     ?parent_type=DEVC/K
     &parent_name=<url-encoded-package>
     &withShortDescriptions=true
```

Response: XML. Relevant nodes:
```xml
<SEU_ADT_REPOSITORY_OBJ_NODE>
  <OBJECT_TYPE>PROG</OBJECT_TYPE>
  <OBJECT_NAME>ZMYPROGRAM</OBJECT_NAME>
  <DESCRIPTION>My Program</DESCRIPTION>
  <OBJECT_URI>/sap/bc/adt/programs/programs/ZMYPROGRAM</OBJECT_URI>
</SEU_ADT_REPOSITORY_OBJ_NODE>
```

## Transaction Properties

```
GET /sap/bc/adt/repository/informationsystem/objectproperties/values
    ?uri=%2Fsap%2Fbc%2Fadt%2Fvit%2Fwb%2Fobject_type%2Ftrant%2Fobject_name%2F{tx_name}
    &facet=package
    &facet=appl
```

## Transport Requests

### List transports

```
GET /sap/bc/adt/cts/transports
    ?user=<username>
    &target=
    &category=Workbench
Accept: application/vnd.sap.cts.transport.worklist+xml; charset=utf-8
```

Response: XML with transport work items. Parse `TRKORR`, `AS4TEXT` (description), `TRSTATUS` (`D`=open, `R`=released), `AS4USER` (owner).

### Create transport

```
POST /sap/bc/adt/cts/transports
Content-Type: application/vnd.sap.cts.transport.request+xml; charset=utf-8

<?xml version="1.0" encoding="utf-8"?>
<cts:transportRequest xmlns:cts="http://www.sap.com/cts">
  <cts:attributes>
    <cts:attribute name="category"    value="Workbench"/>
    <cts:attribute name="owner"       value="{username}"/>
    <cts:attribute name="description" value="{description}"/>
    <cts:attribute name="target"      value=""/>
  </cts:attributes>
</cts:transportRequest>
```

Response: `Location` header contains the new transport URI; extract the last path segment as `TRKORR`.
All attribute values must be XML-escaped before interpolation.

### Release transport

```
POST /sap/bc/adt/cts/transports/{TRKORR}?action=release
```

Response: 200 = released. Irreversible.

## SICF Service Activation

Activate in transaction `SICF` before use:

| Service path | Required for |
|---|---|
| `/sap/bc/adt` | All ADT endpoints |
| `/sap/bc/adt/datapreview` | `run-sql` (Open SQL Data Preview) |

## Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 401 | Wrong credentials |
| 403 | Missing authorization OR expired CSRF token |
| 404 | Object not found |
| 503 | ADT service not activated in SICF |

## Required Authorizations

| Operation | Authorization objects |
|---|---|
| All read operations | `S_ADT_RES`, `S_RFC` (ADT function groups) — or role `SAP_ADT_BASE` |
| `write-source`, `activate` | `S_DEVELOP` with `ACTVT=02` on relevant object types |
| `create-transport`, `release-transport` | `S_CTS_ADMI` or equivalent transport authorization |
| `list-transports` | Covered by `SAP_ADT_BASE` — no additional flag needed |
