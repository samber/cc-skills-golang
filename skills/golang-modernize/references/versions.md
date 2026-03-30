# Go Version Modernizations

## Go 1.21 Modernizations (August 2023)

Changelog: <https://go.dev/doc/go1.21>

### Use built-in `min`, `max`, `clear` _(Go 1.21+)_

Remove custom implementations. `min`/`max` work with any ordered type and accept variadic arguments:

```go
// Before
func minInt(a, b int) int {
    if a < b { return a }
    return b
}
x := minInt(a, b)

// After (Go 1.21+)
x := min(a, b)
smallest := min(a, b, c, d)
```

`clear` zeroes maps and slices:

```go
// Before
for k := range m { delete(m, k) }

// After (Go 1.21+)
clear(m)
```

### Use `log/slog` instead of third-party loggers _(Go 1.21+)_

`log/slog` is the standard structured logging package. New code SHOULD migrate to `slog` over `zap`, `logrus`, or `zerolog`.

```go
// Before: zap
logger, _ := zap.NewProduction()
logger.Info("request handled", zap.String("method", r.Method), zap.Int("status", status))

// Before: logrus
logrus.WithFields(logrus.Fields{"method": r.Method, "status": status}).Info("request handled")

// After (Go 1.21+): slog
slog.Info("request handled", "method", r.Method, "status", status)
// Or with type-safe attributes:
slog.Info("request handled", slog.String("method", r.Method), slog.Int("status", status))
```

**Migration guidance**: For existing projects heavily invested in third-party loggers, migration is optional. For new projects, prefer `slog`. The `samber/slog-*` ecosystem provides handlers for routing slog output to various backends. Go 1.24 added `slog.DiscardHandler` for silent loggers.

### Use `slices` package instead of `sort` and manual loops _(Go 1.21+)_

```go
// Before
sort.Strings(names)
sort.Slice(users, func(i, j int) bool { return users[i].Name < users[j].Name })

// After (Go 1.21+)
slices.Sort(names)
slices.SortFunc(users, func(a, b User) int { return cmp.Compare(a.Name, b.Name) })
```

```go
// Before: manual search
found := false
for _, v := range items { if v == target { found = true; break } }

// After (Go 1.21+)
found := slices.Contains(items, target)
```

```go
// Before: manual clone
clone := append([]string(nil), original...)

// After (Go 1.21+)
clone := slices.Clone(original)
```

### Use `maps` package _(Go 1.21+)_

```go
// Before
clone := make(map[string]int, len(original))
for k, v := range original { clone[k] = v }

// After (Go 1.21+)
clone := maps.Clone(original)
```

### Use `cmp.Or` for default values _(Go 1.22+)_

```go
// Before
addr := os.Getenv("ADDR")
if addr == "" { addr = ":8080" }

// After (Go 1.22+)
addr := cmp.Or(os.Getenv("ADDR"), ":8080")
```

### Use `sync.OnceFunc`, `sync.OnceValue`, `sync.OnceValues` _(Go 1.21+)_

```go
// Before
var (
    once   sync.Once
    client *http.Client
)
func getClient() *http.Client {
    once.Do(func() { client = &http.Client{Timeout: 10 * time.Second} })
    return client
}

// After (Go 1.21+)
var getClient = sync.OnceValue(func() *http.Client {
    return &http.Client{Timeout: 10 * time.Second}
})
```

### Use enhanced `context` functions _(Go 1.21+)_

```go
ctx := context.WithoutCancel(parent)          // detach from parent cancellation
ctx, cancel := context.WithTimeoutCause(parent, 5*time.Second, errTimeout)
ctx, cancel := context.WithDeadlineCause(parent, deadline, errDeadline)
stop := context.AfterFunc(ctx, func() { cleanup() })
```

---

## Go 1.22 Modernizations (February 2024)

Changelog: <https://go.dev/doc/go1.22>

### SHOULD use `range` over integers _(Go 1.22+)_

```go
// Before
for i := 0; i < n; i++ { process(i) }

// After (Go 1.22+)
for i := range n { process(i) }

// When index isn't needed
for range 10 { fmt.Println("hello") }
```

### Remove loop variable shadow copies _(Go 1.22+)_

Go 1.22 changed loop variable semantics: each iteration creates a new variable. Loop variable captures (`v := v`) SHOULD be removed in Go 1.22+ codebases.

**Requirement**: The `go` directive in `go.mod` must be `go 1.22` or later for this behavior.

