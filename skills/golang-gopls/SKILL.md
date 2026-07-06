---
name: golang-gopls
description: "Golang semantic code intelligence via `gopls`, the official Go language server — go-to-definition, find references, call/implementation hierarchy, workspace symbol search, package API discovery, diagnostics, safe rename, refactors (extract/inline/fill/rewrite code actions), formatting, and generated tests. Reaches an agent via gopls's own MCP server (`go_*` tools), Claude Code's native `LSP` tool, or the `gopls` CLI. Use when navigating or refactoring Go code — jumping to a definition, finding call sites before a rename, understanding a file's or package's dependencies, running diagnostics after an edit, or extracting/inlining/renaming. Not for the published ecosystem — packages not in your `go.mod`, versions, licenses, importers — → See `samber/cc-skills-golang@golang-pkg-go-dev` skill (`godig`). Not for a whole-tree vulnerability audit → See `samber/cc-skills-golang@golang-security` skill (`govulncheck`)."
user-invocable: true
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents. Requires the gopls binary (go install golang.org/x/tools/gopls@latest) v0.20+ on PATH.
metadata:
  author: samber
  version: "1.0.0"
  openclaw:
    emoji: "🛰️"
    homepage: https://github.com/samber/cc-skills-golang
    requires:
      bins:
        - go
        - gopls
    install:
      - kind: go
        package: golang.org/x/tools/gopls@latest
        bins: [gopls]
    skill-library-version: "0.22.0"
allowed-tools: Read Edit Write Glob Grep Bash(go:*) Bash(golangci-lint:*) Bash(git:*) Agent Bash(gopls:*) LSP mcp__gopls__*
---

**Persona:** You are a Go engineer who reaches for semantic code intelligence instead of grep whenever a question is about the resolved build — grep finds text, `gopls` finds meaning (types, call graphs, shadowing, implementation relationships).

**Dependencies:** `gopls` — `go install golang.org/x/tools/gopls@latest` (v0.20+). The native `LSP` tool additionally needs `ENABLE_LSP_TOOL=1` and the `gopls-lsp@claude-plugins-official` marketplace plugin (see [references/mcp.md](references/mcp.md)).

`gopls` is the official Go language server. It only answers questions about **your specific, locally resolved build** — your workspace plus every dependency exactly as pinned in `go.sum`, including `replace` directives. For a package that isn't part of that build (versions, docs, licenses, CVEs of something you haven't added yet), → See `samber/cc-skills-golang@golang-pkg-go-dev` skill (`godig`) instead.

## Three ways to reach gopls

Not interchangeable — pick by what you already know and what you need back:

- **gopls's own MCP server (preferred for most tasks)** — purpose-built for agents: tools take names, file paths, and fuzzy queries instead of raw cursor positions. Register once per machine: `claude mcp add gopls -- gopls mcp`. Runs headless over stdio, no editor attached, only sees files saved to disk — the right default for an agent-only workflow. See [references/mcp.md](references/mcp.md) for every tool.
- **The native `LSP` tool** — Claude Code's built-in editor-style integration. Off by default: set `ENABLE_LSP_TOOL=1`, install `gopls`, and install the official `gopls-lsp@claude-plugins-official` marketplace plugin to wire it as the Go language server. Operations (`goToDefinition`, `findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`, `goToImplementation`, call hierarchy) are keyed by `line`/`character`, so they're most useful once you already have a location — typically right after a grep or a read. Unique value: compiler diagnostics are pushed into context automatically after every edit, no explicit call needed.
- **The `gopls` CLI** — same engine, invoked as `gopls <command> <file:line:col>`. The Go team documents it as experimental and debugging-only — "not efficient, complete, flexible, or officially supported." Use it when neither MCP nor the native tool is wired up, or for a one-shot scripted check. Positions are `file:line:col` (1-indexed, UTF-8 bytes) or `file:#offset` (0-indexed). See [references/cli.md](references/cli.md).

**Preference order: MCP → native `LSP` → CLI.** MCP tools match how an agent thinks (by name/path, not cursor position); the native tool adds free automatic diagnostics; the CLI is the documented fallback of last resort. Wire as many as are available and let the task pick the tool — a query you already have a `line:col` for is cheap via `LSP`, a "where is X" query is cheap via `go_search`, a quick unattended check is cheap via the CLI.

## Capability → CLI → MCP → native LSP

Full mapping of every capability to its CLI command, MCP tool, and native `LSP` op: [references/matrix.md](references/matrix.md).

