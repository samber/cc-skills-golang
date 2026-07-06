# Structural Constraints: Import Cycles, Package Boundaries, Type Moves, API Evolution

Go enforces a handful of structural rules at compile time that other languages leave to convention or linting. This file covers the load-bearing ones: why import cycles are a hard error rather than a warning, how to design a package boundary so it doesn't need to be redesigned again, the officially-blessed mechanism for moving a type across packages without breaking every caller at once, and how to evolve an exported API without a flag day.

## Breaking Import Cycles

- Go compiles packages leaf-to-root in dependency order: before compiling package `X`, the compiler must have already finished compiling everything `X` imports, because it needs their compiled type information to type-check `X`.
- An import cycle — `X` imports `Y`, `Y` imports `X` (directly or transitively) — has no valid compilation order, so `go build` rejects it outright as `import cycle not allowed`. This is not a style preference; there is no fallback behavior to fall back to.

Four strategies fix a cycle, in preference order:

| # | Strategy | Call-site cost | Best when |
| --- | --- | --- | --- |
| 1 | Consumer-side interface | None — no call site changes anywhere | The consumer only calls one or two methods on the producer's type |
| 2 | Extract shared type to a leaf package | Import path changes on both sides | Both packages genuinely need the _same concrete type_, not just its behavior |
| 3 | `internal/` package | Import path changes for the shared code only | The shared code should never become part of the public API |
| 4 | Mediator/bridge package | New package, both sides delegate to it | 1–3 don't fit the shape of the coupling |

### 1. Consumer-side interface (dependency inversion)

- The idiomatic first move, and the cheapest one, because it requires zero changes at any call site anywhere in the codebase.
- If package `x` only _uses_ behavior from package `y` — it calls a method or two on `y`'s concrete type, it doesn't need the type itself — define a small interface in `x` naming just those methods.
- Go's implicit interface satisfaction means `y`'s existing type already satisfies that interface without `y` importing anything from `x` or even being aware `x`'s interface exists:

```go
// package x (consumer)
type Storer interface {
    Store(ctx context.Context, key string, val []byte) error
}

func Process(s Storer) error { /* uses s.Store, no import of package y */ }
```

```go
// package y — unchanged, already satisfies x.Storer implicitly
type Store struct{ /* ... */ }
func (s *Store) Store(ctx context.Context, key string, val []byte) error { /* ... */ }
```

- `x` no longer imports `y` at all; `y` never imported `x` to begin with.
- The cycle is gone because one direction of the dependency graph was never real — `x` never needed `y`'s concrete type, only a name for the behavior it called.

### 2. Extract shared types to a new/lower package

- Works because Go's package model is flat within a module — a nested subdirectory is still a fully distinct, independently importable package — so pulling the types both `x` and `y` need into a small new leaf package that both can import breaks the cycle by construction: the leaf package imports neither.
- Be honest about the cost: in a real codebase a single cycle can span five or more packages once you trace every type both sides share, so this is the "correct but sometimes painful" option next to the surgical, call-site-free consumer-side interface above.

### 3. `internal/` packages

- Share code between related packages without widening the public API.
- Anything rooted under an `internal/` directory is importable only by packages rooted at the parent of that `internal/` directory — this lets two sibling packages share implementation detail through a common `internal/` package without either becoming part of the module's public surface, and without pulling either sibling into the other.

### 4. Mediator/bridge package

- A last resort when 1–3 don't fit the shape of the dependency: a new package holding the shared functionality that both `x` and `y` delegate to, absorbing the coupling neither side wants to own.
- Reach for this only after confirming a consumer-side interface can't express the relationship — it usually can.

An `internal/` layout for strategy 3 looks like this — note that both `billing` and `shipping` can import `order/internal/model`, but nothing outside the `order` tree can:

```
order/
├── billing/
│   └── billing.go        // imports order/internal/model
├── shipping/
│   └── shipping.go        // imports order/internal/model
└── internal/
    └── model/
        └── order.go        // shared type, invisible outside order/
```

## Package Boundary Design

- **Accept interfaces, return structs.**
  - Accepting a narrow interface as a parameter maximizes what a caller can pass — including a test fake that implements only the one or two methods the function actually calls — without the function ever needing to import the caller's concrete types.
  - Returning a concrete struct preserves full type information at the call site, which matters because _that_ caller's own consumers get to define their own narrow interface later, on their side, without the original producer ever having had to anticipate what subset of behavior a future caller would need.
