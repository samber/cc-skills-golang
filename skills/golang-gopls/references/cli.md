# `gopls` CLI reference

The Go team documents this interface as experimental — "not efficient, complete, flexible, or officially supported." Treat it as a debugging and one-shot-scripting fallback, not the primary way to drive `gopls`; prefer the MCP tools or the native `LSP` tool when either is available (see [mcp.md](mcp.md)).

## Table of contents

- [Position syntax](#position-syntax)
- [Global flags](#global-flags)
- [Shared write flags](#shared-write-flags)
- [Navigation commands](#navigation-commands)
- [Diagnostics](#diagnostics)
- [Transformation commands](#transformation-commands)
- [Code actions and code lenses](#code-actions-and-code-lenses)
- [Introspection](#introspection)
- [CodeAction kind reference](#codeaction-kind-reference)

## Position syntax

Two interchangeable formats locate a point in a file:

- `file.go:line:column` — both 1-indexed; columns count UTF-8 bytes, not runes or UTF-16 code units. Non-ASCII lines can disagree with what an editor reports if the editor counts differently.
- `file.go:#1234` — a 0-indexed byte offset from the start of the file.

```bash
gopls definition internal/cmd/definition.go:44:47
gopls definition internal/cmd/definition.go:#1270
```

## Global flags

Flags accepted by `gopls` itself, before the subcommand:

| Flag | Value | Purpose |
| --- | --- | --- |
| `-logfile=<path>` | a file path, or the literal string `auto` | Log destination; `auto` picks a default output file instead of stderr |
| `-profile.cpu=<path>` | a file path | Write a CPU profile to this file |
| `-profile.mem=<path>` | a file path | Write a memory profile to this file |
| `-profile.alloc=<path>` | a file path | Write an allocation profile to this file |
| `-profile.block=<path>` | a file path | Write a blocking-profile to this file |
| `-profile.trace=<path>` | a file path | Write an execution trace to this file |
| `-v`, `-verbose` | boolean flag, no value | Verbose output |
| `-vv`, `-veryverbose` | boolean flag, no value | Very verbose output |

`gopls mcp` accepts its own, narrower flag set: `-listen=<addr>` (run over SSE/HTTP instead of stdio), `-logfile=<path>` (defaults to stderr), and `-rpc.trace` (cannot be combined with `-listen`).

## Shared write flags

Every command that can modify source (`format`, `imports`, `rename`, `codeaction`, `codelens`, `execute`) accepts this same set — each is a boolean flag, no value:

| Flag | Purpose |
| --- | --- |
| `-w`, `-write` | Write the edited content back to the source file(s) |
| `-d`, `-diff` | Print a unified diff instead of writing |
| `-l`, `-list` | Print only the names of the files that would be/were edited |
| `-preserve` | Combined with `-w`: keep a copy of each original file before overwriting |

None of these are mutually exclusive with each other; passing none of them just computes the edit without printing or writing it.

## Navigation commands

| Command | Flags | Example | Notes |
| --- | --- | --- | --- |
| `definition` | `-json` (boolean), `-markdown` (boolean) | `gopls definition helper/helper.go:8:6` | `-json` for structured output, `-markdown` to render doc comments as Markdown |
| `references` | `-d`, `-declaration` (boolean) | `gopls references helper/helper.go:8:6` | Includes the declaration itself in the results when set |
| `implementation` | none | `gopls implementation helper/helper.go:8:6` | — |
| `call_hierarchy` | none | `gopls call_hierarchy helper/helper.go:8:6` | Static calls only |
| `symbols` | none | `gopls symbols helper/helper.go` | File-scoped outline |
| `workspace_symbol` | `-matcher=<value>` — one of `fuzzy`, `fastfuzzy`, `casesensitive`, `caseinsensitive` (default `caseinsensitive`) | `gopls workspace_symbol -matcher fuzzy 'wsymbols'` | Matching algorithm for the query |
| `signature` | none | `gopls signature helper/helper.go:8:6` | Function signature at position |
| `highlight` | none | `gopls highlight helper/helper.go:8:6` | Same-symbol identifier highlights |
| `folding_ranges` | none | `gopls folding_ranges helper/helper.go` | Collapsible regions |
| `links` | `-json` (boolean) | `gopls links internal/cmd/check.go` | Structured output when set |
| `prepare_rename` | none | `gopls prepare_rename helper/helper.go:8:6` | Validates a rename is possible at this position before attempting it |
| `semtok` | none | `gopls semtok internal/cmd/semtok.go` | Semantic token dump |

## Diagnostics

| Command | Flags | Example |
| --- | --- | --- |
| `check` | `-severity=<value>` — one of `hint`, `info`, `warning`, `error` (default `warning`); reports diagnostics at or above this severity | `gopls check -severity=error internal/cmd/check.go` |

## Transformation commands

All of these additionally accept the [shared write flags](#shared-write-flags) above.

| Command | Positional args | Example | Notes |
| --- | --- | --- | --- |
| `format` | one or more `<filerange>` (a file, or a range within one) | `gopls format -w internal/cmd/check.go` | Canonical `gofmt`-equivalent; ignores client formatting options |
| `imports` | `<filename>` | `gopls imports -w internal/cmd/check.go` | Adds/removes/sorts imports |
| `rename` | `<position> <new-name>` | `gopls rename helper/helper.go:8:6 Foo` | `<new-name>` is a plain identifier — validate first with `prepare_rename` if unsure |

## Code actions and code lenses

`codeaction` and `codelens` additionally accept the [shared write flags](#shared-write-flags).

| Command | Extra flags | Notes |
| --- | --- | --- |
| `codeaction` | `-kind=<value>` — comma-separated list of kinds, see [CodeAction kind reference](#codeaction-kind-reference) below; `-title=<regex>` — filter actions by title; `-exec` (boolean) — execute the first match instead of only listing | `-kind=refactor` matches every kind nested under it (kinds are hierarchical); only one action executes per invocation — there is no conflict resolution for applying more than one; actions of kind `source.test` are excluded unless explicitly requested via `-kind` |
| `codelens` | `-exec` (boolean) — run the first matching lens instead of only listing | Takes `<file>`, `<file:line>`, or `<file> <title>` as positional args |
| `execute` | none beyond the shared write flags | Takes `<command> <json-argument>` — sends a raw LSP `ExecuteCommand` request; gopls's command set (`command.Interface`) is unstable and may change between versions |

```bash
# List available code actions for a range
gopls codeaction -kind=quickfix ./gopls/main.go

# Execute the first matching action and show a diff
gopls codeaction -kind=quickfix -exec -diff ./gopls/main.go

# Filter by title (regex) in addition to kind
gopls codeaction -kind=refactor.rewrite -title 'Fill struct' -exec -w file.go:12:3

# Code lenses: list, or run a specific one
gopls codelens a_test.go                     # list lenses in a file
gopls codelens a_test.go:10                  # list lenses on line 10
gopls codelens a_test.go "run test"          # list gopls.run_tests commands
gopls codelens -exec a_test.go:10 "run test" # run a specific test

# Execute a raw LSP ExecuteCommand
gopls execute gopls.add_import '{"ImportPath": "fmt", "URI": "file:///hello.go"}'
gopls execute gopls.run_tests '{"URI": "file:///a_test.go", "Tests": ["Test"]}'
gopls execute gopls.list_known_packages '{"URI": "file:///hello.go"}'
```

## Introspection

| Command | Flags | Notes |
| --- | --- | --- |
| `stats` | `-anon` (boolean) | JSON summary of workspace info relevant to performance; populates the file cache as a side effect. `-anon` redacts fields that could leak user/file names or source text |
| `version` | none | Print gopls version info |
| `api-json` | none | Print gopls' full API surface as JSON |
| `bug` | none | Report a bug in gopls |
| `licenses` | none | Print licenses of bundled software |

```bash
gopls stats
gopls stats -anon
gopls version
gopls api-json
gopls bug
gopls licenses
```

## CodeAction kind reference

Passed to `-kind` on `codeaction` (comma-separated, hierarchical — `refactor` matches all `refactor.*`):

```
gopls.doc.features
quickfix
refactor
refactor.extract
refactor.extract.constant
refactor.extract.function
refactor.extract.method
refactor.extract.toNewFile
refactor.extract.variable
refactor.inline
refactor.inline.call
refactor.rewrite
refactor.rewrite.changeQuote
refactor.rewrite.fillStruct
refactor.rewrite.fillSwitch
refactor.rewrite.invertIf
refactor.rewrite.joinLines
refactor.rewrite.removeUnusedParam
refactor.rewrite.splitLines
source
source.assembly
source.doc
source.fixAll
source.freesymbols
source.organizeImports
source.test
```

A few additional kinds exist beyond this `-kind`-documented set but are reachable only through editor UI or `execute`/code lens, not by name filter: `refactor.extract.variable-all`, `refactor.extract.constant-all`, `refactor.inline.variable`, `refactor.rewrite.moveParamLeft`, `refactor.rewrite.moveParamRight`, `refactor.rewrite.eliminateDotImport`, `refactor.rewrite.addTags`, `refactor.rewrite.removeTags`, `refactor.rewrite.implementInterface`, `source.addTest`, `source.splitPackage`, `source.toggleCompilerOptDetails`. See [features.md](features.md#transformation) for what each one does.