```go
// Before (Go < 1.22)
for _, v := range items {
    v := v // shadow copy to avoid closure bug
    go func() { process(v) }()
}

// After (Go 1.22+): safe by default
for _, v := range items {
    go func() { process(v) }()
}
```

### `math/rand` MUST be replaced with `math/rand/v2` _(Go 1.22+)_

```go
// Before
import "math/rand"
rand.Seed(time.Now().UnixNano()) // no longer needed
n := rand.Intn(100)

// After (Go 1.22+)
import "math/rand/v2"
n := rand.IntN(100) // IntN, not Intn
```

Key `math/rand/v2` changes:

- No global seed needed — automatically seeded
- `Intn` -> `IntN`, `Int63n` -> `Int64N` (renamed)
- `rand.N[T]()` generic function for any integer type
- Better algorithms (ChaCha8, PCG)
- `Read` removed — use `crypto/rand` for random bytes

### Use enhanced `net/http` routing _(Go 1.22+)_

```go
// Before: gorilla/mux or chi
r := mux.NewRouter()
r.HandleFunc("/users/{id}", getUser).Methods("GET")

// After (Go 1.22+): stdlib
mux := http.NewServeMux()
mux.HandleFunc("GET /users/{id}", getUser)

func getUser(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")
}
```

### Use `strings.CutPrefix` and `strings.CutSuffix` _(Go 1.20+)_

```go
// Before
if strings.HasPrefix(s, "Bearer ") {
    token := strings.TrimPrefix(s, "Bearer ")
}

// After (Go 1.20+)
if token, ok := strings.CutPrefix(s, "Bearer "); ok {
    // use token
}
```

### Use `reflect.TypeFor[T]()` _(Go 1.22+)_

```go
// Before
t := reflect.TypeOf((*MyInterface)(nil)).Elem()

// After (Go 1.22+)
t := reflect.TypeFor[MyInterface]()
```

### Use `database/sql.Null[T]` _(Go 1.22+)_

```go
// Before
var name sql.NullString
var age  sql.NullInt64

// After (Go 1.22+)
var name sql.Null[string]
var age  sql.Null[int64]
```

---

## Go 1.23 Modernizations (August 2024)

Changelog: <https://go.dev/doc/go1.23>

### Use iterators (`range` over functions) _(Go 1.23+)_

Go 1.23 introduced range-over-func with the `iter` package:

```go
// Before: collect all results into a slice
func AllUsers(db *sql.DB) ([]User, error) {
    rows, err := db.Query("SELECT ...")
    if err != nil { return nil, err }
    defer rows.Close()
    var users []User
    for rows.Next() {
        var u User
        rows.Scan(&u.ID, &u.Name)
        users = append(users, u)
    }
    return users, rows.Err()
}

// After (Go 1.23+): lazy iteration
func AllUsers(db *sql.DB) iter.Seq2[User, error] {
    return func(yield func(User, error) bool) {
        rows, err := db.Query("SELECT ...")
        if err != nil { yield(User{}, err); return }
        defer rows.Close()
        for rows.Next() {
            var u User
            if err := rows.Scan(&u.ID, &u.Name); err != nil {
                yield(User{}, err); return
            }
            if !yield(u, nil) { return }
        }
        if err := rows.Err(); err != nil { yield(User{}, err) }
    }
}
```

### Use iterator-based `slices` and `maps` functions _(Go 1.23+)_

```go
// Sorted keys via iterator
for k := range slices.Sorted(maps.Keys(m)) {
    fmt.Println(k, m[k])
}

// Collect iterator into slice
users := slices.Collect(maps.Values(userMap))

// Chunk a slice into batches
for chunk := range slices.Chunk(items, 100) {
    processBatch(chunk)
}
```

### Use `unique` package for value interning _(Go 1.23+)_

```go
// Before: manual string interning
var mu sync.Mutex
var interned = make(map[string]string)

// After (Go 1.23+)
handle := unique.Make(s)  // Handle[string], comparable, memory-efficient
s = handle.Value()
```

### Timer/Ticker behavior change _(Go 1.23+)_

With `go 1.23` or later in `go.mod`:

- `time.Timer` and `time.Ticker` are garbage collected without calling `Stop()`
- Timer channels are now unbuffered (capacity 0, was 1)

Remove unnecessary `Stop()` calls in defer patterns where the timer goes out of scope.

---

## Go 1.24 Modernizations (February 2025)

Changelog: <https://go.dev/doc/go1.24>

### Use generic type aliases _(Go 1.24+)_

