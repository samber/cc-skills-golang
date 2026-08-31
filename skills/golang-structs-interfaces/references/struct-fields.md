# Struct Fields: Tags and Copy Safety

## Struct Field Tags

Field tags drive every reflection-based encoder and decoder. Exported fields in serialized structs MUST have field tags — without one, the encoder falls back to the Go field name, so renaming a field silently changes the wire format:

```go
type Order struct {
    ID        string    `json:"id"         db:"id"`
    UserID    string    `json:"user_id"    db:"user_id"`
    Total     float64   `json:"total"      db:"total"`
    Items     []Item    `json:"items"      db:"-"`
    CreatedAt time.Time `json:"created_at" db:"created_at"`
    DeletedAt time.Time `json:"-"          db:"deleted_at"`
    Internal  string    `json:"-"          db:"-"`
}
```

| Directive               | Meaning                                     |
| ----------------------- | ------------------------------------------- |
| `json:"name"`           | Field name in JSON output                   |
| `json:"name,omitempty"` | Omit field if zero value                    |
| `json:"name,omitzero"`  | Omit field if zero (Go 1.24+, type-aware)   |
| `json:"-"`              | Always exclude from JSON                    |
| `json:"-,"`             | Field literally named `-`                   |
| `json:",string"`        | Encode number/bool as JSON string           |
| `db:"column"`           | Database column mapping (sqlx, etc.)        |
| `yaml:"name"`           | YAML field name                             |
| `xml:"name,attr"`       | XML attribute                               |
| `validate:"required"`   | Struct validation (go-playground/validator) |

Notes that bite in production:

- **Unexported fields are never serialized**, tag or not. A tag on an unexported field is dead weight and `go vet` flags the malformed ones only.
- **`omitempty` is length/zero based, not semantic.** It drops `0`, `""`, and `false`, so an explicit "zero" value becomes indistinguishable from "absent". Use a pointer, `mo.Option[T]`, or `omitzero` (Go 1.24+) when the difference matters.
- **Tag syntax is unchecked at compile time.** A missing backtick or a `json: "id"` with a stray space produces a silently ignored tag. `go vet`'s `structtag` analyzer catches malformed tags — run it in CI.

**Diagnose:** 1- `go vet ./...` — the `structtag` analyzer reports malformed or duplicated tags 2- round-trip test: marshal, unmarshal, compare — catches field-name drift the compiler cannot see

## Preventing Struct Copies with `noCopy`

Some structs must never be copied after first use (e.g., those containing a mutex, a channel, or internal pointers) — copying duplicates the lock state, so two goroutines end up guarding two different mutexes and the invariant silently disappears. Embed a `noCopy` sentinel to make `go vet` catch accidental copies:

```go
// noCopy may be added to structs which must not be copied after first use.
// See https://pkg.go.dev/sync#noCopy
type noCopy struct{}

func (*noCopy) Lock()   {}
func (*noCopy) Unlock() {}

type ConnPool struct {
    noCopy noCopy
    mu     sync.Mutex
    conns  []*Conn
}
```

`go vet` reports an error if a `ConnPool` value is copied (passed by value, assigned, returned by value, ranged over). The detection is purely name-based: `vet`'s `copylocks` analyzer flags any type whose fields implement `Lock`/`Unlock`. This is the same technique the standard library uses for `sync.WaitGroup`, `sync.Mutex`, `strings.Builder`, and others.

Pass these structs by pointer:

```go
// Good
func process(pool *ConnPool) { ... }

// Bad — go vet will flag this
func process(pool ConnPool) { ... }
```

**Diagnose:** 1- `go vet ./...` — `copylocks` reports every value copy of a lock-bearing struct 2- `go test -race ./...` — surfaces the data races a silent copy introduces
