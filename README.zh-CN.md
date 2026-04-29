# sap-abap-cli

[English](README.md) | [中文](README.zh-CN.md)

通过 [ADT（ABAP 开发工具）REST API](https://help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/about-abap-development-tools) 从 SAP 系统读取 ABAP 源代码和元数据的命令行工具，同时也是一个 AI 智能体技能包（Agent Skill）。

支持程序、类、函数模块、接口、Include、DDIC 对象、包、事务码及对象搜索——可在终端直接使用，也可集成到 AI 智能体工作流中。

---

## 环境要求

- Python 3.8+
- SAP 系统（本地 ECC / S/4HANA 或 BTP ABAP），需已激活 ADT 服务
- 拥有 `SAP_ADT_BASE` 角色（或等效权限）的 SAP 对话用户

依赖包（`click`、`requests`、`urllib3`）在首次运行时自动安装。

---

## Windows 一键安装 — AI 智能体快速上手

> **示例：[opencode](https://opencode.ai)** — 免费开源的 AI 智能体 — 作为本文的参考配置。  
> `sap-abap-cli` 以标准 Agent Skill 形式（`SKILL.md`）打包，可与任何支持自定义工具/技能的智能体框架配合使用。

`setup-opencode-abap-cli.bat` 是专为 Windows 用户设计的一键安装脚本，全自动完成 opencode 与本技能包的配置。

### 脚本执行内容

| 步骤 | 操作 |
|------|------|
| 1 | 检测 Node.js ≥ v18、Python 3、Git 是否已安装（缺失时打印下载指引） |
| 2 | 将 Node.js 可执行目录和 npm 全局包路径添加到用户级 `PATH` |
| 3 | 通过 `npm install -g opencode-ai` 全局安装 opencode |
| 4 | 将本仓库克隆到 `%USERPROFILE%\.agents\skills\sap-abap-cli`（opencode 技能目录） |
| 5 | 安装 Python 依赖：`click`、`requests`、`urllib3` |

### 前置软件

运行脚本前，请先安装：

- **[Node.js v18 LTS 或更高版本](https://nodejs.org)** — 使用默认安装选项（默认已勾选添加 PATH）
- **[Python 3.8+](https://www.python.org/downloads)** — 安装时务必勾选 **"Add Python to PATH"**
- **[Git for Windows](https://git-scm.com/download/win)** — 使用默认安装选项

### 运行安装脚本

下载 [`setup-opencode-abap-cli.bat`](./setup-opencode-abap-cli.bat)，**双击运行**即可。  
脚本将以彩色状态信息引导安装过程；如有前置软件缺失，会自动停止并给出安装提示。

### 使用 opencode 分析 SAP 代码

安装完成后：

```cmd
REM 打开 CMD：按 Win+R，输入 cmd，回车
opencode
```

进入 opencode 后，配置 AI 模型提供商：

```
/connect
```

然后即可用自然语言直接查询 SAP 系统：

```
分析 ZCL_PAYMENT_PROCESSOR 类是否存在安全漏洞
```

```
读取程序 ZREPORT_UPLOAD，检查 SQL 注入风险、缺失的权限检查和硬编码凭据
```

```
扫描包 ZMYPAYMENT 下的所有对象，列出潜在的安全风险
```

opencode 会自动调用 `sap-abap-cli` 通过 ADT 接口从 SAP 系统获取 ABAP 源代码，再交给 AI 模型分析——无需手动复制粘贴。

### SAP 凭据配置（首次使用）

首次执行 ABAP 查询时，opencode 会提示输入 SAP 连接信息：

```
SAP 系统 URL    — 例如 https://my-sap.example.com:8000（含端口号）
SAP 用户名      — 对话用户，例如 DEVELOPER
SAP 密码        — SAP 登录密码
SAP 集团        — 3 位集团编号，例如 100
跳过 SSL 验证？  — 内网或自签名证书环境选 yes
```

凭据保存至 `~\.sap-abap-cli\config.json`，后续会话自动复用。

### 支持的 AI 智能体

opencode 仅作为示例。`sap-abap-cli` 实现了标准 Agent Skill 接口（`SKILL.md`），可与任何支持自定义工具或技能的智能体框架集成：

| 智能体 | 说明 |
|--------|------|
| [opencode](https://opencode.ai) | 免费开源，本文示例，支持 30+ 模型提供商 |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Anthropic 官方 CLI 智能体 |
| [Cursor](https://cursor.sh) | AI 代码编辑器，支持 MCP 工具扩展 |
| 其他 MCP 兼容智能体 | 将 `SKILL.md` 放入技能目录即可接入 |

> ⚠️ **数据合规提示：** ABAP 源代码可能包含企业核心业务逻辑和敏感数据。  
> 将代码发送至公网 AI 服务前，请确认符合企业数据安全政策。  
> 对于敏感环境，建议优先使用公司内网部署的模型底座。

---

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/sap-abap-cli
cd sap-abap-cli

# 2. 配置凭据（交互式向导 — 密码不回显）
python3 skills/sap-abap-cli/scripts/sap_abap_cli.py configure

# 3. 验证连接
python3 skills/sap-abap-cli/scripts/sap_abap_cli.py status

# 4. 开始读取 ABAP 对象
python3 skills/sap-abap-cli/scripts/sap_abap_cli.py get-program SAPMV45A
python3 skills/sap-abap-cli/scripts/sap_abap_cli.py get-class ZCL_MY_CLASS
python3 skills/sap-abap-cli/scripts/sap_abap_cli.py get-function BAPI_SALESORDER_CREATEFROMDAT2 --group BAPI_SD_SALESORDER
```

---

## 配置

### 交互式向导（推荐）

```bash
python3 skills/sap-abap-cli/scripts/sap_abap_cli.py configure
```

凭据保存至 `~/.sap-abap-cli/config.json`，文件权限为 `0600`。

> **安全提示：** 配置文件以明文存储凭据。  
> 请勿将其提交到版本控制系统，并限制文件访问权限。

### 环境变量

适用于 CI/CD 流水线或临时会话。环境变量优先级高于配置文件。

```bash
export SAP_URL=https://my-sap.example.com:8000
export SAP_USERNAME=MYUSER
export SAP_PASSWORD=secret          # 推荐使用此方式，避免 --password 参数暴露在命令历史中
export SAP_CLIENT=100
export SAP_LANGUAGE=EN              # 可选，默认：EN
export SAP_VERIFY_SSL=0             # 可选：设为 0 以跳过自签名证书验证
```

### 非交互式参数（智能体 / 自动化工作流）

```bash
# 通过环境变量传递密码，避免暴露在 Shell 历史记录中
SAP_PASSWORD="secret" python3 skills/sap-abap-cli/scripts/sap_abap_cli.py configure \
  --url      "https://my-sap.example.com:8000" \
  --username "MYUSER" \
  --client   "100"
```

---

## 命令参考

| 命令 | 说明 |
|------|------|
| `configure` | 保存连接凭据 |
| `status` | 显示当前连接配置 |
| `get-program <NAME>` | ABAP 程序 / 报表源代码 |
| `get-class <NAME>` | ABAP 类源代码 |
| `get-function-group <NAME>` | 函数组顶层 Include 源代码 |
| `get-function <NAME> --group <FG>` | 函数模块源代码 |
| `get-include <NAME>` | ABAP Include 源代码 |
| `get-interface <NAME>` | ABAP 接口源代码 |
| `get-table <NAME>` | DDIC 表字段定义（XML） |
| `get-structure <NAME>` | DDIC 结构定义（XML） |
| `get-type-info <NAME>` | 域或数据元素信息（XML） |
| `get-package <NAME>` | 包对象列表（JSON） |
| `get-transaction <NAME>` | 事务码属性 / 包信息（XML） |
| `get-table-contents <NAME> [--max-rows N]` | 表数据 *（需自定义服务）* |
| `search-object <QUERY> [--max-results N]` | 对象名称搜索，支持 `*` 通配符 |

任意命令加 `--help` 查看完整参数说明。

---

## 示例

```bash
CLI="skills/sap-abap-cli/scripts/sap_abap_cli.py"

# 源代码
python3 $CLI get-program SAPMV45A
python3 $CLI get-class ZCL_MY_CLASS
python3 $CLI get-function BAPI_SALESORDER_CREATEFROMDAT2 --group BAPI_SD_SALESORDER
python3 $CLI get-include MV45AFZZ
python3 $CLI get-interface ZIF_MY_INTERFACE

# 字典对象
python3 $CLI get-table VBAK
python3 $CLI get-structure VBAKKOM
python3 $CLI get-type-info MATNR

# 对象发现
python3 $CLI search-object "ZCL_ORDER*" --max-results 20
python3 $CLI get-package ZMYPACKAGE
python3 $CLI get-transaction VA01

# 表数据（需自定义 SAP 服务，参见前置条件）
python3 $CLI get-table-contents T001 --max-rows 50
```

---

## SAP 前置条件

### 1. 激活 ADT 服务

在事务码 `SICF` 中，激活以下路径的服务树：

```
/sap/bc/adt
```

### 2. 分配用户权限

为 SAP 用户分配角色 `SAP_ADT_BASE`，或手动授予：

- `S_ADT_RES` — ADT 资源访问权限
- `S_RFC` — ADT 函数组的远程函数调用权限

### 3. （可选）自定义表内容服务

`get-table-contents` 命令需要在目标 SAP 系统中部署自定义 REST 服务 `/z_sap_abap_cli/z_tablecontent`。  
实现参考：[How to use RFC_READ_TABLE from JavaScript via WebService](https://community.sap.com/t5/application-development-and-automation-blog-posts/how-to-use-rfc-read-table-from-javascript-via-webservice/ba-p/13172358)

其他所有命令无需此服务即可正常使用。

---

## 输出格式

| 命令 | 输出格式 |
|------|----------|
| 源代码类命令 | ABAP 源代码纯文本 |
| `get-table`、`get-structure`、`get-type-info`、`get-transaction`、`search-object` | ADT 原始 XML |
| `get-package` | JSON 数组 |
| `status` | 纯文本键值对 |

所有输出写入 **stdout**。错误写入 **stderr**，并返回非零退出码。

---

## 错误参考

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `Not configured` | 未保存凭据 | 运行 `configure` |
| `HTTP 401` | 用户名或密码错误 | 重新运行 `configure` |
| `HTTP 403` | 缺少 `SAP_ADT_BASE` 角色 | 联系 Basis 分配权限 |
| `HTTP 404` | 对象名称不存在 | 使用 `search-object` 查找正确名称 |
| `HTTP 503` | `/sap/bc/adt` 未激活 | 联系 Basis 在 `SICF` 中激活服务 |
| SSL 错误 | 自签名证书 | 使用 `SAP_VERIFY_SSL=0` 重新配置 |

---

## 安全注意事项

- 凭据以**明文**存储在 `~/.sap-abap-cli/config.json` 中（权限 `0600`）。  
  这与常见 CLI 工具（AWS CLI、Azure CLI）的做法一致。请限制文件访问权限。
- 避免通过 `--password` 参数传递密码——它会出现在 Shell 历史记录和 `ps` 输出中。  
  推荐使用交互式 `configure` 向导或 `SAP_PASSWORD` 环境变量。
- 在共享环境或 CI 环境中，建议使用短期凭据并定期轮换。

---

## 许可证

[MIT](LICENSE)
