# pprof Reference

## Enable pprof HTTP Server

Pprof endpoints MUST be protected with basic auth — NEVER expose them publicly. They leak sensitive runtime information (goroutine stacks, memory contents) and can be abused to DoS your service (CPU profiling is expensive). Pprof SHOULD be toggled via a `PPROF_ENABLED` environment variable.

### Quick Setup (Development)

```go
import _ "net/http/pprof"

func main() {
    go func() {
        log.Println(http.ListenAndServe("localhost:6060", nil))
    }()
    // ... rest of app
}
```

### Secure Setup (Production)

For production, protect endpoints with basic auth:

```go
import "net/http/pprof"

func setupPprof(mux *http.ServeMux) {
    if os.Getenv("PPROF_ENABLED") != "true" {
        return
    }

    // Protect pprof endpoints with basic auth — never expose unauthenticated
    auth := basicAuth(
        os.Getenv("PPROF_USERNAME"),
        os.Getenv("PPROF_PASSWORD"),
    )

    mux.Handle("/debug/pprof/", auth(http.HandlerFunc(pprof.Index)))
    mux.Handle("/debug/pprof/cmdline", auth(http.HandlerFunc(pprof.Cmdline)))
    mux.Handle("/debug/pprof/profile", auth(http.HandlerFunc(pprof.Profile)))
    mux.Handle("/debug/pprof/symbol", auth(http.HandlerFunc(pprof.Symbol)))
    mux.Handle("/debug/pprof/trace", auth(http.HandlerFunc(pprof.Trace)))

    slog.Info("pprof endpoints enabled (basic auth required)")
}

// basicAuth wraps an http.Handler with HTTP Basic Authentication.
func basicAuth(username, password string) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            u, p, ok := r.BasicAuth()
            if !ok || u != username || subtle.ConstantTimeCompare([]byte(p), []byte(password)) != 1 {
                w.Header().Set("WWW-Authenticate", `Basic realm="pprof"`)
                http.Error(w, "unauthorized", http.StatusUnauthorized)
                return
            }
            next.ServeHTTP(w, r)
        })
    }
}
```

## Profile Types

| Profile | Command | What It Shows |
| --- | --- | --- |
| **CPU** | `go tool pprof profile` | Where CPU time is spent |
| **Heap** | `go tool pprof heap` | Memory allocations, live objects |
| **Goroutine** | `go tool pprof goroutine` | Stack traces of all goroutines |
| **Block** | `go tool pprof block` | Blocking operations (needs SetBlockProfileRate) |
| **Mutex** | `go tool pprof mutex` | Lock contention (needs SetMutexProfileFraction) |
| **Alloc** | `go tool pprof -alloc_space heap` | Cumulative allocations (not current heap) |

## Capturing Profiles

```bash
# CPU profiles SHOULD capture at least 30 seconds for meaningful data (30s default).
# Ensure your HTTP server's request timeout exceeds the capture duration.
curl http://localhost:6060/debug/pprof/profile?seconds=30 > cpu.prof

# Heap snapshot
curl http://localhost:6060/debug/pprof/heap > heap.prof

# Goroutine dump (human-readable)
curl http://localhost:6060/debug/pprof/goroutine?debug=2 > goroutines.txt

# Goroutine profile (for pprof analysis)
curl http://localhost:6060/debug/pprof/goroutine > goroutine.prof

# Mutex contention
curl http://localhost:6060/debug/pprof/mutex > mutex.prof

# Block profile
curl http://localhost:6060/debug/pprof/block > block.prof
```

## Analyzing and Interpreting Profiles

→ See `samber/cc-skills-golang@golang-benchmark` skill (pprof.md) for interpreting profiles: `top`, `list`, `peek`, common profile patterns (flat vs cum, GC churn, memory leaks), and compiler diagnostics. See also compiler-analysis.md for escape analysis and inlining decisions.

**Quick start:**

```bash
go tool pprof cpu.prof          # interactive analysis
go tool pprof -http=:8080 cpu.prof  # graphical flamegraph
go tool pprof -base heap1.prof heap2.prof  # compare heap snapshots
```

## Remote Profiling (Production)

For production servers, replace `localhost:6060` with your server address and use basic auth credentials.

**Safety:** pprof has minimal overhead. CPU profile defaults to 30s capture. Heap profile is a snapshot.

---

→ See `samber/cc-skills-golang@golang-observability` skill for continuous profiling with Pyroscope. → See `samber/cc-skills-golang@golang-benchmark` skill for investigation session setup and Prometheus-based performance tracking.
