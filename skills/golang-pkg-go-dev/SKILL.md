---
name: golang-pkg-go-dev
description: "Golang package and module documentation and exploration via `godig`, a pkg.go.dev API client (CLI + MCP server) — package docs, API references, symbols, code examples, available versions, importers (who imports a package), licenses, and known vulnerabilities. Read-only, no auth. Use for looking up any Go/Golang library's documentation, API signatures, usage examples, which versions exist, whether a dependency has CVEs, or who imports a package — prefer this over Context7 for any Go package or module. Triggers on: how to use a Go library, Go API docs, import usage, code examples, pkg.go.dev. Not for upgrading dependencies (→ See `samber/cc-skills-golang@golang-dependency-management` skill) or choosing a library (→ See `samber/cc-skills-golang@golang-popular-libraries` skill)."
user-invocable: true
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents. Requires the godig CLI (go install github.com/samber/godig/cmd/godig@latest) or access to a godig MCP server, and internet access to reach the pkg.go.dev API.
metadata:
  author: samber
  version: "1.0.0"
  openclaw:
    emoji: "🔎"
    homepage: https://github.com/samber/cc-skills-golang
    requires:
      bins:
        - go
        - godig
    install:
      - kind: go
        package: github.com/samber/godig/cmd/godig@latest
        bins: [godig]
allowed-tools: Read Edit Write Glob Grep Bash(go:*) Bash(golangci-lint:*) Bash(git:*) Bash(godig:*) Agent
---

# golang-pkg-go-dev

**Dependencies:** `godig` — `go install github.com/samber/godig/cmd/godig@latest` (or use a registered godig MCP server / the hosted instance instead).

