---
name: golang-how-to
description: "Golang skills orchestrator — always active on any Golang coding, review, debug, or setup task. Reads the task context and loads the most relevant skills from samber/cc-skills-golang, often multiple at once: writing a gRPC service loads golang-grpc + golang-testing + golang-error-handling; debugging a panic loads golang-troubleshooting + golang-safety; auditing security loads golang-security + golang-lint + golang-safety. Also: disambiguates competing clusters when two skills seem to overlap (performance vs benchmark vs troubleshooting, samber/lo vs mo vs ro, DI cluster, safety vs security), and configures CLAUDE.md or AGENTS.md to force-trigger skills in a project (/golang-how-to configure)."
user-invocable: true
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents. Requires git.
metadata:
  author: samber
  version: "1.2.0"
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
allowed-tools: Read Edit Write Glob Grep Bash(go:*) Bash(git:*) Agent AskUserQuestion LSP Bash(gopls:*) mcp__gopls__*
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
| Navigate, diagnose, or refactor local code (definitions, references, rename) | `golang-gopls` | — |
| Adopt new Go language features | `golang-modernize` | `golang-lint` |
| Use samber/lo (slice/map helpers) | `golang-samber-lo` | `golang-data-structures`, `golang-performance` |
| Use samber/oops (structured errors) | `golang-samber-oops` | `golang-error-handling` |
| Use log/slog | `golang-samber-slog` | `golang-observability`, `golang-error-handling` |
| Use dependency injection | `golang-dependency-injection` | `golang-google-wire` or `golang-uber-dig` or `golang-uber-fx` or `golang-samber-do` |

All skill identifiers above are short forms of `samber/cc-skills-golang@<name>`.

## Code navigation with gopls

`gopls` gives semantic code intelligence for Go — go-to-definition, find references, diagnostics, package API, symbol search, refactoring. → See `samber/cc-skills-golang@golang-gopls` skill for the three ways to reach it (its own MCP server, the native `LSP` tool, and its CLI), the full capability matrix, and efficient read/edit workflows.

`gopls` only reasons about code that is present and resolvable in the local build: your workspace plus every dependency exactly as pinned in `go.sum` (including `replace` directives). For any fact that isn't tied to your local build — version history, licenses, ecosystem-wide importers, a package you haven't added yet — use `golang-pkg-go-dev` (`godig`). See the `godig` vs gopls vs Context7 vs govulncheck section below for the full boundary.

## `godig` vs gopls vs Context7 vs govulncheck

Four tools can answer "is this dependency OK to use," and they don't overlap as much as they look:

- **Context7** is a general-purpose, cross-language documentation fetcher — useful when no more specific source exists. For a Go package or module, `godig` is almost always the better choice: it pulls **structured, Go-specific data** straight from pkg.go.dev — exact versions, exported symbols with signatures, runnable examples, `imported-by`, and known vulnerabilities — rather than Context7's generic scraped/curated docs, which don't expose that structure and can lag or miss lesser-known Go modules. Reach for Context7 only when a dependency's documentation genuinely doesn't exist or isn't indexed on pkg.go.dev.
- **`godig`** answers questions about the **published ecosystem**: any Go package or module, whether or not it's in your `go.mod` yet — it calls the remote pkg.go.dev API and never touches your local checkout. Its `vulns` command reports CVEs known for a package/version in isolation, regardless of whether your build actually reaches the vulnerable code path.
- **`gopls`** (→ `samber/cc-skills-golang@golang-gopls`, via its MCP server, the native `LSP` tool, or its CLI) answers questions about **your specific build**: your code plus every dependency exactly as pinned in `go.sum`, including `replace` directives pointing at forks or local paths — neither `godig` nor Context7 can see that. Its `go_vulncheck` operation runs a single, on-demand reachability check against the workspace as it stands right now.
- **`govulncheck`** (the standalone CLI, wrapped by the `samber/cc-skills-golang@golang-security` skill) is the whole-tree audit: it walks the entire module's call graph to confirm which known vulnerabilities are actually reachable, and is the tool of record for CI gates and periodic security sweeps — `gopls`'s `go_vulncheck` is a lighter-weight, single-shot version of the same analysis for use mid-edit.

