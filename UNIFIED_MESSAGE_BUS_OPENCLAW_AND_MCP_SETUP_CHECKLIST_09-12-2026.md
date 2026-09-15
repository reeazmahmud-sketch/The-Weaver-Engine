FILE: UNIFIED_MESSAGE_BUS_OPENCLAW_AND_MCP_SETUP_CHECKLIST_09-12-2026.md
CREATED BY: Admin (prepared) / Grok AI Assistant (filed)
DATE: 09-12-2026
PROJECT: The-Weaver-Engine / Autonomous Agentic Lifecycle
VERSION: 1.0.0
===============================================================================

Description:
Docs-only configuration checklist for reviewing OpenClaw setup alongside an
MCP shared-state server for the Unified Message Bus. Aspirational steps for
Admin review. Does NOT install OpenClaw, does NOT stand up an MCP server,
does NOT store secrets, does NOT draft a second Master Orchestrator.
Docker deferred.

===============================================================================

# OpenClaw + MCP Setup Checklist (Docs-Only — Not Executed)

**Purpose:** Let Admin **review** specific configuration steps without claiming a live install.  
**OpenClaw role:** [`UNIFIED_MESSAGE_BUS_OPENCLAW_AUTONOMOUS_MESSAGE_ROUTER_09-12-2026.md`](UNIFIED_MESSAGE_BUS_OPENCLAW_AUTONOMOUS_MESSAGE_ROUTER_09-12-2026.md)  
**UMB parent:** [`UNIFIED_MESSAGE_BUS_ARCHITECTURE_5_TEAM_CHANNELS_09-12-2026.md`](UNIFIED_MESSAGE_BUS_ARCHITECTURE_5_TEAM_CHANNELS_09-12-2026.md)  
**Weaver as-built MCP path:** `weaver_runtime/1_universal_modules_weaver/mcps/` (**empty today**)  
**Master Orchestrator:** cite [`MASTER_ORCHESTRATOR_PROMPT_FIVE_TEAM_HANDOFFS_09-12-2026.md`](MASTER_ORCHESTRATOR_PROMPT_FIVE_TEAM_HANDOFFS_09-12-2026.md) only  

---

## 0. Execution status

| Item | Status |
|------|--------|
| This checklist filed for review | **Yes** |
| OpenClaw installed | **No** |
| MCP document/state server live for UMB | **No** |
| Tokens / API keys written into repo | **Forbidden** — keep outside portable tree |
| Docker used for this setup | **Deferred** — do not use unless Admin reopens Docker |

**To actually run these steps later:** requires a **separate explicit Admin install order**.

---

## 1. Prerequisites (review)

1. Confirm project home: `The-Weaver-Engine/` (portable product root).  
2. Confirm Master Orchestrator remains **1.0.0-APPROVED-DOCS-ONLY** (no new prompt).  
3. Confirm Docker still deferred.  
4. Confirm Slack/Discord/Telegram **live** bots still out of scope unless separately ordered (OpenClaw may later bridge; do not imply bots are on).  
5. Note Weaver `mcps/` is empty — any MCP server is a **new** capability, not an existing Weaver MCP pack.

---

## 2. OpenClaw setup steps (aspirational)

| Step | Action | Done? |
|------|--------|-------|
| O1 | Obtain OpenClaw (formerly Moltbot) from Admin-approved source; pin version in a local ops note **outside** secrets | ☐ Not executed |
| O2 | Install OpenClaw CLI on the operator machine (Mac first; Windows/Linux as needed) using vendor docs | ☐ |
| O3 | Verify `openclaw` (or vendor binary name) runs in a local shell — smoke `--help` / version only | ☐ |
| O4 | Configure **local** profile: project_id / relative paths to Weaver docs; **no** hardcoded `/Users/...` in portable configs | ☐ |
| O5 | Designate terminal logging channel for **Team 2** module-creation events (per UMB routing) | ☐ |
| O6 | Wire agent progress stream → OpenClaw CLI stdout/log sink (docs contract first; code later) | ☐ |
| O7 | Define Admin shell command allow-list (what humans may issue via CLI) | ☐ |
| O8 | Optional later: bridge OpenClaw → external chat — **only** after Admin orders that channel | ☐ |

---

## 3. MCP shared-state server steps (aspirational)

| Step | Action | Done? |
|------|--------|-------|
| M1 | Choose MCP server role: “shared documentation / state” for UMB (not the same as empty sample `mcps/` folders) | ☐ Not executed |
| M2 | Define root document set agents must see (lifecycle docs + blueprints path) via **relative** paths | ☐ |
| M3 | Expose read APIs/tools for: list docs, fetch doc, fetch Go/No-Go summary fields (as available) | ☐ |
| M4 | Mandate `@Admin` mention handlers on **any** future channel to **query MCP** before answering | ☐ |
| M5 | Prove parity test (manual): terminal agent and (future) Slack agent resolve the **same** doc folder | ☐ |
| M6 | Place any MCP **config stubs** under `weaver_runtime/1_universal_modules_weaver/mcps/` only when Admin orders scaffolding — keep secrets out of git | ☐ |

---

## 4. Joint validation (when Admin orders install)

| Check | Pass criteria |
|-------|---------------|
| CLI progress | Agent can emit a Team 2 “module created” line via OpenClaw CLI |
| Admin command | Admin can issue an allow-listed shell command through OpenClaw CLI |
| MCP parity | Same doc path resolved from CLI session and from a second client |
| No second orchestrator | Still citing approved Master Orchestrator only |
| No Docker | Unless Admin reopened Docker |

---

## 5. Explicit non-goals of this checklist

* Does **not** install software.  
* Does **not** create Slack/Discord/Telegram bots.  
* Does **not** draft or replace the Master Orchestrator.  
* Does **not** claim MALS / `proxy_router` / `engine_core/` exist.  
* Does **not** authorize Docker Compose.

---

## 6. Cross-links

| Document | Role |
|----------|------|
| [`UNIFIED_MESSAGE_BUS_OPENCLAW_AUTONOMOUS_MESSAGE_ROUTER_09-12-2026.md`](UNIFIED_MESSAGE_BUS_OPENCLAW_AUTONOMOUS_MESSAGE_ROUTER_09-12-2026.md) | OpenClaw role |
| [`UNIFIED_MESSAGE_BUS_OPENCLAW_CLI_MCP_COORDINATION_09-12-2026.md`](UNIFIED_MESSAGE_BUS_OPENCLAW_CLI_MCP_COORDINATION_09-12-2026.md) | Terminal ↔ Slack/Telegram alignment intent |
| [`UNIFIED_MESSAGE_BUS_TERMINAL_CLI_INTERFACE_09-12-2026.md`](UNIFIED_MESSAGE_BUS_TERMINAL_CLI_INTERFACE_09-12-2026.md) | Terminal CLI interface |
| [`UNIFIED_MESSAGE_BUS_CORE_TECHNOLOGIES_09-12-2026.md`](UNIFIED_MESSAGE_BUS_CORE_TECHNOLOGIES_09-12-2026.md) | Core tech catalog |
| [`WEAVER_ENGINE_ARCHETYPE_v2_TARGET_REPOSITORY_LAYOUT_09-12-2026.md`](WEAVER_ENGINE_ARCHETYPE_v2_TARGET_REPOSITORY_LAYOUT_09-12-2026.md) | Empty `mcps/` honesty |
| [`WEAVER_ENGINE_CONTINUE_HERE_09-12-2026.md`](WEAVER_ENGINE_CONTINUE_HERE_09-12-2026.md) | Handoff / scope |

---

**End of file.** Review-only checklist. Nothing installed.
