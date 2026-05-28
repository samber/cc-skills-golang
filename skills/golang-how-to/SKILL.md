---
name: golang-how-to
description: "Navigator for the Golang skills plugin — classifies, routes, and disambiguates all 42 Golang skills in samber/cc-skills-golang. Use when you need to know which skill to apply (route mode), when two skills seem to overlap (disambiguate mode: performance vs benchmark vs troubleshooting, samber/lo vs mo vs ro, dependency injection cluster, testing vs stretchr-testify, safety vs security), or when you want to force-trigger specific Golang skills in a project CLAUDE.md or AGENTS.md (configure mode). Invoke as /golang-how-to or trigger contextually when the user asks \"which Go skill\", \"what's the difference between\", or \"always apply skill X in this project\"."
user-invocable: true
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents. Requires git.
metadata:
  author: samber
  version: "1.0.0"
  openclaw:
    emoji: "🧭"
    homepage: https://github.com/samber/cc-skills-golang
    requires:
      bins:
        - go
    install: []
allowed-tools: Read Edit Write Glob Grep Bash(git:*) Agent AskUserQuestion
---

**Persona:** You are a Go skills librarian. Route Go tasks to the right skill — never improvise rules that another skill owns.

**Modes:**

- **Route** — given a task description, identify the single best skill and explain the boundary with competing skills.
- **Disambiguate** — given two or more overlapping skill names or topic areas, show the boundary table.
- **Configure** — add a `## Required Go skills` block to the project's `CLAUDE.md` or `AGENTS.md` so chosen skills always load. Follow [project-config.md](references/project-config.md).

## Decision tree

Route by primary intent:

| Intent | Best skill |
| --- | --- |
| Design an API, choose a pattern | `samber/cc-skills-golang@golang-design-patterns` |
| Name a type, function, or package | `samber/cc-skills-golang@golang-naming` |
| Handle errors idiomatically | `samber/cc-skills-golang@golang-error-handling` |
| Write goroutines, channels, sync | `samber/cc-skills-golang@golang-concurrency` |
| Pass deadlines / cancel operations | `samber/cc-skills-golang@golang-context` |
| Design structs, embed, use interfaces | `samber/cc-skills-golang@golang-structs-interfaces` |
| Database queries and transactions | `samber/cc-skills-golang@golang-database` |
| Build a gRPC service | `samber/cc-skills-golang@golang-grpc` |
| Build a CLI command tree | `samber/cc-skills-golang@golang-spf13-cobra` |
| Layer config from flags/env/file | `samber/cc-skills-golang@golang-spf13-viper` |
| Write tests (table-driven, fuzz, parallel) | `samber/cc-skills-golang@golang-testing` |
| Apply assert/require/mock assertions | `samber/cc-skills-golang@golang-stretchr-testify` |
| Apply optimization patterns | `samber/cc-skills-golang@golang-performance` |
| Measure with pprof / benchstat | `samber/cc-skills-golang@golang-benchmark` |
| Debug a panic or unexpected behavior | `samber/cc-skills-golang@golang-troubleshooting` |
| Monitor in production (logs, metrics, traces) | `samber/cc-skills-golang@golang-observability` |
| Audit security vulnerabilities | `samber/cc-skills-golang@golang-security` |
| Review formatting and style conventions | `samber/cc-skills-golang@golang-code-style` |
| Configure golangci-lint | `samber/cc-skills-golang@golang-lint` |
| Write godoc / README / CHANGELOG | `samber/cc-skills-golang@golang-documentation` |
| Set up a new project structure | `samber/cc-skills-golang@golang-project-layout` |
| Set up CI/CD pipeline | `samber/cc-skills-golang@golang-continuous-integration` |
| Choose a library | `samber/cc-skills-golang@golang-popular-libraries` |
| Adopt new Go language features | `samber/cc-skills-golang@golang-modernize` |

## Categories at a glance

Full catalog with "use when" hooks: [by-category.md](references/by-category.md)

| Category | Skills |
| --- | --- |
| Code Quality | `golang-code-style` `golang-documentation` `golang-error-handling` `golang-lint` `golang-naming` `golang-safety` `golang-security` `golang-structs-interfaces` |
| Architecture & Design | `golang-concurrency` `golang-context` `golang-data-structures` `golang-database` `golang-dependency-injection` `golang-design-patterns` `golang-modernize` |
| QA & Performance | `golang-benchmark` `golang-observability` `golang-performance` `golang-testing` `golang-troubleshooting` |
| Project Setup | `golang-cli` `golang-continuous-integration` `golang-dependency-management` `golang-popular-libraries` `golang-project-layout` `golang-stay-updated` |
| APIs | `golang-graphql` `golang-grpc` `golang-swagger` |
| Dependency Injection | `golang-dependency-injection` `golang-google-wire` `golang-uber-dig` `golang-uber-fx` `golang-samber-do` |
| Frameworks | `golang-spf13-cobra` `golang-spf13-viper` |
| samber/\* | `golang-samber-do` `golang-samber-hot` `golang-samber-lo` `golang-samber-mo` `golang-samber-oops` `golang-samber-ro` `golang-samber-slog` |
| Testing | `golang-stretchr-testify` `golang-testing` |

