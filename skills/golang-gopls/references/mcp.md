# gopls MCP server & native `LSP` tool reference

## Table of contents

- [Starting the server](#starting-the-server)
- [Registering with Claude Code](#registering-with-claude-code)
- [MCP tools](#mcp-tools)
- [The native `LSP` tool](#the-native-lsp-tool)
- [What the MCP server can and cannot do](#what-the-mcp-server-can-and-cannot-do)

## Starting the server

A standalone gopls instance speaking MCP over stdin/stdout, launched fresh per session, no LSP client involved:

```bash
gopls mcp
```

Only sees files as they exist **on disk** — an edit made through a different tool but not yet saved is invisible to it. This is the right mode for an agent-only workflow with no attached editor.

## Registering with Claude Code

```bash
claude mcp add gopls -- gopls mcp
```

## MCP tools

Eight tools, all keyed by name/path/query rather than cursor position — this is the main ergonomic difference from the native `LSP` tool.

| Tool | Purpose | Example |
| --- | --- | --- |
| `go_workspace` | Learn the workspace's overall structure — module, multi-module workspace, or GOPATH project. Call this first, once per session. | `go_workspace({})` |
| `go_vulncheck` | On-demand reachability check: which known vulnerabilities does the _current_ build actually reach. Run right after `go_workspace` if in a Go workspace, and again after any `go.mod` change. | `go_vulncheck({"pattern":"./..."})` |
| `go_search` | Fuzzy search for a type, function, or variable by name across the workspace — use when you don't know the exact location. | `go_search({"query":"server"})` |
| `go_file_context` | Summarize a file's dependencies on other files in the _same package_. Run this immediately after reading any Go file for the first time. | `go_file_context({"file":"/path/to/server.go"})` |
| `go_package_api` | Show a package's public API — most valuable for third-party dependencies or sibling packages in a monorepo you haven't read file-by-file. | `go_package_api({"packagePaths":["example.com/internal/storage"]})` |
| `go_symbol_references` | Find every reference to a symbol — run before modifying any definition to gauge the blast radius. | `go_symbol_references({"file":"/path/to/server.go","symbol":"Server.Run"})` |
| `go_diagnostics` | Build/analysis errors for the given files — mandatory after every edit. | `go_diagnostics({"files":["/path/to/server.go"]})` |
| `go_rename_symbol` | Rename a symbol and every reference to it, workspace-wide, with the same safety checks as LSP rename (blocks changes that would break interface satisfaction). | — |

See [SKILL.md](../SKILL.md#efficient-workflows) for the Read/Edit workflow order these tools are designed to be chained in.

## The native `LSP` tool

Claude Code's built-in editor-style integration — a different mechanism from the MCP server above, worth wiring in addition to it, not instead of it.

**Enabling it:**

1. Set the environment variable `ENABLE_LSP_TOOL=1` (off by default).
2. Install `gopls` (`go install golang.org/x/tools/gopls@latest`).
3. Install the official `gopls-lsp@claude-plugins-official` marketplace plugin to wire `gopls` as the Go language server backing the tool.

**Operations**, all keyed by `line`/`character` rather than name/path:

- `goToDefinition`
- `findReferences`
- `hover`
- `documentSymbol`
- `workspaceSymbol`
- `goToImplementation`
- call hierarchy

`goToTypeDefinition` is intentionally absent from this list — the native tool does not expose it, so type-definition navigation has no agent-invocable path (see [features.md](features.md#navigation)).

Because these need a location up front, they're most efficient once you already have one — right after a grep or a file read — rather than as the first move in an investigation (that's what `go_search` on the MCP server is for).

**Its unique value:** compiler diagnostics are pushed into context **automatically after every edit**, with no explicit diagnostics call needed — the MCP server's `go_diagnostics` requires an explicit invocation each time.

## What the MCP server can and cannot do

The gopls MCP server wraps LSP functionality with these boundaries:

- **Can**: read files from the filesystem and return their contents; execute `go` commands to load package metadata (which may reach `proxy.golang.org` and write to the local Go module/build cache); write to gopls's own cache/configuration files; upload telemetry if the user has opted in.
- **Cannot**: make arbitrary writes to the source tree outside of the edits a tool call explicitly returns; make arbitrary network requests beyond what `go` itself needs to resolve the build.

Either mode — MCP or native `LSP` — only ever reasons about code that is present and resolvable in the local build: the workspace plus every dependency exactly as pinned in `go.sum`, including `replace` directives. For anything outside that boundary, → See `samber/cc-skills-golang@golang-pkg-go-dev` skill (`godig`).
