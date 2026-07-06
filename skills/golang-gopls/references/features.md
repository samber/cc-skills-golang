# gopls feature catalog

Source: [tip.golang.org/gopls/features](https://tip.golang.org/gopls/features/). Each entry names the LSP request or `CodeAction` kind so a specific behavior can be looked up in the upstream docs by exact term.

## Table of contents

- [Navigation](#navigation)
- [Passive (always-on)](#passive-always-on)
- [Diagnostics](#diagnostics)
- [Transformation](#transformation)
- [Web-based features](#web-based-features)
- [Non-Go files](#non-go-files)
- [Completion](#completion)

## Navigation

**Definition** (`textDocument/definition`, CLI `gopls definition`) — jumps to a symbol's declaration. Handles more than plain identifiers: on an import path it lists the imported package's declarations; on a `go:linkname` directive it finds the linked symbol; on a `go:embed` pattern it finds the embedded file; on a doc-comment link it follows the reference; on a non-Go function it can return the assembly implementation; on `return` it locates the named result variables; on `goto`/`break`/`continue` it finds the target label or block. Already at the declaration → most clients reinterpret the request as "find references" instead.

**Type Definition** (`textDocument/typeDefinition`, no CLI equivalent) — jumps to the _named type_ underlying a symbol, unwrapping pointer, array, slice, channel, and map constructors first. For `x chan []*T`, this reports the definition of `T`. Only works on symbols, not arbitrary expressions. No agent-invocable path: it is absent from the native `LSP` tool's fixed operation list (`goToDefinition`, `findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`, `goToImplementation`, call hierarchy), so only a full editor LSP client can reach it.

**References** (`textDocument/references`, CLI `gopls references`) — lists every use of a symbol. For an interface method, this includes concrete implementations; for a package declaration, it includes both direct imports and other files' package clauses; for an embedded field, it reports only field references (use Type Definition to find references to the type itself). **Scoping gotcha:** results reflect only the build configuration of the queried file — a query issued against `foo_windows.go` will not surface a match in `bar_linux.go`. Built-in symbols (`int`, `append`) are rejected as too numerous to be useful.

**Implementation** (`textDocument/implementation`, CLI `gopls implementation`) — on an interface, returns concrete implementations and sub-interfaces; on a concrete type, returns interfaces it satisfies; on an interface method, returns the concrete methods satisfying it, and vice versa. Matching uses method sets for types and signatures for functions. Generic types are treated as wildcards: a candidate is included if _any_ instantiation would allow one to implement the other, without full unification checking. LSP's built-in bias toward subtypes makes this query directionally asymmetric — for full bidirectional traversal, use Type Hierarchy instead.

**Document Symbol** (`textDocument/documentSymbol`, CLI `gopls symbols`) — outline of a single file's top-level declarations. File-scoped; use Symbol for cross-file search.

**Symbol / Workspace Symbol** (`workspace/symbol`, CLI `gopls workspace_symbol`) — fuzzy search across the whole workspace. Default matcher is `fastFuzzy` (FZF-inspired), so abbreviations and typos still match — `DocSym` matches `DocumentSymbol`. Controlled by the `symbolMatcher`, `symbolStyle`, and `symbolScope` settings (see [settings.md](settings.md)); `directoryFilters` excludes directories from the search.

**Selection Range** (`textDocument/selectionRange`, no CLI equivalent) — expands or contracts the current selection along syntactic boundaries (expression → statement → block → function). Useful for selecting exactly the region an Extract refactor needs.

**Call Hierarchy** (`textDocument/prepareCallHierarchy` + `callHierarchyItem/incomingCalls`/`outgoingCalls`, CLI `gopls call_hierarchy`) — shows a function's callers and callees as a static graph. **Only static calls are included** — calls made through a function value or an interface method are invisible, since detecting them isn't analytically tractable. Corroborate with References when a dynamically-dispatched call site matters. Invoke on the function declaration's name.

**Type Hierarchy** (`textDocument/prepareTypeHierarchy` + `typeHierarchyItem/subtypes`/`typeHierarchy/supertypes`, no CLI equivalent yet) — bidirectional view of the subtyping relation: which types implement an interface, and which interfaces a type satisfies. Resolves the asymmetry Implementation has. Limited to **named types** (unlike Implementation, which also matches unnamed function types); alias types are excluded; function-local types are visible only within the same package.

## Passive (always-on)

These need no explicit invocation — they fire continuously as an editor session progresses. Most degrade if the surrounding package has build errors, since they depend on successful type-checking.

**Hover** (`textDocument/hover`) — symbol name/kind/type/value, doc comment (with clickable doc links like `[fmt.Printf]`), promoted methods from embedded fields, struct field size/offset and wasted-space percentage (flagged at ≥20% waste), expanded `//go:embed` patterns, `//go:linkname` targets, and which Go release introduced a given stdlib symbol. Controlled by `hoverKind` (verbosity) and `linkTarget` (base URI for doc links).

**Signature Help** (`textDocument/signatureHelp`) — parameter names/types/docs for the function being called, with the active parameter highlighted; works even while the cursor sits inside the function name, not just inside the parens.

**Document Highlight** (`textDocument/documentHighlight`) — highlights every identifier referring to the same symbol in view, plus related tokens: named results and their return statements, loop control keywords (`for`/`break`/`continue`), switch tokens, a function and its own return statements. Read vs. write references are typically color-coded differently by the client.

**Inlay Hint** (`textDocument/inlayHint`) — inline annotations, off by default (visual clutter), toggled per-kind via the `hints` setting: `parameterNames` (call-site argument labels), `assignVariableTypes`, `compositeLiteralFields`, `compositeLiteralTypes`, `constantValues` (including computed `iota` values), `functionTypeParameters` (generic instantiations), `rangeVariableTypes`.

**Semantic Tokens** (`textDocument/semanticTokens`) — richer syntax coloring than naive lexing: token types (`function`, `keyword`, `macro`, `method`, `namespace`, `number`, `operator`, `parameter`, `string`, `type`, `typeParameter`, `variable`, …) plus modifiers including a custom `shadowing` modifier that flags shadowed declarations. Off by default due to type-checking latency (`semanticTokens` setting); `noSemanticString`/`noSemanticNumber` let a client opt out of just those two kinds if it prefers its own lexical highlighting for them.

**Folding Range** (`textDocument/foldingRange`) — collapsible regions for large comments, functions, and blocks.

**Document Link** (`textDocument/documentLink`) — turns URLs in doc comments and import declarations into clickable links (imports link to their pkg.go.dev page). Controlled by `importShortcut` and `linkTarget`.

## Diagnostics

Three sources, distinguished by the LSP diagnostic's `source` field:

1. **Compilation errors** — gopls doesn't invoke the real compiler; it runs `go list` for package metadata (`source: "go list"`) then mimics the compiler front-end itself: read, scan, parse, type-check (`source: "compiler"`).
2. **Analysis findings** — the `go vet` analysis framework plus gopls's own analyzers, each reporting under its own analyzer name as `source`. The `printf` analyzer (format-string/argument mismatches) is a representative example.
3. **Compiler optimization details** — off by default; toggled per-package with the `source.toggleCompilerOptDetails` code action. Surfaces escape-analysis results, nil-check elimination, and inlining decisions. Only available on packages that are otherwise error-free.

**Recomputation timing:** open-file compile errors update within tens of milliseconds of a keystroke. Workspace-wide analysis diagnostics recompute after roughly a second of idle time, tunable via `diagnosticsDelay`; `diagnosticsTrigger` can switch this to save-triggered instead of edit-triggered. Clients can also request diagnostics explicitly (`textDocument/diagnostic`, "pull diagnostics") if initialized with `pullDiagnostics: true` — off by default for performance.

**Notable quick fixes**, offered as code actions attached to a diagnostic:

- `fillreturns` — heuristically completes an incomplete `return` statement.
- `stubMissingInterfaceMethods` — generates stub methods when a concrete type doesn't yet satisfy a required interface.
- `StubMissingCalledFunction` — creates a stub for an undefined function/method, inferring its signature from the call site.
- `CreateUndeclared` — declares a missing variable or function based on how it's used.
- Fixes marked `source.fixAll` are considered unconditionally safe; most editors offer a single shortcut to apply all of them at once.

CLI: `gopls check <file>` (`-severity=hint|info|warning|error`, default `warning`).

## Transformation

Three underlying mechanisms: **Formatting** and **Rename** are primary LSP requests; most everything else is a **CodeAction** (requested per-range, returns either a direct edit or a lazily-computed command); a handful of dependency-management actions are **CodeLenses** instead.

**Formatting** (`textDocument/formatting`, CLI `gopls format`) — canonical Go formatting; client-supplied formatting options are ignored. `gofumpt: true` switches to `mvdan.cc/gofumpt`'s stricter rules.

**Organize Imports** (`source.organizeImports`, CLI `gopls imports`) — removes unused/duplicate imports, adds missing ones (via workspace-wide heuristics — occasionally surprising), sorts them. The `local` setting groups a path prefix as "local," matching `goimports -local`. Most editors run this on save; disable per-language if that's unwanted.

**Rename** (`textDocument/rename`, CLI `gopls rename`) — two-stage: `prepareRename` reports the current name, then `rename` applies the change everywhere. Refuses renames that would introduce shadowing or break interface satisfaction. Special positions unlock extra behavior:

- Rename a **method's receiver declaration** → renames the receiver identifier across every method of that type; rename a receiver **use** → renames only that one variable.
- Rename the **package name in a `package` clause** → moves every file in the package to a new directory (subpackages stay put unless `renameMovesSubpackages` is set); refused across module boundaries or into an existing package.
- Rename the **`func` keyword** of a declaration → lets you edit the whole signature; parameter/result count and types must stay the same (no adding/removing parameters this way — see `refactor.rewrite.removeUnusedParam`/`moveParamLeft`/`moveParamRight` for that).

**Extract** (`refactor.extract.*`) — replaces a selection with a reference to a new declaration:

- `refactor.extract.variable` / `.constant` — one new local binding for the selected expression, plus `-all` variants that rewrite every occurrence within the enclosing function.
- `refactor.extract.function` / `.method` — turns one or more complete statements into a call to a new function (or method, on the same receiver, if extracted inside a method).
- `refactor.extract.toNewFile` (gopls ≥ v0.17.0) — moves selected top-level declarations into a new file, adding imports as needed; the new filename derives from the first declared symbol.

Extract is less rigorous than Rename/Inline: comments are sometimes dropped, and files carrying a `DO NOT EDIT` generated-code marker receive no code actions at all.

**Inline** (`refactor.inline.*`):

- `refactor.inline.call` — replaces a call with the function body, substituting parameters for arguments. Works only for static calls to accessible functions/methods (not through a function value or interface method, not to unexported names outside the package, not into `internal` packages, not for generic functions). Preserves side-effect ordering (introduces `var`s when an argument must not be duplicated or reordered), keeps qualified references correct (`Printf` → `fmt.Printf` with the import added), keeps implicit conversions explicit, and never drops a variable's last use. `defer` bodies stay wrapped in a closure since defer semantics are tied to function boundaries.
- `refactor.inline.variable` — replaces a local variable's use with its initializer expression; refuses if an identifier in that initializer has been shadowed since the declaration.

**Miscellaneous rewrites** (`refactor.rewrite.*`):

- `removeUnusedParam` — the `unusedparams` analyzer offers renaming to `_` (trivial) or a full signature change that also updates every caller, preserving side-effecting arguments.
- `moveParamLeft` / `moveParamRight` — reorders one parameter, updating every call site.
- `changeQuote` — toggles a string literal between raw (`` `...` ``) and interpreted (`"..."`) form; idempotent to apply twice.
- `invertIf` — negates a plain `if`/`else` condition (no `else if` chain) and swaps the two blocks.
- `splitLines` / `joinLines` — expands or collapses a bracketed list (composite literal, call arguments, signature) one item per line; skipped for lists that already contain `//` comments or have fewer than two items.
- `fillStruct` — populates missing struct-literal fields, matching field names to in-scope variables/constants/functions where possible, zero value otherwise. Searches only the current file, above the cursor — run `source.organizeImports` first if the struct type was just introduced.
- `fillSwitch` — adds missing cases for an enum-like set of named constants, or for a type switch (one case per concrete type implementing the interface, plus a default that panics on an unexpected type).
- `eliminateDotImport` — removes a dot import and qualifies every reference, offered only when no name collision would result.
- `addTags` / `removeTags` — adds or removes struct field tags (e.g. `json`); interactive clients can choose the naming transform (`camelCase`, `snake_case`, `lisp-case`, `PascalCase`, `Title Case`).
- `implementInterface` — adds placeholder method declarations so a named type satisfies a chosen interface (defaults to `error`); interactive-dialog only, gopls-specific.

**Add Test For Function** (`source.addTest`) — generates a table-driven test for the selected function/method, creating the `_test.go` file if needed (copying copyright/build-constraint comments), using an external `p_test` package to encourage testing exported API only, naming results `got`/`got2`/…, comparing against `want`/`want2`/…, and adding a `wantErr bool` field when the final result is `error`. For a method, searches the package for a constructor (preferring `NewT` for type `T`). A leading `context.Context` parameter gets `t.Context()` on Go 1.24+, `context.Background()` otherwise.

## Web-based features

gopls runs a small localhost web server (LSP `window/showDocument`) for reports too rich for inline editor UI. Every endpoint URL embeds a random auth token; restarting gopls invalidates old links and shows a disconnected banner on any page still open.

- **Package Documentation** (`source.doc`) — a pkgsite-style rendered view of a package's docs, including **internal, unpublished packages** pkg.go.dev never sees. Symbol links jump the editor to the source declaration; reload without saving to see current edits reflected.
- **Free Symbols** (`source.freesymbols`) — lists the symbols a selection references but doesn't define itself, grouped as imported (with doc links), local, or package-level — the exact input list an Extract Function/Method refactor would need.
- **Assembly** (`source.assembly`) — the compiled assembly listing for a function, source-line-linked, recompiled on each reload. Architecture follows the file's build tags (e.g. `foo_amd64.go`). Not yet supported for generic functions, `func init`, or functions in test packages.
- **Split Package** (`source.splitPackage`) — an interactive dependency-graph tool for planning how to break a package into smaller, acyclic components. It visualizes the split but does not yet perform the actual code movement/renaming.

All of these send edits/navigation back to the editor via `showDocument`, which works even against modified-but-unsaved source.

## Non-Go files

**Templates** (`text/template`/`html/template`) — disabled until `templateExtensions` lists at least one extension (templates have no canonical extension of their own); the editor also needs to associate that extension with the `tmpl`/`gotmpl` language ID (e.g. VS Code's `files.associations`). Inside `{{ }}` delimiters: diagnostics (parse errors; missing functions are not flagged), full syntax highlighting, definitions and references (all templates share one global scope), and completions. Hover, semantic tokens, symbol search, and document highlight are not yet implemented. Custom delimiters other than `{{`/`}}` are not understood.

**go.mod / go.work** — hover, hints, vulncheck-driven diagnostics, and code lenses (add dependency, upgrade dependency, tidy, run `govulncheck`) are supported; the upstream page marks the fine-grained behavior of each as still under documentation, so verify current behavior directly against a `go.mod` file in an editor session rather than relying on an exhaustive list here.

**Assembly (`.s`) files** — basic support exists; treat as best-effort.

## Completion

Upstream documentation for this feature is a stub as of this writing (tracked as [golang/go#62022](https://github.com/golang/go/issues/62022)) — rely on empirical behavior plus these known settings rather than a documented spec: `usePlaceholders` (fills in placeholder parameter names on completion), `completeFunctionCalls` (adds trailing parentheses, on by default), `completeUnimported` and `matcher`/`deepCompletion`-style settings shape whether not-yet-imported packages and nested field/method completions are offered. See [settings.md](settings.md) for the full settings surface.
