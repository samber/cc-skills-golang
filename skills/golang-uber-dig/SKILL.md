---
name: golang-uber-dig
description: "Implements dependency injection in Golang using uber-go/dig — reflection-based container, Provide/Invoke, dig.In/dig.Out parameter and result objects, named values, value groups, optional dependencies, scopes, and Decorate. Apply when using or adopting uber-go/dig, when the codebase imports `go.uber.org/dig`, or when wiring an application graph at startup. For higher-level lifecycle and modules, see `samber/cc-skills-golang@golang-uber-fx` skill."
user-invocable: true
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents, and for projects using Golang.
metadata:
  author: samber
  version: "1.0.0"
  openclaw:
    emoji: "⛏️"
    homepage: https://github.com/samber/cc-skills-golang
    requires:
      bins:
        - go
    install: []
    skill-library-version: "1.19.0"
allowed-tools: Read Edit Write Glob Grep Bash(go:*) Bash(golangci-lint:*) Bash(git:*) Agent WebFetch mcp__context7__resolve-library-id mcp__context7__query-docs
---

**Persona:** You are a Go architect wiring an application graph with dig. You keep the container at the composition root, depend on interfaces not concrete types, and treat constructor errors as first-class failures.

# Using uber-go/dig for Dependency Injection in Go

Reflection-based dependency injection toolkit for Go, designed to power application frameworks (it is the engine behind `uber-go/fx`) and resolve object graphs during startup.

**Official Resources:**

