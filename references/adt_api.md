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

## Source Code Endpoints

| Object Type | Method | URL Pattern |
|-------------|--------|-------------|
| Program (report) | GET | `/sap/bc/adt/programs/programs/{name}/source/main` |
| Class | GET | `/sap/bc/adt/oo/classes/{name}/source/main` |
| Interface | GET | `/sap/bc/adt/oo/interfaces/{name}/source/main` |
| Function Group | GET | `/sap/bc/adt/functions/groups/{fg_name}/source/main` |
| Function Module | GET | `/sap/bc/adt/functions/groups/{fg_name}/fmodules/{fm_name}/source/main` |
| Include | GET | `/sap/bc/adt/programs/includes/{name}/source/main` |
| DDIC Table | GET | `/sap/bc/adt/ddic/tables/{name}/source/main` |
| DDIC Structure | GET | `/sap/bc/adt/ddic/structures/{name}/source/main` |
| Domain | GET | `/sap/bc/adt/ddic/domains/{name}/source/main` |
| Data Element | GET | `/sap/bc/adt/ddic/dataelements/{name}` |

Object names must be URL-encoded. All responses are plain text (ABAP source) or XML.

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

## SICF Service Activation

Required for all ADT endpoints:
- Transaction: `SICF`
- Service path: `/sap/bc/adt`

## Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 401 | Wrong credentials |
| 403 | Missing authorization OR expired CSRF token |
| 404 | Object not found |
| 503 | ADT service not activated in SICF |

## Required Authorizations

The SAP user needs:
- `S_ADT_RES` — ADT resource access
- `S_RFC` for the relevant ADT function groups
- Or simply assign role `SAP_ADT_BASE`
