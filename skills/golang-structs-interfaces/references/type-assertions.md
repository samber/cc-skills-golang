# Type Assertions & Type Switches

## Safe Type Assertion

Type assertions MUST use the comma-ok form. The single-value form panics when the dynamic type does not match, turning a recoverable branch into a crash:

```go
// Good — safe
s, ok := val.(string)
if !ok {
    // handle
}

// Bad — panics if val is not a string
s := val.(string)
```

## Type Switch

Discover the dynamic type of an interface value:

```go
switch v := val.(type) {
case string:
    fmt.Println(v)
case int:
    fmt.Println(v * 2)
case io.Reader:
    io.Copy(os.Stdout, v)
default:
    fmt.Printf("unexpected type %T\n", v)
}
```

Cases are evaluated in order, so put concrete types before interface types — a concrete type listed after an interface it satisfies is unreachable.

A `nil` interface value matches `case nil`, not `default`. Add that case explicitly when nil is a valid input, otherwise it silently falls through to the `default` branch and gets reported as an unexpected type.

## Optional Behavior with Type Assertions

Check if a value supports additional capabilities without requiring them upfront. This keeps the declared parameter type minimal while still exploiting richer implementations:

```go
type Flusher interface {
    Flush() error
}

func writeData(w io.Writer, data []byte) error {
    if _, err := w.Write(data); err != nil {
        return err
    }
    // Flush only if the writer supports it
    if f, ok := w.(Flusher); ok {
        return f.Flush()
    }
    return nil
}
```

This pattern is used extensively in the standard library (e.g., `http.Flusher`, `io.ReaderFrom`, `io.WriterTo`).

## Asserting to an Interface, not a Concrete Type

Assert to the smallest interface that carries the behavior you need rather than to a concrete type. Asserting to `*os.File` binds the code to one implementation; asserting to `interface{ Sync() error }` accepts every type that can do the job.

## Errors

Error inspection has dedicated helpers — `errors.As` walks the wrap chain, a plain type assertion does not. A bare `err.(*MyError)` misses an error that was wrapped with `%w` anywhere up the stack.

→ See `samber/cc-skills-golang@golang-error-handling` skill for error wrapping and inspection.
