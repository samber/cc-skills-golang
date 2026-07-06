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

`gopls` is the official Go language server. It answers questions about **your specific, locally resolved build**: your workspace plus every dependency exactly as pinned in `go.sum`, including `replace` directives pointing at forks or local paths. It cannot see a package that isn't part of that build — for the published ecosystem (versions, docs, licenses, CVEs of a package you haven't added yet), → See `samber/cc-skills-golang@golang-pkg-go-dev` skill (`godig`) instead.

## Three ways to reach gopls

The same capabilities are exposed through three different surfaces. They are not interchangeable — pick by what you already know and what you need back.

1. **gopls's own MCP server (preferred for most tasks)** — purpose-built for AI agents. Its tools take names, file paths, and fuzzy queries rather than raw cursor positions, so they fit how an agent naturally asks questions ("where is `Server` defined" rather than "what's at line 42, column 7"). Register it once per machine:

   ```bash
   claude mcp add gopls -- gopls mcp
   ```

   This runs gopls **detached**, over stdio, headless — no editor attached, only sees files saved to disk. An **attached** mode also exists (`gopls serve -mcp.listen=localhost:8092`), which shares memory with a live LSP session and can see unsaved buffers; detached is the right default for an agent-only workflow. See [references/mcp.md](references/mcp.md) for every tool.

2. **The native `LSP` tool** — Claude Code's built-in editor-style integration. Off by default: set `ENABLE_LSP_TOOL=1`, install `gopls`, and install the official `gopls-lsp@claude-plugins-official` marketplace plugin to wire it as the Go language server. Its operations (`goToDefinition`, `findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`, `goToImplementation`, call hierarchy) are keyed by `line`/`character`, so they're most useful once you already have a location — typically right after a grep or a read — rather than as a first search. Its one capability the MCP server doesn't replicate: **compiler diagnostics are pushed into context automatically after every edit**, with no explicit diagnostics call needed. See [references/mcp.md](references/mcp.md).

3. **The `gopls` CLI** — the same engine, invoked directly as `gopls <command> <file:line:col>`. The Go team documents this interface as **experimental and intended for debugging**, not for production tooling — "not efficient, complete, flexible, or officially supported." Use it when neither MCP nor the native tool is wired up, for one-shot scripted checks, or to sanity-check a query outside the agent loop. Positions are `file:line:col` (1-indexed, columns in UTF-8 bytes) or `file:#offset` (0-indexed). See [references/cli.md](references/cli.md).

**Preference order: MCP → native `LSP` → CLI.** The MCP tools match how an agent thinks (by name/path, not cursor position); the native tool adds free automatic diagnostics on top; the CLI is the documented fallback of last resort. Wire as many as are available and let the task pick the tool — a query you already have a `line:col` for is cheap via `LSP`, a "where is X" query is cheap via `go_search`, and a quick unattended check is cheap via the CLI.

## Capability → CLI → MCP → native LSP

| Capability | CLI | MCP tool | Native LSP op |
| --- | --- | --- | --- |
| Workspace layout (module/workspace/GOPATH) | `gopls stats` | `go_workspace` | — |
| Fuzzy-find a symbol by name, workspace-wide | `gopls workspace_symbol <query>` | `go_search` | `workspaceSymbol` |
| Go to definition | `gopls definition f:l:c` | — (use `go_file_context`/`go_package_api`) | `goToDefinition` |
| Go to type definition | — (unsupported) | — | `goToTypeDefinition` |
| Find all references | `gopls references f:l:c` | `go_symbol_references` | `findReferences` |
| Implements / implemented-by | `gopls implementation f:l:c` | — | `goToImplementation` |
| Full subtype/supertype tree | — (not yet supported) | — | Type Hierarchy |
| Call graph (callers/callees) | `gopls call_hierarchy f:l:c` | — | Call Hierarchy |
| File's own symbols (outline) | `gopls symbols <file>` | `go_file_context` | `documentSymbol` |
| A package's public API | — | `go_package_api` | (hover per-symbol) |
| A file's intra-package dependencies | — | `go_file_context` | — |
| Hover info (type, doc, size/offset) | — | — | `hover` |
| Signature help | `gopls signature f:l:c` | — | signature help |
| Compiler + analyzer diagnostics | `gopls check <file>` | `go_diagnostics` | automatic, pushed after every edit |
| Vulnerability reachability (current build) | — | `go_vulncheck` | — |
| Safe rename (symbol, receiver, package move, signature) | `gopls rename -w f:l:c NewName` | `go_rename_symbol` | rename |
| Organize / fix imports | `gopls imports -w <file>` | — | `source.organizeImports` code action |
| Format | `gopls format -w <file>` | — | `textDocument/formatting` |
| Refactor (extract, inline, fill, rewrite — see [references/features.md](references/features.md)) | `gopls codeaction -kind=<kind> -exec -w <file>` | — | code action |
| Generate a test for a function | `gopls codelens -exec <file:line> "..."` (via `source.addTest`) | — | code action / code lens |