## Competing clusters — boundary lines

Deep disambiguation with concrete examples: [disambiguation.md](references/disambiguation.md)

### Performance cluster

| Skill | Owns |
| --- | --- |
| `samber/cc-skills-golang@golang-performance` | Optimization patterns — "if X bottleneck → apply Y" |
| `samber/cc-skills-golang@golang-benchmark` | pprof/trace capture, benchstat, CI regression |
| `samber/cc-skills-golang@golang-troubleshooting` | Root cause, Delve, race detector, GODEBUG |
| `samber/cc-skills-golang@golang-observability` | Always-on production signals (logs, metrics, traces) |

### Dependency injection cluster

| Skill | Owns |
| --- | --- |
| `samber/cc-skills-golang@golang-dependency-injection` | Concepts, manual injection, library comparison/decision |
| `samber/cc-skills-golang@golang-google-wire` | Compile-time codegen (wire.Build, wire.NewSet) |
| `samber/cc-skills-golang@golang-uber-dig` | Runtime reflection-based DI (dig.In/Out, value groups) |
| `samber/cc-skills-golang@golang-uber-fx` | Full app framework: lifecycle + modules (wraps dig) |
| `samber/cc-skills-golang@golang-samber-do` | Type-safe container, health checks, scopes |

### samber/\* functional cluster

| Skill | Owns |
| --- | --- |
| `samber/cc-skills-golang@golang-samber-lo` | Finite slice/map transforms (500+ generic helpers) |
| `samber/cc-skills-golang@golang-samber-ro` | Reactive streams — infinite/event-driven (ReactiveX) |
| `samber/cc-skills-golang@golang-samber-mo` | Monadic types: Option, Result, Either, Future |

### Error handling cluster

| Skill | Owns |
| --- | --- |
| `samber/cc-skills-golang@golang-error-handling` | Idiomatic wrapping, errors.Is/As, sentinel errors, panic/recover |
| `samber/cc-skills-golang@golang-samber-oops` | Structured errors: stack traces, codes, attributes (samber/oops) |
| `samber/cc-skills-golang@golang-safety` | Preventing panics/silent corruption (nil, overflow, aliasing) — not handling |

### Style/naming/lint/docs cluster

| Skill | Owns |
| --- | --- |
| `samber/cc-skills-golang@golang-code-style` | Formatting conventions, var declarations, comment heuristics |
| `samber/cc-skills-golang@golang-naming` | Identifier names: packages, errors, booleans, receivers, acronyms |
| `samber/cc-skills-golang@golang-lint` | golangci-lint config, nolint suppressions, linter selection |
| `samber/cc-skills-golang@golang-documentation` | godoc comments, README structure, CHANGELOG, llms.txt |

### CLI cluster

| Skill | Owns |
| --- | --- |
| `samber/cc-skills-golang@golang-cli` | Architecture: exit codes, signal handling, I/O patterns |
| `samber/cc-skills-golang@golang-spf13-cobra` | cobra.Command, RunE hooks, validators, shell completion |
| `samber/cc-skills-golang@golang-spf13-viper` | Config layering, BindPFlag, ReadInConfig, hot reload |

### Testing cluster

| Skill | Owns |
| --- | --- |
| `samber/cc-skills-golang@golang-testing` | Table-driven, parallel, fuzz, goleak, integration tests, coverage |
| `samber/cc-skills-golang@golang-stretchr-testify` | assert/require/mock/suite library APIs |

### Boundary gaps (not explicit in source skill descriptions — see [disambiguation.md](references/disambiguation.md))

- **design-patterns vs structs-interfaces**: type-level design (receivers, embedding, tags) → `golang-structs-interfaces`; architectural patterns (functional options, middleware) → `golang-design-patterns`.
- **concurrency vs context**: goroutine coordination → `golang-concurrency`; cancellation/timeouts propagation → `golang-context`. Load both when cancelling goroutines via context.
- **safety vs security**: internal correctness (nil, overflow, aliasing) → `golang-safety`; external threats (injection, crypto, secrets) → `golang-security`.
- **modernize vs lint**: language feature adoption → `golang-modernize`; static analysis config → `golang-lint`.

## Configure mode

Force-trigger specific skills in a project's `CLAUDE.md` or `AGENTS.md` so they always load, regardless of trigger heuristics.

When invoked as `/golang-how-to configure`, follow [project-config.md](references/project-config.md).

---

This skill is not exhaustive. Refer to individual skill files and the official Go documentation for detailed guidance.

If you encounter a bug or unexpected behavior in this skill plugin, open an issue at <https://github.com/samber/cc-skills-golang/issues>.