- [pkg.go.dev/go.uber.org/dig](https://pkg.go.dev/go.uber.org/dig)
- [github.com/uber-go/dig](https://github.com/uber-go/dig)

This skill is not exhaustive. Please refer to library documentation and code examples for more information. Context7 can help as a discoverability platform.

```bash
go get go.uber.org/dig
```

> **When to choose dig over fx.** Use raw dig when you only need the wiring graph and do not want fx's lifecycle, signal handling, or app boot semantics. For most production apps, prefer fx (`samber/cc-skills-golang@golang-uber-fx` skill) — it adds lifecycle hooks, modules, and signal-aware Run() on top of the same dig engine.

## Core Concepts

### The Container

```go
import "go.uber.org/dig"

c := dig.New()
```

Options:

- `dig.DeferAcyclicVerification()` — defer graph validation to first `Invoke` (faster startup, slower first invocation)
- `dig.RecoverFromPanics()` — convert constructor panics into `dig.PanicError` instead of crashing the process
- `dig.DryRun(true)` — validate the graph without invoking constructors (useful in tests)

### Provide and Invoke

```go
// Register a constructor — lazy, only runs when its output type is needed
err := c.Provide(func(cfg *Config) (*sql.DB, error) {
    return sql.Open("postgres", cfg.DSN)
})

// Pull a service out of the container by asking for it as a function parameter
err = c.Invoke(func(db *sql.DB) error {
    return db.Ping()
})
```

Constructors are **lazy**. They run the first time their output is requested. Each output type is built **once** and shared (singleton per container).

`Provide` returns an error if the registration is malformed (e.g., duplicate type, no constructor return). `Invoke` returns the constructor's error wrapped with the dependency path that triggered it.

## Constructors

A dig constructor is any function. Inputs are dependencies, outputs are provided types. `error` (last return) signals construction failure.

```go
// Single output
func NewLogger() *zap.Logger { /* ... */ }

// With dependencies and error
func NewServer(log *zap.Logger, db *sql.DB) (*Server, error) { /* ... */ }

// Multiple outputs (returned in one call)
func NewGateways(db *sql.DB) (*UserGateway, *PostGateway, error) { /* ... */ }
```

Follow "accept interfaces, return structs" — the same rule as elsewhere in Go. The container does not care whether you return a concrete type or an interface; design the consumer side.

## Parameter Objects with `dig.In`

When a constructor has many dependencies, embed `dig.In` to group them as struct fields. This keeps signatures readable and lets you tag fields:

```go
type HandlerParams struct {
    dig.In

    Logger *zap.Logger
    DB     *sql.DB
    Cache  *redis.Client `optional:"true"`           // zero value if not provided
    DBRO   *sql.DB       `name:"readonly"`           // named dependency
    Routes []http.Handler `group:"routes"`           // value group
}

func NewHandler(p HandlerParams) *Handler {
    h := &Handler{log: p.Logger, db: p.DB}
    if p.Cache != nil {
        h.cache = p.Cache
    }
    return h
}
```

Tags:

- `name:"..."` — disambiguate multiple instances of the same type
- `optional:"true"` — receive the zero value if no provider exists; lets callers add behavior gradually without forcing every consumer to register a provider
- `group:"..."` — collect all values registered to a named group as a slice

## Result Objects with `dig.Out`

Embed `dig.Out` to return several values from one constructor, and to attach `name`/`group` tags to results:

```go
type ConnResult struct {
    dig.Out

    ReadWrite *sql.DB `name:"primary"`
    ReadOnly  *sql.DB `name:"readonly"`
}

func NewConnections(cfg *Config) (ConnResult, error) {
    rw, err := sql.Open("postgres", cfg.PrimaryDSN)
    if err != nil {
        return ConnResult{}, err
    }
    ro, err := sql.Open("postgres", cfg.ReadOnlyDSN)
    if err != nil {
        return ConnResult{}, err
    }
    return ConnResult{ReadWrite: rw, ReadOnly: ro}, nil
}
```

## Named Values

Two providers of the same type collide. Disambiguate with `dig.Name`:

```go
c.Provide(NewPrimaryDB,  dig.Name("primary"))
c.Provide(NewReadOnlyDB, dig.Name("readonly"))

// Consume by name via dig.In
type Params struct {
    dig.In
    Primary  *sql.DB `name:"primary"`
    ReadOnly *sql.DB `name:"readonly"`
}
```

## Value Groups

Many providers, one consumer slice — typical for HTTP handlers, health checks, or migrations:

```go
type RouteResult struct {
    dig.Out
    Handler http.Handler `group:"routes"`
}

func NewUserHandler(db *sql.DB) RouteResult {
    return RouteResult{Handler: &userHandler{db: db}}
}

func NewPostHandler(db *sql.DB) RouteResult {
    return RouteResult{Handler: &postHandler{db: db}}
}

type ServerParams struct {
    dig.In
    Routes []http.Handler `group:"routes"`
}
```

**Flatten** — when a single constructor produces multiple group entries, append `,flatten` so the slice is unwrapped instead of nested:

```go
type RoutesResult struct {
    dig.Out
    Handlers []http.Handler `group:"routes,flatten"`
}
```

Group order is **not guaranteed**. Do not rely on it.

## Provide as Interface (`dig.As`)

Register a concrete constructor and expose it under one or more interfaces without a separate adapter:

```go
c.Provide(NewPostgresDB, dig.As(new(Database), new(io.Closer)))

// Consumers can now ask for Database or io.Closer; the *PostgresDB is hidden.
```

Useful when the concrete type has methods you do not want to leak to consumers.

## Optional Dependencies

`optional:"true"` lets a consumer compile and run when a provider is missing. Use it sparingly — optional dependencies hide configuration mistakes. They make sense for genuinely optional features (a tracing exporter, an in-memory cache) but not for core services like a database.

## Decorate

`Decorate` modifies a value already provided in the container — the decorator receives the original instance and returns a replacement. Common uses: enriching a logger with context, wrapping a metrics scope with tags, swapping a real client for a recording one in a child scope.

```go
c.Decorate(func(log *zap.Logger) *zap.Logger {
    return log.Named("worker")
})
```

Decorators apply to the scope they were registered in and to that scope's descendants. Use them at module boundaries, not in main(), so changes stay local.

## Scopes

A `Scope` is a child container that inherits providers from its parent and can add or override its own. Scopes let request-, tenant-, or module-level dependencies coexist with shared singletons:

```go
root := dig.New()
root.Provide(NewLogger)
root.Provide(NewDatabase)

requestScope := root.Scope("request")
requestScope.Provide(NewRequestContext)        // only visible inside requestScope
requestScope.Decorate(func(l *zap.Logger) *zap.Logger {
    return l.With(zap.String("scope", "request"))
})
```

By default, providers registered to a scope are private to that scope and its children. Use `dig.Export(true)` if a scope-registered provider must be visible from the root.

## Error Handling

dig wraps the constructor error with the dependency path so you can see *which* graph edge failed:

```go
if err := c.Invoke(run); err != nil {
    // err describes the chain: "could not build *http.Server: ..."
}
```

Useful helpers:

- `errors.As(err, &dig.Error{})` — true if the error originated inside dig
- `dig.RootCause(err)` — unwrap to the original constructor error returned by user code
- `dig.IsCycleDetected(err)` — true if the graph contains a cycle (typically reported at first `Invoke` unless `DeferAcyclicVerification` is set)
- `errors.As(err, &dig.PanicError{})` — when `RecoverFromPanics` is enabled, a panicking constructor surfaces as this typed error

## Visualization

dig can emit the dependency graph in DOT format — useful when wiring becomes too tangled to reason about by reading code:

```go
f, _ := os.Create("graph.dot")
_ = dig.Visualize(c, f)
// then: dot -Tpng graph.dot -o graph.png
```

`dig.VisualizeError(err)` highlights the failed edges when an `Invoke` returns an error — invaluable for debugging "missing type" failures in deep graphs.

## Full Application Example

```go
func main() {
    c := dig.New()

    must(c.Provide(NewConfig))
    must(c.Provide(NewLogger))
    must(c.Provide(NewDatabase))
    must(c.Provide(NewUserHandler))
    must(c.Provide(NewServer))

    err := c.Invoke(func(srv *http.Server) error {
        return srv.ListenAndServe()
    })
    if err != nil {
        log.Fatal(err)
    }
}

func must(err error) {
    if err != nil {
        panic(err)
    }
}
```

dig has **no built-in lifecycle**. If you need OnStart/OnStop hooks, signal handling, and graceful shutdown, use fx — see `samber/cc-skills-golang@golang-uber-fx` skill.

## Best Practices

1. Keep the container at the composition root — never pass `*dig.Container` as a parameter; treat it like a plumbing detail of `main()`. Service-locator patterns defeat the testability gains of DI.
2. Depend on interfaces, not concrete types — lets you swap implementations in tests without touching production code, and lets you use `dig.As` to expose narrow interfaces from wide structs.
3. Prefer parameter objects (`dig.In` structs) once a constructor has 4+ dependencies — call sites stay readable and adding a new dependency is a one-line change instead of a signature break.
4. Use `optional:"true"` only for features that are genuinely optional — for core services it hides misconfiguration until much later in the call path.
5. Group registration by module (one file per module that calls `c.Provide` for its types) — review and refactoring become a per-module concern, and you can extract a module into a fx.Module later without rewriting wiring.
6. Validate the graph eagerly in tests — call `c.Invoke(func(...your composition root deps...) {})` at startup to surface missing providers at boot time, not at first request.
7. Return errors from constructors instead of panicking — dig wraps them with the dependency path, which makes the failure point obvious.

## Common Mistakes

| Mistake                                        | Fix                                                                                                                                |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Passing the container into services            | The container belongs to `main()`. Inject the typed dependencies a service needs; otherwise tests need to build a real container.  |
| Registering interfaces directly                | Provide concrete types and use `dig.As` (or have the constructor return the interface). Avoid splitting the interface into a separate provider that wraps the concrete one. |
| Two providers for the same type without `Name` | dig errors at `Provide` time. Either name them, or merge into a single provider that returns a result struct.                      |
| Ignoring `Provide` errors                      | Wrap each `Provide` with a `must`-style helper, or accumulate and report at startup. A silent registration error becomes a missing-type error far later. |
| Using groups when ordering matters             | Groups are unordered. If order matters (middleware chain, migration sequence), provide an explicit ordered slice with one constructor. |
| Constructors with side effects on import       | Keep `init()` empty — start work only inside the constructor, after the graph is built.                                            |

## Testing

dig containers are cheap — build a fresh one per test, override the providers you care about with `Decorate`, and call `Invoke` to drive the system under test. For full patterns (per-test wiring, shared helpers, graph validation in CI, asserting wire-time errors, recovering from constructor panics), see [testing recipes](./references/testing.md).

## Further Reading

- [recipes.md](./references/recipes.md) — end-to-end examples: HTTP server with route group, two databases, request scopes, decorators, dry-run validation, graph visualization
- [testing.md](./references/testing.md) — testing patterns and graph validation

## Quick Reference

### Container

| Function/Method                  | Purpose                                                  |
| -------------------------------- | -------------------------------------------------------- |
| `dig.New(opts...)`               | Create a root container                                  |
| `c.Provide(ctor, opts...)`       | Register a constructor                                   |
| `c.Invoke(fn, opts...)`          | Run a function with injected dependencies                |
| `c.Decorate(fn, opts...)`        | Modify a previously-provided value within a scope        |
| `c.Scope(name, opts...)`         | Create a child scope (private providers by default)      |
| `c.String()`                     | Pretty-print the dependency graph for debugging          |

### Provide / Invoke options

| Option                            | Purpose                                                  |
| --------------------------------- | -------------------------------------------------------- |
| `dig.Name("...")`                 | Disambiguate same-typed providers                        |
| `dig.Group("...")`                | Add the result to a value group                          |
| `dig.As(new(I))`                  | Provide the concrete value as one or more interfaces     |
| `dig.Export(true)`                | Make a scope-level provider visible from the root        |
| `dig.FillProvideInfo(&info)`      | Capture metadata for tooling                             |

### Container options

| Option                              | Purpose                                                  |
| ----------------------------------- | -------------------------------------------------------- |
| `dig.DeferAcyclicVerification()`    | Defer cycle check to first `Invoke`                      |
| `dig.RecoverFromPanics()`           | Convert constructor panics into `dig.PanicError`         |
| `dig.DryRun(true)`                  | Validate without invoking constructors                   |

### Errors

| Helper                              | Purpose                                                  |
| ----------------------------------- | -------------------------------------------------------- |
| `dig.RootCause(err)`                | Unwrap to the user-returned error                        |
| `dig.IsCycleDetected(err)`          | True if the graph has a cycle                            |
| `errors.As(err, &dig.PanicError{})` | Detect a recovered panic                                 |
| `dig.Visualize(c, w, opts...)`      | Write the graph in DOT format                            |

## Cross-References

- → See `samber/cc-skills-golang@golang-uber-fx` skill for application lifecycle, modules, and signal-aware Run() built on top of dig
- → See `samber/cc-skills-golang@golang-dependency-injection` skill for DI concepts, comparison, and when to adopt a DI library
- → See `samber/cc-skills-golang@golang-samber-do` skill for a generics-based alternative without reflection
- → See `samber/cc-skills-golang@golang-google-wire` skill for compile-time DI (no runtime container)
- → See `samber/cc-skills-golang@golang-structs-interfaces` skill for interface design patterns
- → See `samber/cc-skills-golang@golang-testing` skill for general testing patterns

If you encounter a bug or unexpected behavior in uber-go/dig, open an issue at https://github.com/uber-go/dig/issues.
