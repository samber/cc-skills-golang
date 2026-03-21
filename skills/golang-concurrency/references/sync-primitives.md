# Sync Primitives Deep Dive

## sync.Mutex

Protects shared state with exclusive access. MUST hold the lock for the shortest time possible — NEVER hold a mutex across I/O, network calls, or channel operations.

```go
type SafeCache struct {
    mu    sync.Mutex
    items map[string]string
}

func (c *SafeCache) Get(key string) (string, bool) {
    c.mu.Lock()
    defer c.mu.Unlock()
    v, ok := c.items[key]
    return v, ok
}

func (c *SafeCache) Set(key, value string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.items[key] = value
}
```

### Embedding Convention

Embed the mutex as an unexported field, placed directly above the fields it protects:

```go
type Registry struct {
    mu      sync.Mutex // protects entries
    entries map[string]Entry
}
```

## sync.RWMutex

SHOULD be used when reads greatly outnumber writes. Multiple goroutines can hold `RLock` simultaneously; `Lock` is exclusive.

```go
type Config struct {
    mu     sync.RWMutex
    values map[string]string
}

func (c *Config) Get(key string) string {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.values[key]
}

func (c *Config) Set(key, value string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.values[key] = value
}
```

**Pitfall**: Do not upgrade RLock to Lock — this deadlocks. Release RLock first, then acquire Lock.

## sync/atomic

Lock-free operations for simple values. SHOULD be preferred over Mutex for simple counter operations. Faster than mutex for low-contention counters and flags.

```go
// ✓ Good — atomic for a simple counter
var requestCount atomic.Int64

func handleRequest() {
    requestCount.Add(1)
}

func getCount() int64 {
    return requestCount.Load()
}
```

```go
// ✓ Good — atomic.Bool for a shutdown flag
var shuttingDown atomic.Bool

func shutdown() {
    shuttingDown.Store(true)
}

func isRunning() bool {
    return !shuttingDown.Load()
}
```

Go 1.19+ provides typed atomics (`atomic.Int64`, `atomic.Bool`, `atomic.Pointer[T]`) — prefer these over raw `atomic.AddInt64`/`atomic.LoadInt64`.

## sync.Map

SHOULD only be used for write-once/read-many patterns. Optimized for two common patterns: (1) keys are written once and read many times, (2) multiple goroutines read/write disjoint key sets. For other patterns, a plain `map` + `sync.RWMutex` is faster.

```go
var cache sync.Map

func Get(key string) (any, bool) {
    return cache.Load(key)
}

func Set(key string, value any) {
    cache.Store(key, value)
}

func GetOrSet(key string, compute func() any) any {
    if v, ok := cache.Load(key); ok {
        return v
    }
    v, _ := cache.LoadOrStore(key, compute())
    return v
}
```

**When NOT to use `sync.Map`**: when you need to iterate, get the length, or when writes are frequent and keys overlap heavily. Use `sync.RWMutex` + `map` instead.

## sync.Pool

Reuse temporary objects to reduce GC pressure. MUST NOT store pointers to stack-allocated objects. Objects in the pool may be reclaimed at any GC cycle — do not store persistent state.

```go
var bufPool = sync.Pool{
    New: func() any {
        return new(bytes.Buffer)
    },
}

func process(data []byte) string {
    buf := bufPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufPool.Put(buf)
    }()

    buf.Write(data)
    // ... transform ...
    return buf.String()
}
```

**Rules**:

- Always `Reset()` before `Put()` — returning dirty objects causes bugs
- Do not assume an object from `Get()` is zeroed — the `New` func only runs if the pool is empty
- Best for short-lived, frequently allocated objects (buffers, encoders, temporary structs)

## sync.Once

MUST be used for one-time initialization. Execute exactly once, regardless of how many goroutines call it concurrently. Thread-safe by design.