```go
// Now valid (Go 1.24+)
type Set[T comparable] = map[T]struct{}
type Result[T any] = struct { Value T; Err error }
```

### Use `os.Root` for directory-scoped file access _(Go 1.24+)_

**Security-critical**: `os.Root` prevents path traversal attacks (CWE-22) at the OS level. Replace all manual `filepath.Clean` + `strings.HasPrefix` validation with `os.Root` when handling user-supplied paths. Symlinks resolving outside the root are rejected. Supports `Open`, `Create`, `Stat`, `OpenFile`, `Mkdir`, `Remove`, and more.

```go
// Before: manual path validation (risk of path traversal)
path := filepath.Join(baseDir, userInput)
data, err := os.ReadFile(path)

// After (Go 1.24+): safe directory-scoped access
root, err := os.OpenRoot("/opt/data")
if err != nil { return err }
defer root.Close()
f, err := root.Open(userInput) // cannot escape root directory
```

### Use `omitzero` JSON tag _(Go 1.24+)_

`omitzero` is more correct than `omitempty` for `time.Time`, `bool`, and custom types:

```go
// Before: omitempty doesn't work well for time.Time
type Event struct {
    At time.Time `json:"at,omitempty"` // zero time.Time is NOT omitted
}

// After (Go 1.24+)
type Event struct {
    At time.Time `json:"at,omitzero"` // zero time.Time IS omitted
}
```

### Use `strings.SplitSeq`, `strings.FieldsSeq`, `strings.Lines` _(Go 1.24+)_

Iterator-returning variants avoid allocating `[]string`:

```go
// Before: allocates a []string
parts := strings.Split(csv, ",")
for _, part := range parts { process(part) }

// After (Go 1.24+): lazy, zero-allocation iteration
for part := range strings.SplitSeq(csv, ",") { process(part) }
```

### `t.Context()` SHOULD replace manual `context.Background()` in tests _(Go 1.24+)_

```go
// Before
func TestFoo(t *testing.T) {
    ctx := context.Background()
}

// After (Go 1.24+): auto-cancelled when test ends
func TestFoo(t *testing.T) {
    ctx := t.Context()
}
```

### `b.Loop()` MUST be used in benchmarks _(Go 1.24+)_

```go
// Before
func BenchmarkFoo(b *testing.B) {
    for i := 0; i < b.N; i++ { foo() }
}

// After (Go 1.24+)
func BenchmarkFoo(b *testing.B) {
    for b.Loop() { foo() }
}
```

### Use `runtime.AddCleanup` instead of `runtime.SetFinalizer` _(Go 1.24+)_

```go
// Before
runtime.SetFinalizer(obj, func(o *Object) { o.Close() })

// After (Go 1.24+): more flexible, no cycle issues
runtime.AddCleanup(obj, func(resource Resource) { resource.Close() }, obj.resource)
```

### Use `weak` package for weak references _(Go 1.24+)_

```go
import "weak"

ptr := weak.Make(obj)
if v := ptr.Value(); v != nil {
    // object still alive
}
```

### Use `crypto/sha3`, `crypto/hkdf`, `crypto/pbkdf2` _(Go 1.24+)_

Replace `golang.org/x/crypto` sub-packages with standard library equivalents:

```go
// Before
import "golang.org/x/crypto/sha3"
import "golang.org/x/crypto/hkdf"
import "golang.org/x/crypto/pbkdf2"

// After (Go 1.24+)
import "crypto/sha3"
import "crypto/hkdf"
import "crypto/pbkdf2"
```

### Use tool directives in `go.mod` _(Go 1.24+)_

```go
// Before: tools.go with blank imports
//go:build tools
package tools
import (
    _ "golang.org/x/tools/cmd/stringer"
    _ "github.com/golangci/golangci-lint/cmd/golangci-lint"
)

// After (Go 1.24+): in go.mod
// tool (
//     golang.org/x/tools/cmd/stringer
//     github.com/golangci/golangci-lint/cmd/golangci-lint
// )
// Run: go tool stringer ./...
```

### Use `fmt.Appendf`, `fmt.Appendln` _(Go 1.19+, often overlooked)_

```go
// Before
buf = append(buf, fmt.Sprintf("count: %d", n)...)

// After (Go 1.19+)
buf = fmt.Appendf(buf, "count: %d", n)
```

---

## Go 1.25 Modernizations (August 2025)

Changelog: <https://go.dev/doc/go1.25>

### Use `sync.WaitGroup.Go` _(Go 1.25+)_

