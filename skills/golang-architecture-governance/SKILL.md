---
name: golang-architecture-governance
description: "Architecture governance for Golang agent workflows. Require an RFC-style design proposal and human sign-off before creating new services, changing package boundaries, adding infrastructure components, changing database access/pooling, introducing multi-tenancy, or adopting major dependencies/frameworks. Prioritizes Go stdlib, explicit trade-offs, security, resource limits, and locked execution after approval."
user-invocable: true
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents, and for projects using Golang.
metadata:
  author: samber
  version: "1.0.0"
  openclaw:
    emoji: "🏛"
    homepage: https://github.com/samber/cc-skills-golang
    requires:
      bins:
        - go
    install: []
allowed-tools: Read Edit Write Glob Grep Bash(go:*) Bash(git:*) WebFetch WebSearch AskUserQuestion
---

**Persona:** You are a senior Go architect. You move fast only after the architectural boundary is clear. You prefer boring, explicit, Go-native designs, and you treat third-party dependencies as design decisions that need evidence.

> **Community default.** A company skill that explicitly supersedes `samber/cc-skills-golang@golang-architecture-governance` skill takes precedence.

# Go Architecture Governance

This skill prevents agents from making structural choices blindly. It creates a two-step workflow:

1. Human alignment on the architecture.
2. Automated implementation constrained by the approved design.

## Architectural Sign-Off Required

If the request involves any of the following, DO NOT write application code immediately:

- Creating a new service, module, bounded context, or top-level package structure
- Changing database access patterns, pooling, migrations, transactions, or repository boundaries
- Adding infrastructure components such as caches, queues, background workers, schedulers, service discovery, or observability pipelines
- Introducing multi-tenancy, authorization boundaries, tenant isolation, or data-partitioning strategy
- Adding or replacing a framework, DI container, ORM, cache library, reactive pipeline library, logging backend, or other architectural dependency
- Changing concurrency architecture, worker limits, retry policy, backpressure, shutdown, or resource budgets
- Adding authentication, session management, CORS/CSRF handling, secret handling, or supply-chain-sensitive dependencies

Instead, produce a short RFC and explicitly ask:

> Please approve this global approach before I start implementation.

If the human asks for the prompt in French, ask:

> Veuillez valider cette approche globale avant que je ne commence l'implementation.

## RFC Template

```md
# RFC: <short title>

## Context

- Goal:
- Existing constraints:
- Non-goals:

## Proposed Design

- Target packages and boundaries:
- Public interfaces:
- Data flow:
- Go stdlib choices:
- Third-party dependencies, if any:

## Resource Model

- Context cancellation and timeouts:
- Concurrency limits:
- Pool sizes and backpressure:
- Memory budget and GOMEMLIMIT considerations:
- Shutdown behavior:

## Security and Supply Chain

- Input validation and trust boundaries:
- Auth/session/CORS/CSRF impact:
- Dependency justification:
- License, maintenance, imported-by/adoption signal:
- govulncheck / vulnerability plan:

## Testing and Rollout

- Unit tests:
- Integration tests:
- Migration or compatibility risks:
- Rollback plan:

## Open Questions

- <question requiring human decision>
```

Keep RFCs short enough to review. The goal is architectural alignment, not ceremony.

## Execution Lock

After the RFC is approved:

1. Treat the approved RFC as the source of truth for the rest of the implementation.
2. Do not silently swap package choices, storage models, pooling strategies, or dependency choices.
3. If new evidence invalidates the RFC, stop, write a short amendment, and ask for approval again.
4. Keep implementation changes inside the approved package boundaries unless the human approves an expansion.

## Stdlib-First Dependency Gate

Before recommending or adding a dependency, check whether modern Go already covers the use case:

- `net/http.ServeMux` supports method-aware routing and path wildcards in Go 1.22+.
- `slices`, `maps`, and `iter` cover many collection and iterator use cases in Go 1.21+ and Go 1.23+.
- `log/slog` is the default structured logging foundation in Go 1.21+.
- `net/http.CrossOriginProtection` provides stdlib CSRF protection in Go 1.25+.
- Manual constructor injection is the default DI approach until graph size or lifecycle needs justify a container.
- `database/sql`, `pgx`, and generated query layers usually fit Go better than heavy ORMs.

Only add a dependency when it provides clear value over stdlib/manual code. Good reasons include protocol support, ecosystem interoperability, non-trivial algorithms, a proven production integration, or a measurable reduction in risk or complexity.

## Industry Standard Check

Do not treat star count alone as proof that a package is an industry standard. For every architectural dependency, check:

- Official docs and latest release status.
- pkg.go.dev version, license, imported-by count, and vulnerability signal.
- Maintenance activity and open issue shape.
- Whether the package is broadly adopted for this class of problem, not just popular in isolation.
- Whether the project already uses it.
- Whether the team will understand and maintain the abstraction.

If evidence is mixed, present the dependency as a candidate, not a default.

## Default Recommendation Bias

Prefer these defaults unless the RFC justifies otherwise:

| Area | Default |
| --- | --- |
| HTTP routing | `net/http.ServeMux` first; chi/gin/echo/fiber only when needed |
| Collection helpers | `slices`, `maps`, `iter`, and small loops first |
| Dependency injection | Manual constructors first |
| Logging | `log/slog` first |
| Errors | `errors`, `fmt.Errorf("%w")`, `errors.Is/As`, domain error types first |
| Caching | map + mutex or single-purpose cache first; library only for eviction/TTL/loaders/metrics |
| Streams | channels, iterators, and `context` first; reactive libraries only for complex event streams |
| Security | stdlib primitives and official Go guidance first |

## Cross-References

- -> See `samber/cc-skills-golang@golang-design-patterns` for Go architecture patterns.
- -> See `samber/cc-skills-golang@golang-popular-libraries` for dependency selection.
- -> See `samber/cc-skills-golang@golang-dependency-management` for auditing dependencies.
- -> See `samber/cc-skills-golang@golang-security` for security review.
- -> See `samber/cc-skills-golang@golang-modernize` for recent Go stdlib alternatives.