- **Define interfaces where they are consumed, not where they are implemented.** The companion rule, and the one that actually prevents cycles rather than just describing good taste.
  - A consumer package declares the interface naming only the methods it calls; the producer package never imports it, never knows it exists, and satisfies it purely because Go's interface satisfaction is structural.
  - This is exactly the mechanism in the consumer-side-interface fix above — it isn't a separate rule, it's the same rule applied proactively during design instead of reactively during a cycle break.
- **Caveat: this is a heuristic, not dogma.**
  - Don't mechanically split every struct into an interface-plus-implementation pair on the theory that it's "more testable" — a concrete struct with no interface is simpler to read, and an interface with exactly one implementation and no test-double need is pure indirection.
  - Don't return an interface from a constructor just because "it might be more flexible later" — that flexibility has a name (YAGNI) and a cost (the caller loses type information it might have wanted).
  - → See `samber/cc-skills-golang@golang-project-layout` skill for the directory/package layout conventions this section assumes, and `samber/cc-skills-golang@golang-design-patterns` skill for judging when introducing an interface is the right call versus premature abstraction.

### Splitting a god package

- Before reaching for a full package split, gopls's `refactor.extract.toNewFile` code action handles the lighter-weight case: moving a top-level declaration to a new file in the _same_ package, which is often enough to make a bloated package navigable without touching its import graph at all.
- gopls also has an experimental `source.splitPackage` code action that assigns top-level declarations to acyclic components as a starting point for an actual package split — treat its output as a draft partition to review, not a final answer, since it can't know which grouping matches the domain boundaries you actually want.

## Moving Types Across Packages: Type Aliases for Gradual Code Repair

- This is the single most load-bearing Go-specific refactoring technique, and it exists because of a problem unique to Go's type system: type identity is tied to the fully-qualified name, so `pkg2.T` is a genuinely different type from `pkg1.T` even when their underlying definitions are byte-for-byte identical.
- You cannot assign one to the other, cannot use one where the other is expected, and — unlike a moved function (re-exportable as a thin wrapper) or a moved variable/constant (re-declarable pointing at the new location) — there was no way to migrate callers gradually.
- Before Go 1.9 this blocked real large-scale refactors: moving a type meant a single atomic commit touching every call site in the module, because there was no intermediate state where both the old and new names worked.

The fix is `type A = B` — a **type alias**, not a new named type.

- It declares that `A` and `B` are the _same_ type, not merely convertible: code written against the old name and code written against the new name interoperate exactly, with zero runtime cost and no wrapper function needed anywhere.
- This was added to the language specifically, per its own design proposal, to "enable gradual code repair during large-scale refactorings, in particular moving a type from one package to another in such a way that code referring to the old name interoperates with code referring to the new name."

The migration recipe, as a fixed sequence:

```go
// Step 1 — new package: introduce the real definition in its new home.
package newpkg

type NewName struct {
    // ... real fields
}
```

```go
// Step 2 — old package: replace the original declaration with an alias,
// and mark it deprecated so tooling and IDEs surface the migration.
package oldpkg

// Deprecated: use newpkg.NewName instead.
type OldName = newpkg.NewName
```

1. Introduce the type in its new home package with its real definition.
2. In the old package, replace the original type declaration with an alias to the new one, and mark it `// Deprecated: use newpkg.NewName instead` — a doc comment recognized by tooling and editors.
3. Migrate callers to the new import path incrementally, one PR or one package at a time. Both names remain fully valid and interchangeable throughout this entire period — there is no flag day, no big-bang commit, and no window where some callers are broken while others are fixed.
4. Once nothing references the old name, delete the alias.

Go 1.24 extended type aliases to carry type parameters, so this same recipe applies unchanged when the type being moved is generic.

## Exported API Surface and Versioning

- **Deprecate before deleting.** A doc comment beginning `// Deprecated: ...` is recognized by tooling and IDEs and surfaces as a strikethrough or warning at every call site, which gives callers time to migrate before the symbol disappears — deleting an exported identifier outright breaks every downstream module at their next `go build` with no warning beforehand.
- **Prefer additive changes.** Go's own compatibility promise sets the default posture: prefer additive changes (new function, new optional field, new method) over changing an existing signature, because additive changes never break an existing caller. A change that must break existing callers is not a minor version bump — it's a new major version.
- **Semantic import versioning** is how Go expresses that: a v2+ module carries a `/vN` suffix in both its module path and every importer's import path (e.g. `example.com/mod/v2`).
  - This is what lets v1 and v2 of the same module coexist in the same build — the two are, to the toolchain, simply different packages with different import paths.
  - It's what lets callers migrate one package at a time rather than all at once, the same gradual-migration property a type alias gives you _within_ one version, now applied _across_ major versions.
  - During the transition, the v2 implementation can be written as a thin wrapper over v1 (or vice versa, whichever side holds the canonical logic) to avoid maintaining two divergent copies of the same behavior.