Pick by task:

| Task | Tool | How |
| --- | --- | --- |
| Find where a symbol is defined in your own repo | `gopls` | `samber/cc-skills-golang@golang-gopls` — `go_search`, then `go_file_context` |
| Understand a file's intra-package dependencies | `gopls` | `samber/cc-skills-golang@golang-gopls` — `go_file_context` |
| Jump into a dependency's exact resolved source (incl. forks/`replace`d versions) | `gopls` | `samber/cc-skills-golang@golang-gopls` — `go_package_api`, or the native `LSP` tool's `goToDefinition` |
| Find every call site in your own code that references a dependency's symbol | `gopls` | `samber/cc-skills-golang@golang-gopls` — `go_symbol_references` — `godig`'s `imported-by` only lists public _packages_, not call sites in your repo |
| Get compiler diagnostics right after an edit | `gopls` | `samber/cc-skills-golang@golang-gopls` — `go_diagnostics` (MCP), or automatic with the native `LSP` tool |
| Check whether your current build can reach a known vulnerability, mid-edit | `gopls` | `samber/cc-skills-golang@golang-gopls` — `go_vulncheck` |
| Rename, extract, inline, or otherwise refactor local code | `gopls` | `samber/cc-skills-golang@golang-gopls` — safe rename, `refactor.*` code actions |
| Whole-tree vulnerability audit across the module (CI, periodic sweep) | `govulncheck` | `samber/cc-skills-golang@golang-security` skill — `govulncheck ./...` |
| List available versions of a published package | `godig` | `godig versions <path>` |
| Check known CVEs for a package/version you haven't added yet | `godig` | `godig vulns <path>` |
| See exported symbols/signatures of a published package | `godig` | `godig symbols` / `symbol doc` |
| Get runnable code examples for a symbol | `godig` | `godig symbol examples` |
| Read a package's rendered README/docs | `godig` | `godig module readme` / `package doc` |
| See who imports a package across the whole public ecosystem | `godig` | `godig imported-by` |
| Search for a package or library candidate | `godig` | `godig search` |
| Check a package's or module's license | `godig` | `godig package licenses` / `module licenses` |
| Get docs for a non-Go library, or a Go module not indexed on pkg.go.dev | Context7 | `resolve-library-id` / `query-docs` |

See the `samber/cc-skills-golang@golang-pkg-go-dev` skill for the full `godig` command reference, and the `samber/cc-skills-golang@golang-security` skill for the whole-tree `govulncheck` remediation workflow.

## Categories at a glance

Full catalog with "use when" hooks: [by-category.md](references/by-category.md)

| Category | Skills |
| --- | --- |
| Code Quality | `golang-code-style` `golang-documentation` `golang-error-handling` `golang-lint` `golang-naming` `golang-safety` `golang-security` `golang-structs-interfaces` |
| Architecture & Design | `golang-concurrency` `golang-context` `golang-data-structures` `golang-database` `golang-dependency-injection` `golang-design-patterns` `golang-modernize` |
| QA & Performance | `golang-benchmark` `golang-observability` `golang-performance` `golang-testing` `golang-troubleshooting` |
| Project Setup | `golang-cli` `golang-continuous-integration` `golang-dependency-management` `golang-gopls` `golang-pkg-go-dev` `golang-popular-libraries` `golang-project-layout` `golang-stay-updated` |
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
- **Package lookup**: `golang-pkg-go-dev` (query pkg.go.dev for an existing path: versions/docs/symbols/importers/CVEs) · `golang-gopls` (navigate/refactor your locally resolved build) · `golang-popular-libraries` (which library to adopt) · `golang-dependency-management` (manage go.mod) · `golang-security` (whole-tree CVE scan)
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