## Use cases

- **Navigation** — jump to a definition, an implementation, or trace a call graph before touching code you didn't write. Details: [references/features.md](references/features.md#navigation).
- **Code discovery** — learn a workspace's shape (`go_workspace`), fuzzy-search a symbol you can't place exactly (`go_search`), or read a dependency's public surface (`go_package_api`) before using it.
- **Documentation** — hover for type/doc/size info, signature help while calling a function, or browse rendered package docs (`source.doc`, including internal packages pkg.go.dev never sees).
- **Diagnostics & safety** — compiler and analyzer errors after every edit (`go_diagnostics` / automatic with `LSP`), plus a lightweight, on-demand `go_vulncheck` reachability check against the current build.
- **Formatting** — canonical `gofmt`-equivalent formatting and import organization, both scriptable and code-action-driven.
- **Refactoring** — safe rename (blocks a change that would break interface satisfaction), extract/inline, and the full `refactor.rewrite.*` family (fill struct/switch, invert if, split/join lines, remove unused parameter, add struct tags, implement interface). Full catalog with gotchas: [references/features.md](references/features.md#transformation).

## Efficient workflows

Follow the two workflows gopls's own MCP instructions prescribe — they encode the order that avoids redundant queries and half-applied edits.

**Read workflow** (understand before touching anything):

1. `go_workspace` — learn the layout once per session.
2. `go_search` — fuzzy-locate a type/function/variable by name.
3. `go_file_context` — right after reading any Go file for the first time, see what it pulls in from the rest of its package.
4. `go_package_api` — for a third-party dependency or a sibling package in a monorepo, see its public surface without reading every file.

**Edit workflow** (iterate until diagnostics are clean):

1. Read first (workflow above).
2. `go_symbol_references` before modifying any definition — judge the blast radius, read every referencing file that needs a matching edit.
3. Make all planned edits, including the reference-site edits.
4. `go_diagnostics` on every changed file — mandatory after each modification.
5. Fix reported errors, re-run diagnostics until clean. Hint/info diagnostics unrelated to the task can be ignored.
6. If `go.mod` dependencies changed, run `go_vulncheck` on the whole workspace once diagnostics are clean.
7. Run `go test <changed-package-paths>` — not `./...` unless explicitly asked, since a full-repo run slows the iteration loop.

**Gotchas worth knowing before you rely on a result:**

- `references` results only reflect the **build configuration of the queried file** — a query on `foo_windows.go` will not surface matches in `bar_linux.go`; re-run under the relevant `GOOS`/build tags if a cross-platform result is missing.
- `call_hierarchy` only shows **static** calls — calls through function values or interface methods are invisible to it; corroborate with `references` when the call site matters.
- Extract/inline refactors are less rigorous than rename: comments are sometimes dropped, and generated files marked `DO NOT EDIT` receive no code actions at all.
- `refactor.rewrite.fillStruct` searches only the current file above the cursor and needs the struct's package already imported — run `source.organizeImports` first if the type was just typed in.

## gopls vs godig vs Context7 vs govulncheck

`gopls` only reasons about code **present and resolvable in the local build** — for anything that isn't tied to that build (a package's version history, its license, who imports it across the whole public ecosystem, whether a package you haven't added yet has known CVEs), → See `samber/cc-skills-golang@golang-pkg-go-dev` skill (`godig`) — it queries pkg.go.dev directly and needs no local checkout. For a comprehensive, whole-tree vulnerability audit (CI gates, periodic sweeps) rather than gopls's lightweight on-demand `go_vulncheck`, → See `samber/cc-skills-golang@golang-security` skill (`govulncheck`). Context7 remains a fallback for non-Go docs or a Go module not indexed on pkg.go.dev. The full task-to-tool matrix lives in the `samber/cc-skills-golang@golang-how-to` skill's "`godig` vs gopls vs Context7 vs govulncheck" section.

---

This skill is not exhaustive. Please refer to the official gopls documentation and code examples for current behavior and settings — the tool evolves fast and this skill's static markdown can lag.

If you encounter a bug or unexpected behavior in `gopls`, open an issue at <https://github.com/golang/go/issues> (label `gopls`).