`godig` queries the [pkg.go.dev](https://pkg.go.dev) API. Use it to answer questions about Go packages and modules: docs, symbols, versions, importers and vulnerabilities. It works as a CLI and as an MCP server. All operations are **read-only** and need no authentication.

## When to use this skill

Trigger on questions like:

- "What versions of github.com/samber/lo are available?"
- "Does golang.org/x/text have known vulnerabilities?"
- "Show me the docs / symbols for package X."
- "Which packages import X?"
- "Search Go packages for Y."

## Setup

### Install

```bash
go install github.com/samber/godig/cmd/godig@latest
```

### Register the MCP server (optional)

`godig mcp` runs over **stdio** by default, or **streamable HTTP** with `--transport http`.

stdio (the client launches godig on demand):

```bash
claude mcp add pkg-go-dev -- godig mcp
```

streamable HTTP (shared server at `/mcp`, default `:8080`):

```bash
godig mcp --transport http --addr :8080
claude mcp add --transport http pkg-go-dev http://localhost:8080/mcp
```

Hosted instance (no install needed) — a public server runs at `https://godig.samber.dev/mcp`:

```bash
claude mcp add --transport http pkg-go-dev https://godig.samber.dev/mcp
```

The CLI and the MCP server expose the **same** operations. Prefer the CLI when available; otherwise use the MCP tools.

## Usage — intent → command/tool

Always append `-o md` to CLI commands so the output is Markdown (renders well in chat).

| Usage | Example | MCP tool |
| --- | --- | --- |
| `godig overview <path>` — start here, one compact call | `godig overview github.com/samber/ro -o md` | `overview` |
| `godig search <query> [--symbol <s>] [--filter <expr>] [--limit N]` | `godig search "result option monad" --limit 5 -o md` | `search` |
| `godig package info <path> [--imports]` | `godig package info github.com/samber/ro -o md` | `package-info` |
| `godig package doc <path> --format <md\|text\|html>` | `godig package doc github.com/samber/ro --format md -o md` | `package-doc` |
| `godig package examples <path>` | `godig package examples github.com/samber/ro -o md` | `package-examples` |
| `godig package licenses <path>` | `godig package licenses github.com/samber/ro -o md` | `package-licenses` |
| `godig module info <path>` | `godig module info github.com/samber/ro -o md` | `module-info` |
| `godig module licenses <path>` | `godig module licenses github.com/samber/ro -o md` | `module-licenses` |
| `godig module readme <path>` | `godig module readme github.com/samber/ro -o md` | `module-readme` |
| `godig packages <path> [--limit N]` | `godig packages github.com/samber/ro -o md` | `packages` |
| `godig versions <path> [--filter <expr>] [--limit N]` | `godig versions github.com/samber/ro -o md` | `versions` |
| `godig imported-by <path> [--limit N]` | `godig imported-by github.com/samber/ro --limit 20 -o md` | `imported-by` |
| `godig symbols <path> [--goos <os>] [--goarch <arch>] [--limit N]` | `godig symbols github.com/samber/ro -o md` | `symbols` |
| `godig vulns <path>` | `godig vulns github.com/samber/ro -o md` | `vulns` |

### Tips

- **Start with `overview`** — one call returns a compact summary (metadata, latest + recent versions, license types, vulnerabilities). Reach for `doc`/`examples`/`module readme`/`licenses` (LARGE) only when the full text is needed.
- **Always pass `-o md`** so results render as Markdown (tables, or raw doc/README) in the chat. Other formats exist (`table` default, `json`, `raw`) but prefer `md` here.
- `<path>` is a full import path, e.g. `github.com/samber/lo`. Pass it as the positional argument (CLI) or as the `path` argument (MCP tool).
- Optional parameters map 1:1 to CLI flags and MCP tool arguments (`version`, `module`, `limit`, `filter`, `goos`, `goarch`, ...).
- `--filter` is a **Go boolean expression** over item fields (functions: `contains`, `hasPrefix`, `hasSuffix`, `matches`), e.g. `--filter 'hasPrefix(version, "v1.5")'` — not a regex.
- `--goos`/`--goarch` set the documentation/symbols build context (e.g. `linux`/`amd64`).
- Listing commands auto-paginate (return all results); use `--limit` to cap.
- `vulns` returns an empty list when a module has no known vulnerabilities.

### Examples

Always request Markdown output (`-o md`):

```bash
# Overview — start here (compact, one call)
godig overview github.com/samber/ro -o md

# Search
godig search "result option monad" --limit 5 -o md

# Package facets
godig package info github.com/samber/ro -o md
godig package doc github.com/samber/ro --format md -o md
godig package examples github.com/samber/ro -o md
godig package licenses github.com/samber/ro -o md

# Module facets
godig module info github.com/samber/ro -o md
godig module readme github.com/samber/ro -o md
godig module licenses github.com/samber/ro -o md

# Lists (auto-paginated; --limit to cap)
godig versions github.com/samber/ro -o md
godig packages github.com/samber/ro -o md
godig imported-by github.com/samber/ro --limit 20 -o md
godig symbols github.com/samber/ro -o md

# Filter (Go boolean expression over item fields) and build context (goos/goarch)
godig versions github.com/samber/ro --filter 'hasPrefix(version, "v0.3")' -o md
godig symbols github.com/samber/ro --goos linux --goarch amd64 -o md

# Vulnerabilities
godig vulns github.com/samber/ro -o md
```

### Sample output

`godig overview github.com/samber/ro -o md`

| field          | value                        |
| -------------- | ---------------------------- |
| latestVersion  | v0.3.0                       |
| licenses       | ["Apache-2.0"]               |
| modulePath     | github.com/samber/ro         |
| name           | ro                           |
| path           | github.com/samber/ro         |
| recentVersions | ["v0.3.0","v0.2.0","v0.1.0"] |
| repoUrl        | https://github.com/samber/ro |

`godig search ro --limit 3 -o md`

| modulePath | packagePath | synopsis | version |
| --- | --- | --- | --- |
| github.com/samber/ro | github.com/samber/ro |  | v0.3.0 |
| github.com/blevesearch/bleve | github.com/blevesearch/bleve/analysis/lang/ro |  | v1.0.14 |
| github.com/blevesearch/bleve/v2 | github.com/blevesearch/bleve/v2/analysis/lang/ro |  | v2.6.0 |

`godig package info github.com/samber/ro -o md`

| field             | value                |
| ----------------- | -------------------- |
| isLatest          | true                 |
| isStandardLibrary | false                |
| modulePath        | github.com/samber/ro |
| name              | ro                   |
| path              | github.com/samber/ro |
| version           | v0.3.0               |

`godig versions github.com/samber/ro --limit 3 -o md`

| commitTime | hasGoMod | latestVersion | modulePath | version |
| --- | --- | --- | --- | --- |
| 2026-03-02T15:16:08Z | true | v0.3.0 | github.com/samber/ro | v0.3.0 |
| 2025-10-25T22:20:38Z | true | v0.3.0 | github.com/samber/ro | v0.2.0 |
| 2025-10-14T12:21:03Z | true | v0.3.0 | github.com/samber/ro | v0.1.0 |

`godig imported-by github.com/samber/ro --limit 3 -o md`

| package                                |
| -------------------------------------- |
| github.com/CooperCorona/websocket      |
| github.com/CooperCorona/websocket/test |
| github.com/samber/ro/ee/plugins/otel   |

`godig vulns github.com/dgrijalva/jwt-go -o md`

| details | fixedVersion | id | summary |
| --- | --- | --- | --- |
| Authorization bypass in github.com/dgrijalva/jwt-go |  | GO-2020-0017 |  |

`godig package licenses github.com/samber/ro -o md`

| contents                                 | filePath | types          |
| ---------------------------------------- | -------- | -------------- |
| Apache License Version 2.0 … (full text) | LICENSE  | ["Apache-2.0"] |

`godig module info github.com/samber/ro -o md`

| field             | value                        |
| ----------------- | ---------------------------- |
| commitTime        | 2026-03-02T15:16:08Z         |
| hasGoMod          | true                         |
| isLatest          | true                         |
| isRedistributable | true                         |
| path              | github.com/samber/ro         |
| repoUrl           | https://github.com/samber/ro |
| version           | v0.3.0                       |

`godig packages github.com/samber/ro --limit 4 -o md`

| isRedistributable | name | path | synopsis |
| --- | --- | --- | --- |
| true | ro | github.com/samber/ro |  |
| true | constraints | github.com/samber/ro/internal/constraints |  |
| true | xatomic | github.com/samber/ro/internal/xatomic |  |
| true | xerrors | github.com/samber/ro/internal/xerrors |  |

`godig symbols github.com/samber/ro --limit 4 -o md`

| kind     | name              | parent          | synopsis                  |
| -------- | ----------------- | --------------- | ------------------------- |
| Type     | Backpressure      | Backpressure    | type Backpressure int8    |
| Constant | BackpressureBlock | Backpressure    | const BackpressureBlock   |
| Constant | BackpressureDrop  | Backpressure    | const BackpressureDrop    |
| Type     | ConcurrencyMode   | ConcurrencyMode | type ConcurrencyMode int8 |

`godig package doc <path> --format md -o md`, `godig package examples <path> -o md` and `godig module readme <path> -o md` return raw Markdown (long output), e.g.:

```markdown
# package ro

## Constants

...
```

`godig module licenses <path> -o md` mirrors `package licenses` (full license text).

---

This skill is not exhaustive. `godig --help` and each sub-command's `--help` list current flags and output formats; the data mirrors what [pkg.go.dev](https://pkg.go.dev) exposes.

If you encounter a bug or unexpected behavior in `godig`, open an issue at <https://github.com/samber/godig/issues>.