```go
// Before
var wg sync.WaitGroup
wg.Add(1)
go func() {
    defer wg.Done()
    process()
}()
wg.Wait()

// After (Go 1.25+)
var wg sync.WaitGroup
wg.Go(func() {
    process()
})
wg.Wait()
```

### Use `testing/synctest` for concurrent code testing _(Go 1.25+, experimental in 1.24)_

```go
// Before
func TestConcurrent(t *testing.T) {
    var count atomic.Int32
    var wg sync.WaitGroup

    wg.Add(1)
    go func() {
        defer wg.Done()
        count.Add(1)
    }()

    wg.Wait()

    // Problem: Race conditions are hard to detect, timing-dependent,
    // and flaky tests are common
    if count.Load() != 1 {
        t.Fatal("expected 1")
    }
}

// After (Go 1.25+)
func TestConcurrent(t *testing.T) {
    synctest.Test(t, func(t *testing.T) {
        var count atomic.Int32
        go func() { count.Add(1) }()
        synctest.Wait() // wait for all goroutines to park
        if count.Load() != 1 { t.Fatal("expected 1") }
    })
}
```

**Note**: Use `synctest.Test` (not `synctest.Run` which is deprecated since Go 1.25).

### Use `runtime/trace.FlightRecorder` _(Go 1.25+)_

Lightweight always-on ring-buffer tracing for production:

```go
fr := trace.NewFlightRecorder()
fr.Start()
// ... later, on error:
fr.WriteTo(file) // captures recent trace data
```

### Container-aware `GOMAXPROCS` _(Go 1.25+)_

Go 1.25 automatically respects cgroup CPU limits on Linux. Remove manual workarounds:

```go
// Before: using uber-go/automaxprocs
import _ "go.uber.org/automaxprocs"

// After (Go 1.25+): built-in, remove the import
// GOMAXPROCS is set automatically from cgroup CPU limits
```

### `encoding/json/v2` (experimental) _(Go 1.25+, GOEXPERIMENT=jsonv2)_

Major JSON revision. **Experimental** — evaluate for new code, don't migrate production yet.

---

## Go 1.26 Modernizations (February 2026)

Changelog: <https://go.dev/doc/go1.26>

### Use `errors.AsType[T]()` _(Go 1.26+)_

```go
// Before
var pathErr *os.PathError
if errors.As(err, &pathErr) {
    fmt.Println(pathErr.Path)
}

// After (Go 1.26+)
if pathErr, ok := errors.AsType[*os.PathError](err); ok {
    fmt.Println(pathErr.Path)
}
```

### Use enhanced `new()` _(Go 1.26+)_

```go
// Before: helper function needed
func ptr[T any](v T) *T { return &v }
cfg := Config{Timeout: ptr(30)}

// After (Go 1.26+)
cfg := Config{Timeout: new(30)}
```

### Use `crypto/hpke` _(Go 1.26+)_

Hybrid Public Key Encryption (RFC 9180) is now in the standard library.

### Green Tea GC enabled by default _(Go 1.26+)_

10-40% reduction in GC overhead. Review and potentially remove manual GC tuning (`GOGC`, `GOMEMLIMIT`) that compensated for older GC behavior.

### Modernized `go fix` _(Go 1.26+)_

Go 1.26 rewrote `go fix` to apply modernize analyzers automatically:

```bash
go fix ./...  # applies safe modernize transformations
```

---

## General Modernization (Any Version)

### Code MUST use `any` instead of `interface{}` _(Go 1.18+)_

```go
// Before
func process(data interface{}) interface{} { ... }

// After (Go 1.18+)
func process(data any) any { ... }
```

### Use generics instead of `interface{}` + type assertions _(Go 1.18+)_

```go
// Before
func Contains(slice []interface{}, item interface{}) bool { ... }

// After (Go 1.18+)
func Contains[T comparable](slice []T, item T) bool { ... }
// Or better (Go 1.21+): slices.Contains
```

### Use `errors.Join` instead of multi-error libraries _(Go 1.20+)_

```go
// Before: hashicorp/go-multierror or uber-go/multierr
errs = multierror.Append(errs, err1)
return errs.ErrorOrNil()

// After (Go 1.20+)
return errors.Join(err1, err2)
```

### Use `net.JoinHostPort` instead of `fmt.Sprintf` _(any version)_

```go
// Before (broken for IPv6)
addr := fmt.Sprintf("%s:%d", host, port)

// After (handles IPv6 correctly: [::1]:8080)
addr := net.JoinHostPort(host, strconv.Itoa(port))
```
