---
name: golang-uber-fx
description: "Golang application framework using uber-go/fx — fx.New, fx.Provide, fx.Invoke, fx.Module, fx.Lifecycle hooks, fx.Annotate (name/group/As), fx.Decorate, fx.Supply, fx.Replace, fx.WithLogger, and signal-aware Run(). Apply when using or adopting uber-go/fx, when the codebase imports `go.uber.org/fx`, or when wiring services with fx.New. For raw DI without lifecycle, see `samber/cc-skills-golang@golang-uber-dig` skill."
user-invocable: true
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents, and for projects using Golang.
metadata:
  author: samber
  version: "1.0.0"
  openclaw:
    emoji: "🏭"
    homepage: https://github.com/samber/cc-skills-golang
    requires:
      bins:
        - go
    install: []
    skill-library-version: "1.24.0"
allowed-tools: Read Edit Write Glob Grep Bash(go:*) Bash(golangci-lint:*) Bash(git:*) Agent WebFetch mcp__context7__resolve-library-id mcp__context7__query-docs
---

**Persona:** You are a Go architect building a long-running service with fx. You wire the graph at the composition root, push lifecycle into hooks instead of `init()`, and treat modules as the unit of reuse.

# Using uber-go/fx for Application Wiring in Go

Application framework that combines a reflection-based DI container (built on `uber-go/dig`) with a lifecycle, module system, signal-aware run loop, and structured event logging. Designed for long-running services where boot order, graceful shutdown, and modular composition matter.

**Official Resources:**

