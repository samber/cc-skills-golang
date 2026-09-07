---
description: Embedded Go skill routing rules — applies to every Go file in the project
alwaysApply: true
globs:
  - "**/*.go"
  - "**/go.mod"
  - "**/go.sum"
  - "**/go.work"
---

# Golang Skills — Always Load Rules

This rule embeds the skill-routing logic directly. It applies to every Go file in the project, ensuring the right Go skills trigger on every Go task without an extra skill load.

## Skill Loading Rules

For each Go task, load the **primary skill** and all applicable **secondary skills** at the same time. Do not wait — load them together at the start.

| Intent | Primary Skill | Also Load |
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
| Refactor or restructure existing code | `golang-refactoring` | `golang-naming`, `golang-code-style`, `golang-project-layout` |
| Configure golangci-lint | `golang-lint` | `golang-code-style` |
| Write godoc / README / CHANGELOG | `golang-documentation` | `golang-naming` |
| Set up a new project structure | `golang-project-layout` | `golang-design-patterns`, `golang-dependency-injection`, `golang-lint` |
| Set up CI/CD pipeline | `golang-continuous-integration` | `golang-lint`, `golang-security` |
| Choose a library | `golang-popular-libraries` | relevant library-specific skill |
| Look up a package's docs, versions, importers, or CVEs | `golang-pkg-go-dev` | `golang-dependency-management` |
| Navigate, diagnose, or refactor local code | `golang-gopls` | — |
| Adopt new Go language features | `golang-modernize` | `golang-lint` |
| Use samber/lo (slice/map helpers) | `golang-samber-lo` | `golang-data-structures`, `golang-performance` |
| Use samber/oops (structured errors) | `golang-samber-oops` | `golang-error-handling` |
| Use log/slog | `golang-samber-slog` | `golang-observability`, `golang-error-handling` |
| Use dependency injection | `golang-dependency-injection` | `golang-google-wire` or `golang-uber-dig` or `golang-uber-fx` or `golang-samber-do` |

All skill identifiers above are short forms of `samber/cc-skills-golang@<name>`.

## Competing Clusters — Boundary Lines

Key clusters and their owners:

- **Performance**: `golang-performance` (optimization) · `golang-benchmark` (measurement) · `golang-troubleshooting` (root cause) · `golang-observability` (always-on production)
- **DI**: `golang-dependency-injection` (concepts/decision) · `golang-google-wire` (compile-time) · `golang-uber-dig` (runtime reflection) · `golang-uber-fx` (lifecycle) · `golang-samber-do` (type-safe container)
- **samber/\***: `golang-samber-lo` (finite transforms) · `golang-samber-ro` (reactive streams) · `golang-samber-mo` (monadic types)
- **Errors**: `golang-error-handling` (idioms) · `golang-samber-oops` (structured errors) · `golang-safety` (prevent panics)
- **Style**: `golang-code-style` · `golang-naming` · `golang-lint` · `golang-documentation`
- **CLI**: `golang-cli` (architecture) · `golang-spf13-cobra` (command tree) · `golang-spf13-viper` (config layering)
- **Package lookup**: `golang-pkg-go-dev` (query pkg.go.dev) · `golang-gopls` (navigate local build) · `golang-popular-libraries` (which lib) · `golang-dependency-management` (manage go.mod) · `golang-security` (CVE scan)
- **Gap — type vs arch**: `golang-structs-interfaces` vs `golang-design-patterns`
- **Gap — goroutine vs cancel**: `golang-concurrency` + `golang-context` — load both when cancelling goroutines via context
- **Gap — correctness vs threat**: `golang-safety` (internal bugs) vs `golang-security` (external threats)
- **Gap — features vs rules**: `golang-modernize` (language adoption) vs `golang-lint` (static analysis config)
- **Gap — process vs target rules**: `golang-refactoring` (safe process) vs `golang-naming`/`golang-code-style`/`golang-project-layout`/`golang-design-patterns`/`golang-modernize` (target shape) — load `golang-refactoring` alongside whichever owns the target shape

## Code Navigation with gopls

`gopls` gives semantic code intelligence for Go — go-to-definition, find references, diagnostics, package API, symbol search, refactoring. See `samber/cc-skills-golang@golang-gopls` skill for the three ways to reach it (MCP server, native LSP tool, CLI), capability matrix, and efficient workflows.

`gopls` only reasons about code present and resolvable in your local build: workspace plus every dependency exactly as pinned in `go.sum` (including `replace` directives). For facts not tied to your local build — version history, licenses, ecosystem-wide importers, a package you haven't added yet — use `golang-pkg-go-dev` (`godig`).

## `godig` vs gopls vs Context7 vs govulncheck

| Task | Tool |
| --- | --- |
| Find where a symbol is defined in your repo | `gopls` |
| Understand a file's intra-package deps | `gopls` |
| Jump into a dependency's exact resolved source (incl. forks/replace) | `gopls` |
| Find every call site in your code referencing a dep's symbol | `gopls` |
| Get compiler diagnostics right after an edit | `gopls` |
| Check if current build reaches a known vulnerability (mid-edit) | `gopls` |
| Rename, extract, inline, or refactor local code | `gopls` |
| Whole-tree vulnerability audit (CI, periodic sweep) | `govulncheck` |
| List available versions of a published package | `godig` |
| Check known CVEs for a package/version not yet added | `godig` |
| See exported symbols/signatures of a published package | `godig` |
| Get runnable code examples for a symbol | `godig` |
| Read a package's rendered README/docs | `godig` |
| See who imports a package across public ecosystem | `godig` |
| Search for a package or library candidate | `godig` |
| Check a package's or module's license | `godig` |
| Get docs for non-Go lib or Go module not on pkg.go.dev | Context7 |

## Categories at a Glance

| Category | Skills |
| --- | --- |
| Code Quality | `golang-code-style` `golang-documentation` `golang-error-handling` `golang-lint` `golang-naming` `golang-safety` `golang-security` `golang-structs-interfaces` |
| Architecture & Design | `golang-concurrency` `golang-context` `golang-data-structures` `golang-database` `golang-dependency-injection` `golang-design-patterns` `golang-modernize` `golang-refactoring` |
| QA & Performance | `golang-benchmark` `golang-observability` `golang-performance` `golang-testing` `golang-troubleshooting` |
| Project Setup | `golang-cli` `golang-continuous-integration` `golang-dependency-management` `golang-gopls` `golang-pkg-go-dev` `golang-popular-libraries` `golang-project-layout` `golang-stay-updated` |
| APIs | `golang-graphql` `golang-grpc` `golang-swagger` |
| Dependency Injection | `golang-dependency-injection` `golang-google-wire` `golang-uber-dig` `golang-uber-fx` `golang-samber-do` |
| Frameworks | `golang-spf13-cobra` `golang-spf13-viper` |
| samber/\* | `golang-samber-do` `golang-samber-hot` `golang-samber-lo` `golang-samber-mo` `golang-samber-oops` `golang-samber-ro` `golang-samber-slog` |
| Testing | `golang-stretchr-testify` `golang-testing` |
