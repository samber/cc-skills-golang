---
name: golang-how-to
description: "Golang skills orchestrator — always active on any Golang coding, review, debug, or setup task. Reads the task context and loads the most relevant skills from samber/cc-skills-golang, often multiple at once: writing a gRPC service loads golang-grpc + golang-testing + golang-error-handling; debugging a panic loads golang-troubleshooting + golang-safety; auditing security loads golang-security + golang-lint + golang-safety. Also: disambiguates competing clusters when two skills seem to overlap (performance vs benchmark vs troubleshooting, samber/lo vs mo vs ro, DI cluster, safety vs security), and configures CLAUDE.md or AGENTS.md to force-trigger skills in a project (/golang-how-to configure)."
user-invocable: true
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents. Requires git.
metadata:
  author: samber
  version: "1.1.1"
  openclaw:
    emoji: "🧭"
    homepage: https://github.com/samber/cc-skills-golang
    requires:
      bins:
        - go
        - gopls
    install:
      - kind: go
        package: golang.org/x/tools/gopls@latest
        bins: [gopls]
allowed-tools: Read Edit Write Glob Grep Bash(git:*) Agent AskUserQuestion LSP Bash(gopls:*) mcp__gopls__*
---

**Persona:** You are a Go skills orchestrator. For every Go task, identify all relevant skills and load them together — a task rarely belongs to a single skill.