- [pkg.go.dev/go.uber.org/fx](https://pkg.go.dev/go.uber.org/fx)
- [uber-go.github.io/fx](https://uber-go.github.io/fx/)
- [github.com/uber-go/fx](https://github.com/uber-go/fx)

This skill is not exhaustive. Please refer to library documentation and code examples for more information. Context7 can help as a discoverability platform.

```bash
go get go.uber.org/fx
```

> **fx vs. dig.** fx wraps dig and adds: lifecycle hooks (`fx.Lifecycle`), modules (`fx.Module`), `Run()` with signal handling, structured event logs (`fxevent`), and ergonomic helpers (`fx.Supply`, `fx.Replace`, `fx.Decorate`, `fx.Annotate`). Use raw dig (`samber/cc-skills-golang@golang-uber-dig` skill) only when you do not need lifecycle or app boot — most production services should use fx.

## Core Concepts

### The Application

```go
import "go.uber.org/fx"

app := fx.New(
    fx.Provide(NewLogger, NewDatabase, NewServer),
    fx.Invoke(RegisterRoutes),
)
app.Run() // blocks until SIGINT/SIGTERM, then runs OnStop hooks
```

`fx.New` builds the graph and validates types. `app.Run()` calls `Start` (firing OnStart hooks in dependency order), waits for a signal, then calls `Stop` (firing OnStop hooks in reverse order).

### Boot stages

1. **Wire** — `fx.New` validates the graph; constructors do not run yet
2. **Start** — `app.Start(ctx)` runs each `fx.Invoke`, instantiating constructors lazily as their outputs are needed; OnStart hooks fire in topological order
3. **Run** — main goroutine blocks on `app.Done()` (or `app.Wait()` for the exit code)
4. **Stop** — `app.Stop(ctx)` fires OnStop hooks in reverse order with the supplied context

The default start/stop timeout is **15 seconds** — override with `fx.StartTimeout` / `fx.StopTimeout` when bootstrapping does real work.

## Provide and Invoke

```go
fx.New(
    // Constructors. Lazy — only run if their output is needed.
    fx.Provide(
        NewLogger,
        NewDatabase,
        NewServer,
    ),
    // Functions that drive the app. Always run during Start.
    fx.Invoke(
        RegisterRoutes,
        StartMetricsExporter,
    ),
)
```

`fx.Provide` registers constructors; their return types become available to other constructors and to `fx.Invoke`. `fx.Invoke` is the trigger — without an Invoke (directly or indirectly) referencing a type, its constructor never runs.

## Lifecycle Hooks

Inject `fx.Lifecycle` and append hooks. Constructors should return quickly; long-running work belongs in `OnStart`.

```go
func NewHTTPServer(lc fx.Lifecycle, log *zap.Logger, cfg *Config) *http.Server {
    srv := &http.Server{Addr: cfg.Addr}

    lc.Append(fx.Hook{
        OnStart: func(ctx context.Context) error {
            ln, err := net.Listen("tcp", srv.Addr)
            if err != nil {
                return fmt.Errorf("listen: %w", err)
            }
            go func() {
                if err := srv.Serve(ln); err != nil && err != http.ErrServerClosed {
                    log.Error("server", zap.Error(err))
                }
            }()
            return nil
        },
        OnStop: func(ctx context.Context) error {
            return srv.Shutdown(ctx)
        },
    })

    return srv
}
```

**Hook context.** Both OnStart and OnStop receive a context bounded by `StartTimeout` / `StopTimeout`. Respect cancellation — a hook that ignores `ctx.Done()` will be killed (its goroutine continues, but the app considers it failed).

**Run blocking work in a goroutine.** OnStart must return; do not call `srv.Serve` synchronously. Otherwise startup hangs and dependent hooks never fire.

**Simplified hooks** — `fx.StartHook`, `fx.StopHook`, `fx.StartStopHook` adapt simpler signatures (no context, no error, or both) when you do not need them:

```go
lc.Append(fx.StartHook(srv.Start))                 // func() error
lc.Append(fx.StartStopHook(srv.Start, srv.Stop))   // matched pair
```

## Parameter and Result Objects

fx uses dig's `dig.In` and `dig.Out` semantics, re-exported as `fx.In` and `fx.Out`. Use them once a constructor has 4+ dependencies, or when you need `name`/`group`/`optional` tags.

```go
type ServerParams struct {
    fx.In

    Logger *zap.Logger
    DB     *sql.DB
    Cache  *redis.Client     `optional:"true"`
    Routes []http.Handler    `group:"routes"`
}

func NewServer(p ServerParams) *Server { /* ... */ }
```

```go
type DBResult struct {
    fx.Out

    Primary  *sql.DB `name:"primary"`
    ReadOnly *sql.DB `name:"readonly"`
}

func NewConnections(cfg *Config) (DBResult, error) { /* ... */ }
```

## fx.Annotate

`fx.Annotate` wraps a constructor to add tags or interface bindings without rewriting it as a `fx.Out` struct. Prefer it for ergonomic name/group/As bindings — it is the modern replacement for ad-hoc adapter functions.

```go
fx.Provide(
    // Result name: registers the *sql.DB as `name:"primary"`
    fx.Annotate(NewPrimaryDB, fx.ResultTags(`name:"primary"`)),

    // Param tags: consume the named *sql.DB
    fx.Annotate(NewUserRepo, fx.ParamTags(`name:"primary"`)),

    // Provide as interface — Database (the consumer) sees only the interface
    fx.Annotate(NewPostgresDB, fx.As(new(Database))),

    // Group + interface together
    fx.Annotate(NewUserHandler,
        fx.As(new(http.Handler)),
        fx.ResultTags(`group:"routes"`),
    ),
)
```

## Value Groups

Many constructors, one consumer slice — typical for HTTP routes, health checks, metrics collectors:

```go
type RouteResult struct {
    fx.Out
    Handler http.Handler `group:"routes"`
}

func NewUserHandler(db *sql.DB) RouteResult { /* ... */ }
func NewPostHandler(db *sql.DB) RouteResult { /* ... */ }

type ServerParams struct {
    fx.In
    Routes []http.Handler `group:"routes"`
}
```

**Flatten** — when a constructor produces several entries, append `,flatten`:

```go
type RoutesResult struct {
    fx.Out
    Handlers []http.Handler `group:"routes,flatten"`
}
```

Group order is **not guaranteed**. If you need a fixed sequence (middleware chain, migration order), provide an explicit ordered slice with one constructor.

## fx.Module

`fx.Module` groups providers, invokes, and decorators under a name. Modules **scope decorators** to themselves and their children — a logger renamed in `fx.Module("db", ...)` only appears renamed for code inside that module.

```go
var DatabaseModule = fx.Module("database",
    fx.Provide(
        NewConnection,
        NewUserRepository,
        NewPostRepository,
    ),
    fx.Decorate(func(log *zap.Logger) *zap.Logger {
        return log.Named("db")
    }),
)

var HTTPModule = fx.Module("http",
    fx.Provide(NewServer, NewRouter),
    fx.Invoke(RegisterRoutes),
)

func main() {
    fx.New(
        fx.Provide(NewConfig, NewLogger),
        DatabaseModule,
        HTTPModule,
    ).Run()
}
```

Modules are the unit of reuse in fx. Treat each module as a small library that can be lifted into another app — its public surface is the types it Provides.

## fx.Supply, fx.Replace, fx.Decorate

| Option                | Purpose                                                                                       |
| --------------------- | --------------------------------------------------------------------------------------------- |
| `fx.Supply(values...)`| Provide pre-built values directly. Equivalent to `fx.Provide(func() T { return v })` for each value. Use for config, secrets, command-line flags. |
| `fx.Replace(values...)`| Replace an already-provided type. Most useful in tests: swap a real client for a fake.       |
| `fx.Decorate(fn)`     | Wrap or modify an existing value. Scoped to the surrounding module. Useful for adding tags, names, or middleware to a logger or metrics scope. |

```go
// Supply
fx.Supply(cfg, secret)

// Replace (typically inside fxtest.New)
fx.Replace(
    fx.Annotate(&fakeDB{}, fx.As(new(Database))),
)

// Decorate, module-scoped
fx.Module("worker",
    fx.Decorate(func(s metrics.Scope) metrics.Scope {
        return s.Tagged(map[string]string{"component": "worker"})
    }),
)
```

## Optional Dependencies

`optional:"true"` lets a consumer compile and run when no provider exists. Use it for genuinely optional features (a tracer, a cache) — not for core services like a database.

```go
type Params struct {
    fx.In

    Logger *zap.Logger
    Tracer trace.Tracer `optional:"true"`
}
```

## Logging fx Events

fx emits structured events (provide, invoke, hook execution, errors) through `fxevent.Logger`. By default it writes to stderr — replace with a Zap logger or silence it in tests:

```go
fx.New(
    fx.Provide(NewZapLogger),
    fx.WithLogger(func(log *zap.Logger) fxevent.Logger {
        return &fxevent.ZapLogger{Logger: log}
    }),
    // Or silence: fx.NopLogger
)
```

## Manual Lifecycle Control

`app.Run()` is convenient but inflexible. For tests, custom signal handling, or embedding fx in a larger program, call `app.Start(ctx)` / `app.Stop(ctx)` directly and wait on `app.Done()` between them. See [recipes.md](./references/recipes.md) for a CLI-embedding example.

`fx.StartTimeout` and `fx.StopTimeout` set defaults; pass an explicit context to override per-call.

## Testing with fxtest

`go.uber.org/fx/fxtest` integrates fx with `*testing.T` — failures call `t.Fatal` and `RequireStop` registers as `t.Cleanup`. Use `fx.Populate(&target)` to extract values from the graph and `fx.Replace` to swap real dependencies for fakes. Full patterns (graph validation in CI, asserting wire-time errors, isolated lifecycle tests) live in [testing.md](./references/testing.md).

```go
var svc *UserService
app := fxtest.New(t,
    fx.Provide(func() Database { return &fakeDB{} }, NewUserService),
    fx.Populate(&svc),
)
defer app.RequireStop()
app.RequireStart()
```

## Further Reading

- [recipes.md](./references/recipes.md) — full HTTP service with database/metrics, background workers with graceful drain, multiple impls of the same interface, manual lifecycle for CLI embedding, custom event loggers
- [testing.md](./references/testing.md) — fxtest patterns, `fx.Replace`, `fx.Populate`, isolated lifecycle tests, CI graph validation

## Best Practices

1. Keep `main()` thin — providers, modules, and a single `Run()`. Push real work into modules so each can be tested in isolation.
2. Use lifecycle hooks instead of `init()` or goroutines launched from constructors — Start/Stop ordering depends on graph topology, but goroutines from `init()` do not, which leads to races and leaks.
3. Always make OnStart return promptly — long work goes in a goroutine inside the hook. A blocking OnStart hangs the rest of the boot.
4. Respect `ctx.Done()` in hooks — a hook that ignores cancellation is reported as a timeout failure but its goroutine continues, leaking resources.
5. Group by module, not by layer — a module owns the providers, lifecycle, and decorators for one concern (HTTP, DB, metrics). Layered modules (one per architectural layer) tend to leak across files.
6. Use `fx.Annotate` for tags rather than wrapping a constructor in an `fx.Out` struct — keeps the constructor free of fx-specific types and reusable outside fx.
7. Replace `fx.Provide` with `fx.Supply` for pre-built values (config loaded by main, command-line flags). It is shorter and signals intent.
8. In tests, prefer `fxtest.New` + `fx.Populate` over `fx.Invoke` — the test fails cleanly with proper teardown.
9. Validate the graph in CI by booting the app under `fx.New(...).Err()` (or `fxtest.New`) — catches missing providers and cycles before deploy.
10. Pin a single zap (or slog) logger via `fx.WithLogger` — fx's default logger is fine for development but is too noisy and unstructured for production.

## Common Mistakes

| Mistake                                              | Fix                                                                                                                    |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Long-running work directly in OnStart               | Spawn a goroutine inside OnStart; the hook itself must return quickly so dependent hooks can run.                       |
| `fx.Provide` something that should be `fx.Supply`   | Pre-built values (config, secrets) belong in `fx.Supply` — clearer and avoids a no-op constructor.                      |
| Module decorator leaking to siblings                 | Decorate inside `fx.Module(...)` — decorators only flow to descendants, not siblings. A top-level `fx.Decorate` is global. |
| Group order assumed                                  | Groups are unordered. If order matters, provide an ordered slice with one constructor.                                  |
| Constructors with side effects                       | Side effects belong in OnStart — constructors should be cheap and pure-ish, since they may run concurrently and lazily. |
| Forgotten `fx.Invoke`                                | Without an Invoke (or a downstream consumer), constructors never run. Add at least one Invoke per app.                  |
| Passing `fx.Lifecycle` outside its constructor       | The Lifecycle is meant for the constructor that owns the resource. Don't store it in a struct and append later.         |
| Using `fx.Replace` outside tests                     | In production code, prefer `fx.Decorate` (transforms) or restructure providers. `Replace` is for fxtest.                |

## Quick Reference

### Application

| Function                     | Purpose                                                  |
| ---------------------------- | -------------------------------------------------------- |
| `fx.New(opts...)`            | Build the application graph                              |
| `app.Run()`                  | Start, wait for signal, Stop — single call               |
| `app.Start(ctx)`             | Run OnStart hooks in dependency order                    |
| `app.Stop(ctx)`              | Run OnStop hooks in reverse order                        |
| `app.Done()`                 | Channel that closes on SIGINT/SIGTERM                    |
| `app.Err()`                  | Wiring error from `fx.New` (validate without starting)   |
| `app.Wait()`                 | Block on shutdown signal and return exit code            |

### Wiring

| Option                       | Purpose                                                  |
| ---------------------------- | -------------------------------------------------------- |
| `fx.Provide(ctors...)`       | Register constructors                                    |
| `fx.Invoke(fns...)`          | Run functions during Start                               |
| `fx.Supply(values...)`       | Provide pre-built values                                 |
| `fx.Replace(values...)`      | Replace previously-provided values (tests)               |
| `fx.Decorate(fn)`            | Wrap an existing value (module-scoped)                   |
| `fx.Module(name, opts...)`   | Group providers/invokes/decorators                       |
| `fx.Options(opts...)`        | Bundle options into a single value                       |
| `fx.Populate(targets...)`    | Extract typed values from the graph (tests)              |

### Annotations

| Function                              | Purpose                                          |
| ------------------------------------- | ------------------------------------------------ |
| `fx.Annotate(fn, opts...)`            | Tag/interface-wrap a constructor                 |
| `fx.ParamTags("...")`                 | Tag parameters of an annotated constructor       |
| `fx.ResultTags("...")`                | Tag results of an annotated constructor          |
| `fx.As(new(I))`                       | Provide as one or more interfaces                |
| `fx.From(types...)`                   | Bind annotated parameters to specific provided types |

### Lifecycle

| Helper                                       | Purpose                                       |
| -------------------------------------------- | --------------------------------------------- |
| `fx.Hook{OnStart, OnStop}`                   | Full hook with context-aware callbacks        |
| `fx.StartHook(fn)`                           | Adapt a simple Start function                 |
| `fx.StopHook(fn)`                            | Adapt a simple Stop function                  |
| `fx.StartStopHook(start, stop)`              | Pair of simple Start/Stop functions           |
| `fx.StartTimeout(d)`, `fx.StopTimeout(d)`    | Override default 15s lifecycle timeouts       |

### Logging

| Option                                        | Purpose                                      |
| --------------------------------------------- | -------------------------------------------- |
| `fx.WithLogger(fn)`                           | Plug in a custom `fxevent.Logger`            |
| `fx.NopLogger`                                | Silence fx event logging                     |
| `fxevent.ZapLogger{Logger: log}`              | Bridge fx events into zap                    |
| `fxevent.SlogLogger{Logger: log}`             | Bridge fx events into log/slog               |

### Testing

| Helper                                       | Purpose                                       |
| -------------------------------------------- | --------------------------------------------- |
| `fxtest.New(t, opts...)`                     | App that fails the test on errors             |
| `app.RequireStart()`, `app.RequireStop()`    | Start/Stop with `t.Fatal` on failure          |
| `fxtest.NewLifecycle(t)`                     | Standalone lifecycle for unit tests           |
| `fx.Populate(targets...)`                    | Pull typed values out of the graph            |

## Cross-References

- → See `samber/cc-skills-golang@golang-uber-dig` skill for the underlying container, `dig.In`/`dig.Out`, and DI without lifecycle
- → See `samber/cc-skills-golang@golang-dependency-injection` skill for DI concepts, comparison, and when to adopt a DI library
- → See `samber/cc-skills-golang@golang-samber-do` skill for a generics-based alternative without reflection
- → See `samber/cc-skills-golang@golang-google-wire` skill for compile-time DI (no runtime container)
- → See `samber/cc-skills-golang@golang-structs-interfaces` skill for interface design patterns
- → See `samber/cc-skills-golang@golang-context` skill for context propagation in OnStart/OnStop hooks
- → See `samber/cc-skills-golang@golang-testing` skill for general testing patterns

If you encounter a bug or unexpected behavior in uber-go/fx, open an issue at https://github.com/uber-go/fx/issues.
