# Linter Reference

golangci-lint v2 uses a `.golangci.yml` with `version: "2"` at the project root.

Key sections of `.golangci.yml`:

- **`run`** — concurrency, timeout, test inclusion, directory exclusions
- **`linters.enable`** / **`linters.disable`** — which linters are active
- **`linters.settings`** — per-linter thresholds and options
- **`formatters`** — code formatters (gofmt, gofumpt)
- **`issues`** — output limits, exclusion rules

To add a linter: add it to `linters.enable` and optionally configure it in `linters.settings`.

To disable a linter: move it to `linters.disable` with a comment explaining why.

## Linter Categories

The recommended configuration enables linters across these domains:

| Domain | Linters | Catches |
| --- | --- | --- |
| Correctness | govet, staticcheck, unused, errcheck, nilerr, forcetypeassert, copyloopvar | Bugs, unchecked errors, stdlib misuse |
| Style | gocritic, revive, wsl_v5, whitespace, godot, misspell, predeclared, errname | Readability, naming, consistency |
| Complexity | gocyclo, nestif, funlen, dupl | Overly complex or duplicated code |
| Performance | perfsprint, unconvert, ineffassign, goconst | Conversions, string ops, dead assigns |
| Security | bodyclose, sqlclosecheck, rowserrcheck | Resource leaks (HTTP, SQL) |
| Testing | thelper, paralleltest, testifylint | Test hygiene and best practices |
| Modernization | modernize, intrange, usestdlibvars, exhaustive, nolintlint | Modern Go idioms, lint hygiene |
| Formatting | gofmt, gofumpt | Code formatting |

All linters are enabled in the [recommended .golangci.yml](./.golangci.yml), organized by domain.

### Correctness & Safety

- **govet** — Go's built-in checker: copylocks, printf format mismatches, struct tag validation, context stored in structs, unreachable code, nil dereferences
- **staticcheck** — Extensive static analysis: deprecated APIs, common mistakes, unnecessary code, simplifications, misuse of standard library
- **unused** — Detects unused variables, functions, types, and struct fields
- **errcheck** — Ensures all error returns are checked, including type assertions (configured with `check-type-assertions: true`)
- **nilerr** — Detects returning nil error when `err` is non-nil (common source of silent failures)
- **forcetypeassert** — Flags type assertions without the comma-ok check (`v := x.(T)` instead of `v, ok := x.(T)`)
- **copyloopvar** — Detects loop variable copy issues (Go 1.22+)

### Style & Readability

- **gocritic** — Opinionated style checks: unnecessary conversions, range copies, append-assign patterns, redundant code
- **revive** — Naming conventions for exported types, unexported returns, receiver naming, error naming, stuttered package names
- **wsl_v5** — Whitespace and blank line rules for visual grouping and readability
- **whitespace** — Detects trailing whitespace and unnecessary blank lines in function bodies
- **godot** — Ensures exported-symbol comments end with a period
- **misspell** — Catches common English misspellings in identifiers and comments
- **predeclared** — Flags shadowing of Go built-in identifiers (e.g., naming a variable `len`, `cap`, `error`)
- **errname** — Enforces error naming conventions: error types suffixed with `Error` (e.g., `DecodeError`), error variables prefixed with `Err` (e.g., `ErrNotFound`)

### Complexity

- **gocyclo** — Cyclomatic complexity threshold (configured: 13). Functions exceeding this should be split
- **nestif** — Detects deeply nested if/else chains that harm readability
- **funlen** — Function length limits (configured: 120 lines, 80 statements)
- **dupl** — Code duplication detection (configured: 20 token threshold)

### Performance

- **perfsprint** — Suggests faster alternatives to `fmt.Sprintf` (e.g., `strconv.Itoa` instead of `fmt.Sprintf("%d", n)`)
- **unconvert** — Detects unnecessary type conversions (e.g., `int(x)` when `x` is already `int`)
- **ineffassign** — Detects assignments to variables that are never subsequently read
- **goconst** — Detects repeated string/number literals that should be extracted to constants (configured: min 2 chars, min 3 occurrences)

### Security & Resources

- **bodyclose** — Ensures HTTP response bodies are closed (unclosed bodies leak connections)
- **sqlclosecheck** — Ensures `sql.Rows` and `sql.Stmt` are closed after use
- **rowserrcheck** — Ensures `sql.Rows.Err()` is checked after iteration

### Testing

- **thelper** — Ensures test helpers call `t.Helper()` so failures report the correct call site
- **paralleltest** — Detects tests and subtests missing `t.Parallel()` calls
- **testifylint** — Enforces testify best practices (e.g., `assert.Equal(t, expected, actual)` over `assert.True(t, expected == actual)`)

### Modernization & Meta

- **modernize** — Detects code that can be rewritten using newer Go features (requires golangci-lint v2.6.0+)
- **intrange** — Suggests `range N` over C-style `for i := 0; i < N; i++` loops (Go 1.22+)
- **usestdlibvars** — Replaces hardcoded strings/numbers with stdlib constants (e.g., `http.MethodGet` instead of `"GET"`)
- **exhaustive** — Ensures switch statements on enum types cover all possible values
- **nolintlint** — Enforces proper `//nolint` directive usage: requires linter name and justification comment (configured with `require-explanation` and `require-specific`)

### Formatting

Formatters run via `golangci-lint fmt ./...`:

- **gofmt** — Standard Go formatter (canonical formatting)
- **gofumpt** — Stricter formatter with extra rules (configured with `extra-rules: true`): consistent empty lines, grouped imports, simplified code patterns