**Dependencies:** `gopls` — `go install golang.org/x/tools/gopls@latest`; the built-in `LSP` tool also needs `ENABLE_LSP_TOOL=1` and a Go language server wired (see [Code navigation with gopls](#code-navigation-with-gopls)).

**Modes:**

- **Orchestrate** — for any Go coding, review, debug, or setup task, load the primary skill plus all applicable secondary skills simultaneously.
- **Disambiguate** — when two skills seem to overlap, show the boundary table. See [disambiguation.md](references/disambiguation.md).
- **Configure** — add a `## Required Go skills` block to the project's `CLAUDE.md` or `AGENTS.md`. Follow [project-config.md](references/project-config.md).

## Skill loading

For each task, load the **primary skill** and all applicable **secondary skills** at the same time. Do not wait — load them together at the start.

| Intent | Primary | Also load |
| --- | --- | --- |
| Design an API, choose a pattern | `golang-design-patterns` | `golang-structs-interfaces`, `golang-naming` |
| Name a type, function, or package | `golang-naming` | `golang-code-style` |
| Handle errors idiomatically | `golang-error-handling` | `golang-safety` (nil-heavy code) |
| Write goroutines, channels, sync | `golang-concurrency` | `golang-context` (if cancellation) |
| Pass deadlines / cancel operations | `golang-context` | `golang-concurrency` (if goroutines) |
| Design structs, embed, use interfaces | `golang-structs-interfaces` | `golang-design-patterns` |
| Database queries and transactions | `golang-database` | `golang-error-handling`, `golang-security` |
| Build a gRPC service | `golang-grpc` | `golang-testing`, `golang-error-handling` |
| Build a GraphQL API | `golang-graphql` | `golang-testing`, `golang-error-handling` |
| Build a CLI command tree | `golang-spf13-cobra` | `golang-cli`, `golang-spf13-viper` (if config) |
| Layer config from flags/env/file | `golang-spf13-viper` | `golang-spf13-cobra` |
| Write tests | `golang-testing` | `golang-stretchr-testify` (if using testify) |
| Apply optimization patterns | `golang-performance` | `golang-benchmark` (measure first) |
| Measure with pprof / benchstat | `golang-benchmark` | `golang-performance` (fix), `golang-troubleshooting` (root cause) |
| Debug a panic or unexpected behavior | `golang-troubleshooting` | `golang-safety`, `golang-benchmark` (if perf-related) |
| Monitor in production | `golang-observability` | `golang-performance` (if SLO breach) |
| Audit security vulnerabilities | `golang-security` | `golang-safety`, `golang-lint` |
| Review formatting and style | `golang-code-style` | `golang-naming`, `golang-lint` |
| Configure golangci-lint | `golang-lint` | `golang-code-style` |
| Write godoc / README / CHANGELOG | `golang-documentation` | `golang-naming` |
| Set up a new project structure | `golang-project-layout` | `golang-design-patterns`, `golang-dependency-injection`, `golang-lint` |
| Set up CI/CD pipeline | `golang-continuous-integration` | `golang-lint`, `golang-security` |
| Choose a library | `golang-popular-libraries` | relevant library-specific skill |
| Look up a package's docs, versions, importers, or CVEs | `golang-pkg-go-dev` | `golang-dependency-management` |
| Adopt new Go language features | `golang-modernize` | `golang-lint` |
| Use samber/lo (slice/map helpers) | `golang-samber-lo` | `golang-data-structures`, `golang-performance` |
| Use samber/oops (structured errors) | `golang-samber-oops` | `golang-error-handling` |
| Use log/slog | `golang-samber-slog` | `golang-observability`, `golang-error-handling` |
| Use dependency injection | `golang-dependency-injection` | `golang-google-wire` or `golang-uber-dig` or `golang-uber-fx` or `golang-samber-do` |

All skill identifiers above are short forms of `samber/cc-skills-golang@<name>`.

## Code navigation with gopls

`gopls` gives semantic code intelligence for Go — go-to-definition, find references, diagnostics, package API, symbol search. It reaches an agent through two different mechanisms; they solve different problems and are worth wiring both.

**gopls's own MCP server** — built for AI agents specifically, and the default choice for most tasks. Register it with `claude mcp add gopls -- gopls mcp` (requires `gopls` v0.20+ on PATH; the detached `gopls mcp` mode only sees saved files, which is fine for an agent-only workflow with no attached editor). Its tools take names, paths, and queries rather than raw cursor positions, so they fit how an agent naturally asks questions. Two workflows:

- **Read** — `go_workspace` first, to learn the workspace layout (module/workspace/GOPATH). `go_search` fuzzy-finds a symbol by name. `go_file_context` shows a file's intra-package dependencies — use it right after reading any Go file for the first time. `go_package_api` shows a package's public API — most useful for third-party dependencies or other packages in a monorepo.
- **Edit** — before touching a symbol's definition, `go_symbol_references` finds every call site so you can judge the blast radius. After every edit, `go_diagnostics` on the changed files is mandatory — fix what it reports, then re-run it. If the edit touched `go.mod` dependencies, `go_vulncheck` afterwards checks the whole workspace for reachable vulnerabilities in the new dependency graph. Then run `go test <packagePath>` for the changed packages — not `./...` unless asked, since a full-repo run slows down the iteration loop.

**The native `LSP` tool** — Claude Code's built-in editor-style integration. It is **not enabled by default**: set `ENABLE_LSP_TOOL=1`, install `gopls`, and wire it as the Go language server by installing the official `gopls-lsp@claude-plugins-official` marketplace plugin. Its operations (`goToDefinition`, `findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`, `goToImplementation`, call hierarchy) are keyed by `line`/`character`, so they're most useful once you already have a location — typically right after a grep or read — rather than as a first search. Its unique value the MCP server doesn't replicate: compiler diagnostics get pushed into context automatically after every edit, with no explicit `go_diagnostics` call needed.

Either way, `gopls` only reasons about code that is present and resolvable in the local build: your workspace plus every dependency exactly as pinned in `go.sum` (including `replace` directives). `go_vulncheck` only flags what your _current_ build actually reaches — for a specific published package/version you haven't added yet, or for a comprehensive whole-tree `govulncheck` audit, see `samber/cc-skills-golang@golang-pkg-go-dev` and `samber/cc-skills-golang@golang-security` respectively. For any fact that isn't tied to your local build — version history, licenses, ecosystem-wide importers — use `golang-pkg-go-dev` (`godig`). See that skill's `godig` vs gopls section for the full boundary.

## Categories at a glance

Full catalog with "use when" hooks: [by-category.md](references/by-category.md)

| Category | Skills |
| --- | --- |
| Code Quality | `golang-code-style` `golang-documentation` `golang-error-handling` `golang-lint` `golang-naming` `golang-safety` `golang-security` `golang-structs-interfaces` |
| Architecture & Design | `golang-concurrency` `golang-context` `golang-data-structures` `golang-database` `golang-dependency-injection` `golang-design-patterns` `golang-modernize` |
| QA & Performance | `golang-benchmark` `golang-observability` `golang-performance` `golang-testing` `golang-troubleshooting` |
| Project Setup | `golang-cli` `golang-continuous-integration` `golang-dependency-management` `golang-pkg-go-dev` `golang-popular-libraries` `golang-project-layout` `golang-stay-updated` |
| APIs | `golang-graphql` `golang-grpc` `golang-swagger` |
| Dependency Injection | `golang-dependency-injection` `golang-google-wire` `golang-uber-dig` `golang-uber-fx` `golang-samber-do` |
| Frameworks | `golang-spf13-cobra` `golang-spf13-viper` |
| samber/\* | `golang-samber-do` `golang-samber-hot` `golang-samber-lo` `golang-samber-mo` `golang-samber-oops` `golang-samber-ro` `golang-samber-slog` |
| Testing | `golang-stretchr-testify` `golang-testing` |

## Competing clusters — boundary lines

Full boundary tables with routing examples: [disambiguation.md](references/disambiguation.md)

Key clusters and their owners:

- **Performance**: `golang-performance` (optimization patterns) · `golang-benchmark` (measurement) · `golang-troubleshooting` (root cause) · `golang-observability` (always-on production)
- **DI**: `golang-dependency-injection` (concepts/decision) · `golang-google-wire` (compile-time) · `golang-uber-dig` (runtime reflection) · `golang-uber-fx` (lifecycle framework) · `golang-samber-do` (type-safe container)
- **samber/\***: `golang-samber-lo` (finite transforms) · `golang-samber-ro` (reactive streams) · `golang-samber-mo` (monadic types)
- **Errors**: `golang-error-handling` (idioms) · `golang-samber-oops` (structured errors) · `golang-safety` (prevent panics)
- **Style**: `golang-code-style` · `golang-naming` · `golang-lint` · `golang-documentation`
- **CLI**: `golang-cli` (architecture) · `golang-spf13-cobra` (command tree) · `golang-spf13-viper` (config layering)
- **Package lookup**: `golang-pkg-go-dev` (query pkg.go.dev for an existing path: versions/docs/symbols/importers/CVEs) · `golang-popular-libraries` (which library to adopt) · `golang-dependency-management` (manage go.mod) · `golang-security` (whole-tree CVE scan)
- **Gap — type vs arch**: `golang-structs-interfaces` (type design) vs `golang-design-patterns` (architectural patterns)
- **Gap — goroutine vs cancel**: `golang-concurrency` + `golang-context` — load both when cancelling goroutines via context
- **Gap — correctness vs threat**: `golang-safety` (internal bugs) vs `golang-security` (external threats)
- **Gap — features vs rules**: `golang-modernize` (language adoption) vs `golang-lint` (static analysis config)

## Configure mode

Force-trigger specific skills in a project's `CLAUDE.md` or `AGENTS.md` so they always load.

When invoked as `/golang-how-to configure`, follow [project-config.md](references/project-config.md).

---

This skill is not exhaustive. Refer to individual skill files and the official Go documentation for detailed guidance.

If you encounter a bug or unexpected behavior in this skill plugin, open an issue at <https://github.com/samber/cc-skills-golang/issues>.
