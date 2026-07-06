# The Fowler Catalog, Mapped to Go

Each entry below follows the same structure: **Motivation** (why the refactoring earns its keep), **Smell trigger** (the code shape that signals it's time), **Go mechanics** (what the transform actually looks like in Go), **Tool** (what performs it), and **Risk** (matching the Risk Stratification table in [SKILL.md](../SKILL.md)). Entries are grouped by family, following the shape of Fowler's _Refactoring_ catalog.

## Extract Function / Extract Method

- **Motivation:** A function doing more than one job is harder to name, test, and reuse than two functions each doing one job — splitting it restores a name for the piece that was previously anonymous.
- **Smell trigger:** Long Function — a function whose body mixes several levels of abstraction, or where a comment introduces a block that could instead be the function's name.
- **Go mechanics:** Select the statements to extract; the tool infers the parameter list from free variables and the return list from variables used after the extracted block. For a method, it additionally infers the receiver.
- **Tool:**

```
gopls codeaction -exec -kind=refactor.extract.function file.go:#start,#end
gopls codeaction -exec -kind=refactor.extract.method   file.go:#start,#end
```

Editor-integrated as "Extract function"/"Extract method" in the code actions menu.

- **Risk:** Medium. gopls's own documentation describes Extract as "considerably less rigorous" than Rename or Inline, and it is known to drop comments attached to the extracted statements (golang/go#20744). Always diff the result and re-read the extracted body — don't trust it as behavior-preserving by construction the way Rename and Inline are.

## Inline Function / Inline Call

- **Motivation:** A wrapper that no longer adds a distinct name, or a level of indirection that has stopped paying for itself, is pure navigation overhead for the reader — inlining removes the detour.
- **Smell trigger:** A trivial one-line forwarding function, or a Middle Man that has accreted no behavior of its own since it was introduced.
- **Go mechanics:** The call site is replaced with the callee's body, with real substitution rather than naive text-splicing: arguments that have side effects are hoisted into `var` temporaries instead of being duplicated wherever the parameter is used, implicit conversions at the call boundary are made explicit, and a callee body containing `defer` is wrapped in an immediately-invoked function literal so the deferred call still fires at the right point. Inline cannot cross a dynamic dispatch (interface method call, function value) or inline a generic function.
- **Tool:**

```
gopls codeaction -exec -kind=refactor.inline.call file.go:#offset
```

- **Risk:** Low. Alongside Rename, this is one of the two gopls operations that is provably behavior-preserving by construction — it refuses rather than produce a semantically wrong inline.

## Extract Variable / Inline Variable, Extract Constant

- **Motivation:** A repeated or unexplained expression forces every reader to re-derive its meaning at each occurrence; giving it a name states the meaning once.
- **Smell trigger:** The same non-trivial expression appears more than once, or a single occurrence is opaque enough that a reader has to pause and work out what it computes.
- **Go mechanics:** Extract Variable introduces a `:=` binding immediately above the first use; the `-all` variant rewrites every syntactic occurrence of the expression in scope to reference the new variable. Extract Constant does the same for a literal that deserves a name and compile-time immutability. Inline Variable is the reverse: substitute the variable's value at its use site(s) and remove the binding.
- **Tool:**

```
gopls codeaction -exec -kind=refactor.extract.variable     file.go:#start,#end
gopls codeaction -exec -kind=refactor.extract.variable-all file.go:#start,#end
gopls codeaction -exec -kind=refactor.extract.constant     file.go:#start,#end
gopls codeaction -exec -kind=refactor.inline.variable      file.go:#offset
```

- **Risk:** Low.

## Rename

- **Motivation:** A misleading identifier costs every future reader the same confusion, repeatedly — fixing the name once removes that tax for good. A naming fix is often the trigger for an entire refactor, because a name that's wrong for the current shape of the code cascades into every call site that reads it.
- **Smell trigger:** Any identifier — variable, function, type, field, package — whose name no longer describes what it holds or does.
- **Go mechanics:**
  - gopls Rename is workspace-wide: it updates every reference across every file and package that imports the renamed symbol, and it type-checks the result.
  - It refuses rather than proceed when the rename would introduce a shadowing conflict, when renaming a method would break an interface satisfaction relationship elsewhere in the workspace, or when the surrounding code doesn't currently type-check.
  - Two special cases are easy to get backwards: renaming the `p` in `package p` moves the entire package directory and rewrites every import path that referred to it; renaming a method's _receiver declaration_ (the `s` in `func (s *Store) Get(...)`) propagates to every method of that type, while renaming a single _use_ of a receiver variable inside one method body touches only that method.
- **Tool:**

```
gopls rename file.go:#offset newName
```

Editor-integrated as "Rename Symbol" (F2 in most gopls-backed editors).

- **Risk:** Low — but treat any refusal as a real semantic hazard to investigate, not friction to route around by hand-editing instead.

→ See `samber/cc-skills-golang@golang-naming` skill for what to rename identifiers _to_. This entry covers only _how_ to apply the rename safely at scale.

## Change Function Declaration (Signature)

- **Motivation:** A parameter list that has grown past what the function actually needs, or that no longer matches how the function is used, makes every call site harder to read and easier to call wrong.
- **Smell trigger:** Long Parameter List, or a single parameter that has stopped being relevant to the function's job.
- **Go mechanics:**
  - gopls has partial, single-purpose support: removing a parameter nobody passes meaningfully, or reordering two adjacent parameters, are each mechanical.
  - Adding a new parameter across every call site, or a broader signature rewrite, is not a single gopls action today. For that case, use an `eg`-staged migration: write a new function variant with the added or generalized parameter, migrate call sites to the new form via an `eg` template (`eg -t template.go -w ./...`), verify, then Rename the old function out of the way (or delete it) once nothing calls it anymore.
  - This keeps the migration mechanical and reviewable instead of a set of manual edits scattered across the tree.
- **Tool:**

```
gopls codeaction -exec -kind=refactor.rewrite.removeUnusedParam file.go:#offset
gopls codeaction -exec -kind=refactor.rewrite.moveParamLeft      file.go:#offset
gopls codeaction -exec -kind=refactor.rewrite.moveParamRight     file.go:#offset
eg -t template.go -w ./...   # staged migration for adding/generalizing a parameter
```

- **Risk:** Medium for a single-parameter add/remove with a handful of call sites; High when the signature changes across many callers with no mechanical one-shot action available.

→ See `samber/cc-skills-golang@golang-design-patterns` skill for converting a long parameter list into an options struct rather than just reordering or trimming it.

## Move Function / Move Field / Move Type

- **Motivation:** A function, field, or type placed in the wrong package is a standing invitation to reach across a boundary that shouldn't be crossed — moving it to where its data lives removes that temptation.
- **Smell trigger:** Feature Envy — a function reads and manipulates another package's data more than its own — or a type whose responsibilities clearly belong to a different package than the one it currently lives in.
- **Go mechanics:**
  - No one-shot gopls action moves a symbol across package boundaries yet.
  - The gradual-repair sequence: introduce the symbol in its new home; leave a **type alias** (`type Old = pkg.New`) for a moved type, or a thin wrapper function/forwarding variable for a moved function, in the old location so both the old and new names keep working; migrate callers to the new name incrementally, one small commit at a time; delete the old name (and the alias/wrapper) only once nothing references it.
  - Splitting a large file into a new file _within the same package_ is a distinct, one-shot gopls action.
- **Tool:**

```
gopls codeaction -exec -kind=refactor.extract.toNewFile file.go:#start,#end   # same-package file split
```

Cross-package moves are the manual type-alias/wrapper sequence above — there is no equivalent one-shot command.

- **Risk:** High.

→ See `samber/cc-skills-golang@golang-project-layout` skill for target package layout. See [structural.md](structural.md) for the full type-alias gradual-repair recipe.

## Split Package / Merge Package

- **Motivation:** A package that has grown to serve many unrelated responsibilities is hard to review, test, and reason about as a unit — splitting it along its natural seams restores each piece's ability to be understood on its own. The reverse move, merging, is occasionally right when two packages have become so mutually dependent that the boundary between them adds ceremony without adding isolation.
- **Smell trigger:** A "god package" (the package-level analogue of a Large Class), or Divergent Change — the same package keeps changing for several unrelated reasons because it hosts several unrelated concerns.
- **Go mechanics:**
  - gopls exposes an experimental code action that partitions a package's top-level declarations into groups with no cyclic dependency between them, proposing a split into acyclic components. Treat its proposal as a starting point to review, not a final answer — package boundaries also encode API and ownership decisions the tool can't see.
  - Merging has no dedicated tool: move the declarations into the target package and resolve whatever import cycle results with a consumer-side interface (see [structural.md](structural.md)) before falling back to a bigger restructuring.
- **Tool:**

```
gopls codeaction -exec -kind=source.splitPackage file.go   # experimental; splitting only
```

- **Risk:** High.

→ See `samber/cc-skills-golang@golang-project-layout` skill for target package layout.

## Replace Nested Conditional with Guard Clauses

- **Motivation:** Deep `if`/`else` nesting forces a reader to hold every outer condition in mind to understand an inner branch; guard clauses let each precondition exit on its own line and leave only the main path in the body.
- **Smell trigger:** An `if`/`else if`/`else` chain, or nested `if` blocks, where most branches are actually preconditions or error cases rather than alternatives of equal weight.
- **Go mechanics:** Each branch that isn't the primary path becomes an early `return`/`continue`/`break`, flattening the remaining logic to a single nesting level. gopls's invert-if action flips a single `if`/`else` in place and is a useful mechanical building block for this, but it operates on one condition at a time — turning a whole nested chain into guard clauses is a structural pass with the assistance of that action, not a single tool invocation.
- **Tool:**

```
gopls codeaction -exec -kind=refactor.rewrite.invertIf file.go:#offset
```

- **Risk:** Low.

→ See `samber/cc-skills-golang@golang-code-style` skill for the full early-return style rule this refactor works toward.

## Introduce Parameter Object

- **Motivation:** When the same group of parameters keeps showing up together across several functions, the group itself is a concept that deserves a name and a single place to add validation or a new field.
- **Smell trigger:** Data Clumps — the same cluster of parameters (or fields) recurring together — or a Long Parameter List where several parameters are conceptually one unit.
- **Go mechanics:** Define a struct that holds the recurring parameter group, then change each affected function's signature to take the struct instead of the individual values. gopls has a planned "Extract parameter struct" action tracked as golang/go#65552; as of this writing it is not yet generally available. Until it lands, treat this as an Extract-Variable-style manual step (define the struct, construct it at each call site) followed by a signature change at each call site — the same staged approach as Change Function Declaration above.
- **Tool:** No dedicated gopls action yet (golang/go#65552 tracks it). Combine manual struct extraction with the signature-change tooling above.
- **Risk:** Medium.

→ See `samber/cc-skills-golang@golang-design-patterns` skill for functional options as the alternative when the struct exists to configure construction rather than to group a plain data clump.

## Replace Conditional with Polymorphism

- **Motivation:** A `switch` on a type or state constant that shows up in more than one place forces every new case to be added in lock-step at every one of those places; an interface with one implementation per case collects each case's behavior in one place instead.
- **Smell trigger:** Repeated Switches — the same `switch` on a type tag or state value recurs at multiple call sites, and adding a new case means finding and updating every one of them.
- **Go mechanics:** Define an interface with one method per behavior that currently varies by case, then give each case its own implementing type. Callers that used to switch on the tag now just call the interface method, and dispatch happens through Go's interface mechanism instead of a repeated `switch`.
- **Tool:** Manual — no mechanical tool performs this transform; use Extract Function/Interface steps to carve out each case's behavior into its own type, then Rename/Inline to clean up the seams.
- **Risk:** Medium.

→ See `samber/cc-skills-golang@golang-design-patterns` skill for the target interface-dispatch pattern.

## Hide Delegate / Remove Middle Man

- **Motivation:** A caller that reaches through one object to call methods on another is coupled to both the shape of the first object _and_ the shape of everything downstream of it; hiding the delegate collapses that chain to a single call. The opposite failure — a method that does nothing but forward to another object — adds a hop with no behavior to show for it, and removing it lets callers reach the real implementation directly.
- **Smell trigger:** Message Chains (`a.B().C().D()` reaching through several objects to get to the one that matters) call for Hide Delegate; a Middle Man (a method whose entire body is `return x.SameMethod(...)`) calls for Remove Middle Man.
- **Go mechanics:** Struct embedding is Go's usual mechanism for Hide Delegate — embedding the delegate promotes its methods onto the containing type, so callers invoke them directly on the outer struct instead of chaining through an accessor. Remove Middle Man is the inverse: delete the pass-through method (after an Inline Call at each of its call sites, or a Rename-and-redirect) and let callers reach the real implementation directly, whether through an exported field or the embedded type.
- **Tool:** Manual for the embedding decision; `gopls codeaction -exec -kind=refactor.inline.call` mechanizes the "delete the middle man" step once callers are ready to call through directly.
- **Risk:** Low-Medium.

## Sprout Method / Wrap Method

- **Motivation:** Feathers's core insight: code with no tests is code you can't safely edit in place, because there's no way to notice if you broke it. Both techniques add new behavior without touching the untested code directly, so the new behavior can be tested even when the old code still can't be.
- **Smell trigger:** A need to add new behavior to a function or method that currently has little or no test coverage.
- **Go mechanics:**
  - **Sprout Method** — write the new behavior as a brand-new, fully-tested function or method, and call it from the one call site that needs it, leaving the original code otherwise untouched.
  - **Wrap Method** — rename the original method (e.g. `Save` → `saveInternal`), then add a new method with the old name (`Save`) that calls the renamed original and adds the new behavior around it; this is a manual decorator, since Go has no built-in method-wrapping mechanism.
- **Tool:** `gopls rename` for the rename step in Wrap Method; the new code itself is hand-written and tested like any other new function.
- **Risk:** Low — by design, this is how Feathers's approach avoids touching untested code directly.

→ See [safety-net.md](safety-net.md) for when low/zero coverage should push you toward this pattern instead of editing in place.

## Replace Temp with Query

- **Motivation:** A local variable computed once and reused several times hides the fact that it's a derived value — reading the variable's name doesn't tell you it's a computation, only that it's a value, which obscures where the real logic lives.
- **Smell trigger:** A local variable assigned once from an expression and then read multiple times later in the function, where the variable's name doesn't make clear it's derived rather than an input.
- **Go mechanics:** Replace the variable with a call to a small unexported function or method that recomputes the same expression, then remove the variable and each of its reads becomes a call instead. This is a manual step — Go's function-call cost is cheap enough that the transform is rarely a performance concern, so the only judgment call is readability, not cost.
- **Tool:** Manual. If the resulting function is only ever called once, gopls's inline action can fold it back at any point without losing the readability gain that motivated extracting it.
- **Risk:** Low.

## Smell → Refactoring Quick Reference

| Smell | Go-specific fix |
| --- | --- |
| Long Function | Extract Function/Method |
| Large/God Package | Split Package |
| Long Parameter List | Introduce Parameter Object, or an options struct |
| Data Clumps | Extract a struct for the recurring group |
| Primitive Obsession | Introduce a named type instead of a bare `string`/`int` |
| Divergent Change (one package, many unrelated reasons to change) | Split Package |
| Shotgun Surgery (one conceptual change touches many packages) | Move Function/Field to consolidate the concept into one package |
| Feature Envy | Move Function to the package whose data it actually uses |
| Repeated Switches | Replace Conditional with Polymorphism |
| Message Chains | Hide Delegate |
| Middle Man | Remove Middle Man |

Divergent Change and Shotgun Surgery point to opposite fixes even though both are "too much change ripples around": Divergent Change is one package changing for many reasons — the fix is to split it apart. Shotgun Surgery is one reason to change rippling across many packages — the fix is to consolidate that concept into one package so a single change touches one place.

## Cross-References

- → See [structural.md](structural.md) for the full type-alias gradual-repair recipe used by Move Function/Field/Type, and for breaking import cycles ahead of a package split or merge.
- → See [safety-net.md](safety-net.md) for the coverage-adaptive strategy that determines when Sprout/Wrap Method should replace an in-place edit.
- → See [go-tooling.md](go-tooling.md) for the full gopls code-action reference, `gofmt -r`, `eg`, and `gopatch` invocation details.
- → See `samber/cc-skills-golang@golang-naming` skill for what to rename identifiers _to_.
- → See `samber/cc-skills-golang@golang-project-layout` skill for target package/directory layout.
- → See `samber/cc-skills-golang@golang-design-patterns` skill for options structs, consumer-side interfaces, and interface-dispatch patterns referenced throughout this catalog.
- → See `samber/cc-skills-golang@golang-code-style` skill for the guard-clause/early-return style rule.