- **`retract` directives** mark an already-shipped defective version as unfit for use in `go.mod` — `go get` and `go list -m -u` surface the retraction to anyone who depends on it, without requiring the broken version to be deleted from the module proxy:

```
module example.com/mod

go 1.24

retract (
    v1.2.0 // published with a data-loss bug, see #123
    [v1.2.1, v1.2.3] // range retraction — a whole span of bad releases
)
```

## `init()`, Global State, and Package-Level Vars as a Refactoring Target

- `init()` ordering and mutable package-level state are a common source of hidden coupling: a caller of a function has no way to see, from the call site, that the function's behavior depends on some other package's `init()` having already run, or on a global variable some unrelated code path mutated earlier in the program's lifetime.
- That coupling doesn't show up in a signature, so it doesn't show up in a diff, and it's exactly the kind of dependency that makes a piece of code unsafe to move or test in isolation.
- The refactor is toward explicit construction: a constructor function that returns a struct, with dependencies passed in as parameters rather than reached for through a package-level variable or `init()`-populated singleton.
  - This doesn't remove the dependency — the code still needs what it needed before — it makes the dependency an explicit, visible seam in the function signature instead of an implicit one buried in the package's `init()`.
  - → See `samber/cc-skills-golang@golang-design-patterns` skill for constructor and dependency-injection patterns, and [safety-net.md](safety-net.md) in this skill for how this same seam is what a Feathers-style characterization test exploits to get coverage before a risky change.

## Generics — When a Refactor Toward Them Is Warranted

- Narrower case, briefly: introduce a type parameter only when the _logic_ is genuinely identical across types, not merely similar.
- When the _behavior_ differs per type — even by one branch — that's an interface, not a generic; a generic with a type switch inside it is usually an interface wearing a disguise.
- A practical litmus test: reach for a generic when a type parameter would eliminate a type assertion that's currently in the code, and the constraint it needs stays narrow — `comparable`, `cmp.Ordered`, or a small one-method interface.
- Write the concrete version first; refactor to generic only once the duplication is real and already committed in two or more places, not anticipated for a future third caller that may never arrive.
- As of this writing, Go has no method-level type parameters, which blocks fluent generic method chaining (`Map` returning a differently-typed receiver) as a design option — plan around that limitation rather than discovering it mid-refactor.
- Verify a generics migration the same way as any other refactor, no special-casing: `go build ./... && go vet ./...` plus the full test suite for the touched packages.

## Common Mistakes

| Mistake | Fix | Why |
| --- | --- | --- |
| Moving a type by defining `type OldName NewName` (a new named type) instead of `type OldName = NewName` | Use `=` — a real type alias | Without `=` this declares a _distinct_ type; every existing value of the old type now fails to assign to the new one, which is the exact break the alias was supposed to avoid |
| Breaking a cycle by moving the _producer's_ concrete type into the consumer's package | Define the interface in the consumer instead, leave the producer's type where it is | Moving the concrete type usually just relocates the cycle to whatever else the producer's type depends on |
| Deleting an exported symbol in the same PR that deprecates it | Deprecate first, land, wait for a release cycle, delete later | Callers outside the module have no chance to react to a deprecation notice they never saw before the symbol vanished |
| Bumping a module to v2 without adding `/v2` to the module path | Add the `/v2` suffix to both `go.mod`'s `module` line and every import path | Without the suffix, Go's module resolution can't tell the new major version apart from the old one, and existing v1 importers silently get pulled onto breaking code on their next `go get -u` |
| Reaching for a generic the first time a second, similar-looking function appears | Wait for a third real occurrence with identical logic, or an existing type assertion the generic would remove | Two occurrences are often coincidentally similar rather than logically identical; a premature generic ossifies an abstraction around a coincidence |

## Cross-References

- → See `samber/cc-skills-golang@golang-project-layout` skill for directory/package layout conventions.
- → See `samber/cc-skills-golang@golang-design-patterns` skill for when an interface is the right design choice versus premature abstraction, and for constructor/DI patterns.
- → See [catalog.md](catalog.md) in this skill for the Fowler catalog entries (Extract Interface, Change Function Declaration, Move Function) these structural moves build on.
- → See [workflow.md](workflow.md) in this skill for staging a cross-package move or package split as an ordered sequence of small PRs.
