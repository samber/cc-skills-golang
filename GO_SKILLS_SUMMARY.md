# Go Skills Summary

Generated from cc-skills-golang repository

- **Go Benchmarking & Performance Measurement**: Performance improvement does not exist without measures — if you can measure it, you can improve it. ([cc-skills-golang\skills\golang-benchmark\SKILL.md](cc-skills-golang\skills\golang-benchmark\SKILL.md))

- **Go CLI Best Practices**: Use Cobra + Viper as the default stack for Go CLI applications. Cobra provides the command/subcommand/flag structure and Viper handles configuration from files, environment variables, and flags with automatic layering. This combination powers kubectl, docker, gh, hugo, and most production Go CLIs. ([cc-skills-golang\skills\golang-cli\SKILL.md](cc-skills-golang\skills\golang-cli\SKILL.md))

- **Go Code Style**: Style rules that require human judgment — linters handle formatting, this skill handles clarity. For naming see `samber/cc-skills-golang@golang-naming` skill; for design patterns see `samber/cc-skills-golang@golang-design-patterns` skill; for struct/interface design see `samber/cc-skills-golang@gola ([cc-skills-golang\skills\golang-code-style\SKILL.md](cc-skills-golang\skills\golang-code-style\SKILL.md))

- **Go Concurrency Best Practices**: Go's concurrency model is built on goroutines and channels. Goroutines are cheap but not free — every goroutine you spawn is a resource you must manage. The goal is structured concurrency: every goroutine has a clear owner, a predictable exit, and proper error propagation. ([cc-skills-golang\skills\golang-concurrency\SKILL.md](cc-skills-golang\skills\golang-concurrency\SKILL.md))

- **Go context.Context Best Practices**: `context.Context` is Go's mechanism for propagating cancellation signals, deadlines, and request-scoped values across API boundaries and between goroutines. Think of it as the "session" of a request — it ties together every operation that belongs to the same unit of work. ([cc-skills-golang\skills\golang-context\SKILL.md](cc-skills-golang\skills\golang-context\SKILL.md))

- **Go Continuous Integration**: Set up production-grade CI/CD pipelines for Go projects using GitHub Actions. ([cc-skills-golang\skills\golang-continuous-integration\SKILL.md](cc-skills-golang\skills\golang-continuous-integration\SKILL.md))

- **Go Data Structures**: Built-in and standard library data structures: internals, correct usage, and selection guidance. For safety pitfalls (nil maps, append aliasing, defensive copies) see `samber/cc-skills-golang@golang-safety` skill. For channels and sync primitives see `samber/cc-skills-golang@golang-concurrency` skil ([cc-skills-golang\skills\golang-data-structures\SKILL.md](cc-skills-golang\skills\golang-data-structures\SKILL.md))

- **Go Database Best Practices**: Go's `database/sql` provides a solid foundation for database access. Use `sqlx` or `pgx` on top of it for ergonomics — never an ORM. ([cc-skills-golang\skills\golang-database\SKILL.md](cc-skills-golang\skills\golang-database\SKILL.md))

- **Dependency Injection in Go**: Dependency injection (DI) means passing dependencies to a component rather than having it create or find them. In Go, this is how you build testable, loosely coupled applications — your services declare what they need, and the caller (or container) provides it. ([cc-skills-golang\skills\golang-dependency-injection\SKILL.md](cc-skills-golang\skills\golang-dependency-injection\SKILL.md))

- **Go Dependency Management**: **Before running `go get` to add any new dependency, AI agents MUST ask the user for confirmation.** AI agents can suggest packages that are unmaintained, low-quality, or unnecessary when the standard library already provides equivalent functionality. Using `go get -u` to upgrade an existing depende ([cc-skills-golang\skills\golang-dependency-management\SKILL.md](cc-skills-golang\skills\golang-dependency-management\SKILL.md))

- **Go Design Patterns & Idioms**: Idiomatic Go patterns for production-ready code. For error handling details see the `samber/cc-skills-golang@golang-error-handling` skill; for context propagation see `samber/cc-skills-golang@golang-context` skill; for struct/interface design see `samber/cc-skills-golang@golang-structs-interfaces` s ([cc-skills-golang\skills\golang-design-patterns\SKILL.md](cc-skills-golang\skills\golang-design-patterns\SKILL.md))

- **Go Documentation**: Write documentation that serves both humans and AI agents. Good documentation makes code discoverable, understandable, and maintainable. ([cc-skills-golang\skills\golang-documentation\SKILL.md](cc-skills-golang\skills\golang-documentation\SKILL.md))

- **Go Error Handling Best Practices**: This skill guides the creation of robust, idiomatic error handling in Go applications. Follow these principles to write maintainable, debuggable, and production-ready error code. ([cc-skills-golang\skills\golang-error-handling\SKILL.md](cc-skills-golang\skills\golang-error-handling\SKILL.md))

- **Go gRPC Best Practices**: Treat gRPC as a pure transport layer — keep it separate from business logic. The official Go implementation is `google.golang.org/grpc`. ([cc-skills-golang\skills\golang-grpc\SKILL.md](cc-skills-golang\skills\golang-grpc\SKILL.md))

- **Go Linting**: `golangci-lint` is the standard Go linting tool. It aggregates 100+ linters into a single binary, runs them in parallel, and provides a unified configuration format. Run it frequently during development and always in CI. ([cc-skills-golang\skills\golang-linter\SKILL.md](cc-skills-golang\skills\golang-linter\SKILL.md))

- **Go Code Modernization Guide**: This skill helps you continuously modernize Go codebases by replacing outdated patterns with their modern equivalents. ([cc-skills-golang\skills\golang-modernize\SKILL.md](cc-skills-golang\skills\golang-modernize\SKILL.md))

- **Go Naming Conventions**: Go favors short, readable names. Capitalization controls visibility — uppercase is exported, lowercase is unexported. All identifiers MUST use MixedCaps, NEVER underscores. ([cc-skills-golang\skills\golang-naming\SKILL.md](cc-skills-golang\skills\golang-naming\SKILL.md))

- **Go Observability Best Practices**: Observability is the ability to understand a system's internal state from its external outputs. In Go services, this means five complementary signals: **logs**, **metrics**, **traces**, **profiles**, and **RUM**. Each answers different questions, and together they give you full visibility into both  ([cc-skills-golang\skills\golang-observability\SKILL.md](cc-skills-golang\skills\golang-observability\SKILL.md))

- **Go Performance Optimization**: 1. **Profile before optimizing** — intuition about bottlenecks is wrong ~80% of the time. Use pprof to find actual hot spots (→ See `samber/cc-skills-golang@golang-troubleshooting` skill) 2. **Allocation reduction yields the biggest ROI** — Go's GC is fast but not free. Reducing allocations per requ ([cc-skills-golang\skills\golang-performance\SKILL.md](cc-skills-golang\skills\golang-performance\SKILL.md))

- **Go Libraries and Frameworks Recommendations**: When recommending libraries, prioritize: ([cc-skills-golang\skills\golang-popular-libraries\SKILL.md](cc-skills-golang\skills\golang-popular-libraries\SKILL.md))

- **Go Project Layout**: When starting a new project, **ask the developer** what software architecture they prefer (clean architecture, hexagonal, DDD, flat structure, etc.). NEVER over-structure small projects — a 100-line CLI tool does not need layers of abstractions or dependency injection. ([cc-skills-golang\skills\golang-project-layout\SKILL.md](cc-skills-golang\skills\golang-project-layout\SKILL.md))

- **Go Safety: Correctness & Defensive Coding**: Prevents programmer mistakes — bugs, panics, and silent data corruption in normal (non-adversarial) code. Security handles attackers; safety handles ourselves. ([cc-skills-golang\skills\golang-safety\SKILL.md](cc-skills-golang\skills\golang-safety\SKILL.md))

- **Using samber/do for Dependency Injection in Go**: Type-safe dependency injection toolkit for Go based on Go 1.18+ generics. ([cc-skills-golang\skills\golang-samber-do\SKILL.md](cc-skills-golang\skills\golang-samber-do\SKILL.md))

- **Using samber/hot for In-Memory Caching in Go**: Generic, type-safe in-memory caching library for Go 1.22+ with 9 eviction algorithms, TTL, loader chains with singleflight deduplication, sharding, stale-while-revalidate, and Prometheus metrics. ([cc-skills-golang\skills\golang-samber-hot\SKILL.md](cc-skills-golang\skills\golang-samber-hot\SKILL.md))

- **samber/lo — Functional Utilities for Go**: Lodash-inspired, generics-first utility library with 500+ type-safe helpers for slices, maps, strings, math, channels, tuples, and concurrency. Zero external dependencies. Immutable by default. ([cc-skills-golang\skills\golang-samber-lo\SKILL.md](cc-skills-golang\skills\golang-samber-lo\SKILL.md))

- **samber/mo — Monads and Functional Abstractions for Go**: Go 1.18+ library providing type-safe monadic types with zero dependencies. Inspired by Scala, Rust, and fp-ts. ([cc-skills-golang\skills\golang-samber-mo\SKILL.md](cc-skills-golang\skills\golang-samber-mo\SKILL.md))

- **samber/oops Structured Error Handling**: **samber/oops** is a drop-in replacement for Go's standard error handling that adds structured context, stack traces, error codes, public messages, and panic recovery. Variable data goes in `.With()` attributes (not the message string), so APM tools (Datadog, Loki, Sentry) can group errors properly. ([cc-skills-golang\skills\golang-samber-oops\SKILL.md](cc-skills-golang\skills\golang-samber-oops\SKILL.md))

- **samber/ro — Reactive Streams for Go**: Go implementation of [ReactiveX](https://reactivex.io/). Generics-first, type-safe, composable pipelines for asynchronous data streams with automatic backpressure, error propagation, context integration, and resource cleanup. 150+ operators, 5 subject types, 40+ plugins. ([cc-skills-golang\skills\golang-samber-ro\SKILL.md](cc-skills-golang\skills\golang-samber-ro\SKILL.md))

- **samber/slog-\*\*\*\* — Structured Logging Pipeline for Go**: 20+ composable `slog.Handler` packages for Go 1.21+. Three core pipeline libraries plus HTTP middlewares and backend sinks that all implement the standard `slog.Handler` interface. ([cc-skills-golang\skills\golang-samber-slog\SKILL.md](cc-skills-golang\skills\golang-samber-slog\SKILL.md))

- **Go Security**: Security in Go follows the principle of **defense in depth**: protect at multiple layers, validate all inputs, use secure defaults, and leverage the standard library's security-aware design. Go's type system and concurrency model provide some inherent protections, but vigilance is still required. ([cc-skills-golang\skills\golang-security\SKILL.md](cc-skills-golang\skills\golang-security\SKILL.md))

- **Stay Updated with Go**: A curated guide to keeping your finger on the pulse of the Go ecosystem. ([cc-skills-golang\skills\golang-stay-updated\SKILL.md](cc-skills-golang\skills\golang-stay-updated\SKILL.md))

- **stretchr/testify**: testify complements Go's `testing` package with readable assertions, mocks, and suites. It does not replace `testing` — always use `*testing.T` as the entry point. ([cc-skills-golang\skills\golang-stretchr-testify\SKILL.md](cc-skills-golang\skills\golang-stretchr-testify\SKILL.md))

- **Go Structs & Interfaces**: > "The bigger the interface, the weaker the abstraction." — Go Proverbs ([cc-skills-golang\skills\golang-structs-interfaces\SKILL.md](cc-skills-golang\skills\golang-structs-interfaces\SKILL.md))

- **Go Testing Best Practices**: This skill guides the creation of production-ready tests for Go applications. Follow these principles to write maintainable, fast, and reliable tests. ([cc-skills-golang\skills\golang-testing\SKILL.md](cc-skills-golang\skills\golang-testing\SKILL.md))

- **Go Troubleshooting Guide**: **NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.** Symptom fixes create new bugs and waste time. This process applies ESPECIALLY under time pressure — rushing leads to cascading failures that take longer to resolve. ([cc-skills-golang\skills\golang-troubleshooting\SKILL.md](cc-skills-golang\skills\golang-troubleshooting\SKILL.md))