```go
type DBClient struct {
    initOnce  sync.Once
    closeOnce sync.Once
    conn      *sql.DB
}

func (c *DBClient) getConn() *sql.DB {
    c.initOnce.Do(func() {
        var err error
        c.conn, err = sql.Open("postgres", dsn)
        if err != nil {
            panic(fmt.Sprintf("db init: %v", err))
        }
    })
    return c.conn
}

func (c *DBClient) Close() error {
    var err error
    c.closeOnce.Do(func() {
        err = c.conn.Close()
    })
    return err
}
```

Go 1.21+ also provides `sync.OnceFunc`, `sync.OnceValue`, and `sync.OnceValues` for simpler use cases:

```go
var loadConfig = sync.OnceValue(func() *Config {
    cfg, err := parseConfig("config.yaml")
    if err != nil {
        panic(err)
    }
    return cfg
})

// Usage: cfg := loadConfig()
```

## sync.WaitGroup

Coordinate goroutine completion. Call `Add` before launching the goroutine, `Done` inside the goroutine, `Wait` in the caller.

```go
func processAll(ctx context.Context, items []Item) {
    var wg sync.WaitGroup
    for _, item := range items {
        wg.Add(1) // Add BEFORE go
        go func(item Item) {
            defer wg.Done()
            process(ctx, item)
        }(item)
    }
    wg.Wait() // blocks until all goroutines finish
}
```

```go
// ✗ Bad — Add inside the goroutine (race: Wait may return before Add runs)
go func() {
    wg.Add(1)
    defer wg.Done()
    process(item)
}()
```

### Go 1.24+: wg.Go()

Go 1.24 introduced `wg.Go()` which eliminates the manual `Add`/`Done` bookkeeping:

```go
func processAll(ctx context.Context, items []Item) error {
    var wg sync.WaitGroup
    var mu sync.Mutex
    var lastErr error

    for _, item := range items {
        item := item // optional starting Go 1.22+ (per-iteration scoping)
        wg.Go(func() {
            if err := process(ctx, item); err != nil {
                mu.Lock()
                lastErr = err
                mu.Unlock()
            }
        })
    }

    wg.Wait()
    return lastErr
}
```

**Benefits of `wg.Go()`**:

- No risk of forgetting `Add` or `Done`
- Cleaner, less error-prone API
- Semantically clearer: "do this concurrently"
- Automatically handles Add/Done internally

**When to use**: Go 1.24+ projects where all concurrent work needs to complete and you want simpler code.

## golang.org/x/sync/singleflight

Deduplicates concurrent calls for the same key. When multiple goroutines request the same resource simultaneously, only one executes; the rest wait and share the result.

```go
var group singleflight.Group

func GetUser(ctx context.Context, id string) (*User, error) {
    v, err, _ := group.Do(id, func() (any, error) {
        // Only one goroutine executes this for a given id
        return db.QueryUser(ctx, id)
    })
    if err != nil {
        return nil, err
    }
    return v.(*User), nil
}
```

**Use cases**: cache stampede prevention, deduplicating expensive lookups (DB, API), rate-limited external service calls.

## golang.org/x/sync/errgroup

Goroutine group with error propagation. Returns the first error from any goroutine. With `WithContext`, cancels remaining goroutines on first error.

```go
func fetchAll(ctx context.Context, urls []string) ([]Response, error) {
    g, ctx := errgroup.WithContext(ctx) // cancel siblings on first error
    results := make([]Response, len(urls))

    for i, url := range urls {
        g.Go(func() error {
            resp, err := fetch(ctx, url)
            if err != nil {
                return fmt.Errorf("fetching %s: %w", url, err)
            }
            results[i] = resp // safe: each goroutine writes to its own index
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return nil, err
    }
    return results, nil
}
```

### Bounded Concurrency with SetLimit

SHOULD use `SetLimit` to bound concurrency and avoid unbounded goroutine spawning.

```go
g, ctx := errgroup.WithContext(ctx)
g.SetLimit(10) // at most 10 goroutines run concurrently

for _, task := range tasks {
    g.Go(func() error {
        return process(ctx, task)
    })
}
return g.Wait()
```

This replaces hand-rolled worker pools for most use cases.

→ See `samber/cc-skills-golang@golang-concurrency` skill for high-level patterns and decision trees.
