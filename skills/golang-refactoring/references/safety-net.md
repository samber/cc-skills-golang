# The Coverage-Adaptive Safety Net

The right amount of caution before a refactor is not a fixed policy — it is gated on how well-tested the _blast radius_ already is, not on the project's global coverage number. A codebase sitting at 90% coverage overall can still have the one function you're about to touch at 0%, and a codebase at 30% overall can have your target function fully pinned by table-driven tests. Measure the code you're actually going to change, then pick the tier below.

## The Three Tiers

- **HIGH coverage on the blast radius (roughly ≥80% function coverage via `go tool cover -func`)** — refactor aggressively with tools, and trust the green bar.
  - Prefer gopls Rename/Inline/Extract, `eg`/`gofmt -r` for bulk mechanical changes, and generated `go/analysis` fixers over hand-edits.
  - Run the fast net (build/vet/test) after each step, and escalate to `-race`/`-bench` only when the step touches concurrency or a hot path.
  - Larger steps are acceptable here because a well-covered blast radius means the net catches a regression within one test run — the cost of being wrong is cheap and immediate, so there is little reason to slow down.
- **MEDIUM coverage (~40-80%)** — harden the blast radius before refactoring it, not after.
  - First measure exactly what the change touches: gopls references and call hierarchy tell you the real call graph, not the one you remember from reading the code (see the planning gate in [workflow.md](workflow.md)).
  - Add targeted table-driven or golden tests covering precisely those paths, confirm they pass against the current code, and only then refactor.
  - The step that's easy to skip and shouldn't be: re-run with `-coverprofile` afterward and check that the new tests actually exercise the lines you're about to change. A test that imports the right package but never reaches the branch you're editing gives false confidence — it looks like safety net from the outside and catches nothing.
- **LOW/ZERO coverage (<40%, or the specific touched lines are uncovered even if the package average looks fine) — Feathers mode** — write characterization (a.k.a. golden or pinning) tests _first_, capturing what the code actually does today, warts and all, before changing a single line.
  - This is deliberately not a correctness test — you are not asserting the code is right, only recording what it currently does so a refactor can be checked against it.
  - Find a seam (below) and introduce the minimum needed to make the code testable.
  - Restrict yourself to the safest, tool-verified refactorings only — gopls Rename and Inline, both behavior-preserving by construction — and avoid Extract or any cross-package move until a real net exists to check them against.
  - Prefer Sprout/Wrap (see [catalog.md](catalog.md)) to add new behavior in a new, tested function rather than editing untested code in place.
  - Running `deadcode -test` first is worth the two minutes — some of what looks like "untested code that needs a net" turns out to be exported API nothing actually calls, in which case the honest fix is deletion, not testing.

| Tier | Blast-radius coverage | Strategy | Allowed transforms |
| --- | --- | --- | --- |
| **High** | ≥80% function coverage | Refactor first, verify after each step | gopls Rename/Inline/Extract, `eg`/`gofmt -r`, generated `go/analysis` fixers |
| **Medium** | ~40-80% | Harden the touched paths, confirm green, then refactor | Same as High, once targeted tests exist and `-coverprofile` confirms they hit the touched lines |
| **Low/Zero** | <40%, or the touched lines specifically | Characterize first (Feathers mode), introduce a seam, refactor last | gopls Rename/Inline only; Sprout/Wrap for new behavior; no Extract or cross-package move until a net exists |

**Diagnose:** 1- `go test -covermode=atomic -coverpkg=./... -coverprofile=cover.out ./...` — runs the suite and produces a coverage profile scoped to the blast radius's packages 2- `go tool cover -func=cover.out` — ranks every function by coverage percentage; scan this for the specific functions you're about to touch, not the package-level average 3- `go tool cover -html=cover.out` — a visual red/green view of the exact touched lines, useful when `-func`'s percentage for a function is ambiguous about which branches are actually green

Two caveats worth internalizing before trusting any number this produces:

- **Go's coverage is statement coverage, not branch coverage** — a line inside an `if` block that ran once counts as fully covered even if the `else` never executed and even if a `switch` only ever hit one `case`. A function reporting 100% can still have an untested branch; treat the percentage as a floor on how much is exercised, not proof that the logic is correct, and read the actual branches in the code you're about to touch rather than trusting the summary.
- **`go test ./...` silently drops any package that has no `_test.go` file from the aggregate** — it isn't counted as 0%, it simply isn't in the report at all, which makes an untested package invisible instead of visibly red. Passing `-coverpkg=./...` (as in the Diagnose command above) forces every package in the module into the profile so a silently-untested dependency doesn't slip past the tier decision unnoticed.