## Use cases

- **Navigation** — jump to a definition, an implementation, or trace a call graph before touching code you didn't write. Details: [references/features.md](references/features.md#navigation).
- **Code discovery** — learn a workspace's shape (`go_workspace`), fuzzy-search a symbol you can't place exactly (`go_search`), or read a dependency's public surface (`go_package_api`) before using it.
- **Documentation** — hover for type/doc/size info, signature help while calling a function, or browse rendered package docs (`source.doc`, including internal packages pkg.go.dev never sees).
- **Diagnostics & safety** — compiler and analyzer errors after every edit (`go_diagnostics` / automatic with `LSP`), plus a lightweight `go_vulncheck` reachability check: once as a baseline right after detecting the workspace, and again after any `go.mod` change.
- **Formatting** — canonical `gofmt`-equivalent formatting and import organization, both scriptable and code-action-driven.
- **Refactoring** — safe rename (blocks a change that would break interface satisfaction), extract/inline, and the full `refactor.rewrite.*` family (fill struct/switch, invert if, split/join lines, remove unused parameter, add struct tags, implement interface). Full catalog with gotchas: [references/features.md](references/features.md#transformation).

## Efficient workflows

These Read/Edit workflows encode the order that avoids redundant queries and half-applied edits — treat every step as required, not optional, even to save a round trip.

- **Session start** — call `go_workspace` once to detect whether this is a Go workspace at all; if it is, immediately follow with a baseline `go_vulncheck` to surface vulnerabilities the workspace already carries. This is unconditional, separate from the edit workflow's later check after a dependency change.

**Read workflow** (understand before touching anything):

1. `go_workspace` — layout (module/workspace/GOPATH); same call as the session-start check above if it hasn't run yet.
2. `go_search` — fuzzy-locate a type/function/variable by name.
3. `go_file_context` — right after reading any Go file for the first time, see what it pulls in from the rest of its package; re-run if that file's dependencies change.
4. `go_package_api` — a third-party dependency's or sibling package's public surface, without reading every file.

**Edit workflow** (iterate until diagnostics are clean):

1. Read first (workflow above).
2. `go_symbol_references` before modifying any definition — judge the blast radius, then read every referencing file that needs a matching edit.
3. Make all planned edits, including the reference-site edits, before moving on.
4. `go_diagnostics` on every changed file — mandatory after each modification, not an optional cleanup pass.
5. Fix reported errors: review any suggested quick-fix diff before applying, then re-run diagnostics to confirm the fix landed. Ignore hint/info diagnostics unrelated to the task. A diagnostic message can paraphrase the surrounding source rather than quote it verbatim.
6. Only if `go.mod` dependencies changed, run `go_vulncheck` on the whole workspace — after diagnostics are clean, not before.
7. Run `go test <changed-package-paths>` — not `./...` unless explicitly asked, since a full-repo run slows the iteration loop.

**Gotchas worth knowing before you rely on a result:**

- `references` results only reflect the **build configuration of the queried file** — a query on `foo_windows.go` will not surface matches in `bar_linux.go`; re-run under the relevant `GOOS`/build tags if a cross-platform result is missing.
- `call_hierarchy` only shows **static** calls — calls through function values or interface methods are invisible to it; corroborate with `references` when the call site matters.
- Extract/inline refactors are less rigorous than rename: comments are sometimes dropped, and generated files marked `DO NOT EDIT` receive no code actions at all.
- `refactor.rewrite.fillStruct` searches only the current file above the cursor and needs the struct's package already imported — run `source.organizeImports` first if the type was just typed in.

## gopls vs godig vs Context7 vs govulncheck

`gopls` only reasons about code present and resolvable in the local build:

- For anything not tied to that build (version history, license, ecosystem-wide importers, CVEs of a package not yet added) → See `samber/cc-skills-golang@golang-pkg-go-dev` skill (`godig`) — it queries pkg.go.dev directly, no local checkout needed.
- For a comprehensive, whole-tree vulnerability audit (CI gates, periodic sweeps) rather than gopls's lightweight on-demand `go_vulncheck` → See `samber/cc-skills-golang@golang-security` skill (`govulncheck`).
- Context7 remains a fallback for non-Go docs or a Go module not indexed on pkg.go.dev.

The full task-to-tool matrix lives in the `samber/cc-skills-golang@golang-how-to` skill's "`godig` vs gopls vs Context7 vs govulncheck" section.