## Seams — What to Introduce When There's No Net Yet

- A seam, in Michael Feathers's sense, is a place in the code where you can alter behavior without editing that exact spot.
- Seams are how Feathers mode gets a fake into a test without first performing the larger refactor the test is meant to protect against.
- Two seam types matter in Go:
  - An **object seam** is an interface, or a function-typed field or parameter, injected at the point of construction — a test substitutes a fake implementation through that injection point instead of exercising the real dependency. This is the seam type that matters most in Go, because interfaces are satisfied implicitly: introducing one at the point of use requires touching only the consumer, never the producer package, which means you can add a seam to legacy code without an invasive edit to whatever it depends on.
  - A **link/build-tag seam** swaps an entire implementation at build time via `//go:build` constraints; it's used far more rarely, mostly for platform- or environment-specific substitutions where an interface would be overkill.
- The enabling move for untested code with no seam yet: extract the smallest possible interface — often just one method — at the exact call site where the untested code depends on something external (a database client, the filesystem, a clock), and inject the concrete implementation through a constructor parameter instead of constructing it inline.
  - This single move does two things at once: it breaks a potential import cycle between the consumer and whatever concrete type it depended on, and it opens the door for a fake in a characterization test, without requiring any change to the producer side at all.

```go
// Before — no seam: NewReport constructs its own client, so a test
// exercising Generate has no way to substitute a fake and is stuck
// hitting a real database.
func NewReport(dsn string) *Report {
    db, _ := sql.Open("postgres", dsn)
    return &Report{db: db}
}

func (r *Report) Generate(ctx context.Context, id int) (Summary, error) {
    row := r.db.QueryRowContext(ctx, "SELECT ... WHERE id = $1", id)
    // ...
}

// After — a one-method interface extracted at the point of use;
// the concrete *sql.DB already satisfies it implicitly, so the
// producer package needs no change at all.
type rowQuerier interface {
    QueryRowContext(ctx context.Context, query string, args ...any) *sql.Row
}

func NewReport(db rowQuerier) *Report {
    return &Report{db: db}
}

func (r *Report) Generate(ctx context.Context, id int) (Summary, error) {
    row := r.db.QueryRowContext(ctx, "SELECT ... WHERE id = $1", id)
    // ... unchanged — a characterization test can now inject a fake rowQuerier
}
```

→ See `samber/cc-skills-golang@golang-design-patterns` skill for constructor and dependency-injection patterns this move builds on, and [catalog.md](catalog.md) in this skill for the Sprout/Wrap mechanics that typically pair with a freshly introduced seam.

## Verification Command Reference

This is the fast net from the Core Loop in [SKILL.md](../SKILL.md), escalated only as far as the change actually requires:

```bash
go build ./...                              # fastest gate — compile errors
go vet ./...                                 # correctness checks the compiler doesn't do
go test ./...                                # full test suite
go test -run TestName ./pkg/...              # target one test while iterating
go test -race ./...                          # concurrency changes — see samber/cc-skills-golang@golang-testing for race-detector and testing/synctest mechanics
go test -covermode=atomic -coverpkg=./... -coverprofile=cover.out ./...
go tool cover -func=cover.out                 # per-function and total coverage, ranked
go tool cover -html=cover.out                 # visual red/green source view
go test -bench=. -benchmem -count=10 > new.txt   # capture before AND after with the same command, then:
benchstat old.txt new.txt                     # `~` means no statistically significant difference — the desired result for a behavior-preserving refactor; anything else is a signal to stop and investigate, not noise to shrug off
```

## Cross-References

- → See `samber/cc-skills-golang@golang-testing` skill for general test-writing craft, race-detector mechanics, and `testing/synctest` — this file assumes them as a baseline and only covers when a refactor's safety net needs to reach for them.
- → See `samber/cc-skills-golang@golang-benchmark` skill for interpreting a `benchstat` delta and the full profiling methodology.
- [catalog.md](catalog.md) — the Fowler refactoring catalog mapped to Go, including the Sprout/Wrap entries referenced in the Feathers-mode and seams sections above.
- [workflow.md](workflow.md) — the planning gate that measures the blast radius this file's tiers are gated on, and the human-checkpoint rule for touching untested code.
