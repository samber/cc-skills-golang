# `gopls` CLI reference

The Go team documents this interface as experimental — "not efficient, complete, flexible, or officially supported." Treat it as a debugging and one-shot-scripting fallback, not the primary way to drive `gopls`; prefer the MCP tools or the native `LSP` tool when either is available (see [mcp.md](mcp.md)).

## Table of contents

- [Position syntax](#position-syntax)
- [Global flags](#global-flags)
- [Navigation commands](#navigation-commands)
- [Diagnostics](#diagnostics)
- [Transformation commands](#transformation-commands)
- [Code actions and code lenses](#code-actions-and-code-lenses)
- [Introspection](#introspection)
- [Server modes](#server-modes)
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

| Flag | Purpose |
| --- | --- |
| `-listen=<addr>` | Run gopls as a long-lived server instead of a one-shot command |
| `-mcp.listen=<addr>` | Expose an MCP server alongside the LSP server (attached mode) |
| `-logfile=<path>` | Log to a file instead of stderr; `auto` picks a default path |
| `-remote=<addr>` | Forward commands to an already-running gopls daemon |
| `-rpc.trace` | Print the full RPC trace, LSP-inspector format |
| `-v`, `-vv` | Verbose / very verbose output |
| `-profile.cpu`, `-profile.mem`, `-profile.alloc`, `-profile.block`, `-profile.trace` | Write the respective pprof/trace profile to a file |

## Navigation commands

| Command | Example | Notes |
| --- | --- | --- |
| `definition` | `gopls definition helper/helper.go:8:6` | `-json`, `-markdown` flags for structured/rendered output |
| `references` | `gopls references helper/helper.go:8:6` | `-d`/`-declaration` includes the declaration itself in results |
| `implementation` | `gopls implementation helper/helper.go:8:6` | No flags |
| `call_hierarchy` | `gopls call_hierarchy helper/helper.go:8:6` | Static calls only |
| `symbols` | `gopls symbols helper/helper.go` | File-scoped outline |
| `workspace_symbol` | `gopls workspace_symbol -matcher fuzzy 'wsymbols'` | `-matcher fuzzy\|fastfuzzy\|casesensitive\|caseinsensitive` (default caseinsensitive) |
| `signature` | `gopls signature helper/helper.go:8:6` | Function signature at position |
| `highlight` | `gopls highlight helper/helper.go:8:6` | Same-symbol identifier highlights |
| `folding_ranges` | `gopls folding_ranges helper/helper.go` | Collapsible regions |
| `links` | `gopls links internal/cmd/check.go` | `-json` for structured output |
| `prepare_rename` | `gopls prepare_rename helper/helper.go:8:6` | Validates a rename is possible at this position before attempting it |
| `semtok` | `gopls semtok internal/cmd/semtok.go` | Semantic token dump |

## Diagnostics

```bash
gopls check internal/cmd/check.go
gopls check -severity=error internal/cmd/check.go   # hint|info|warning|error, default warning
```

## Transformation commands

All write-capable commands share these flags: `-w`/`-write` (write edits to disk), `-d`/`-diff` (print a diff instead), `-l`/`-list` (print only the names of edited files), `-preserve` (with `-write`, keep a copy of the original).

| Command | Example | Notes |
| --- | --- | --- |
| `format` | `gopls format -w internal/cmd/check.go` | Canonical `gofmt`-equivalent; ignores client formatting options |
| `imports` | `gopls imports -w internal/cmd/check.go` | Adds/removes/sorts imports |
| `rename` | `gopls rename helper/helper.go:8:6 Foo` | Positional args: `<position> <new-name>` |

## Code actions and code lenses

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

`codeaction` flags: `-kind` (comma-separated list of kinds — see below), `-title` (regex filter on the action's title), `-exec` (run the first match instead of only listing). Only one action can be executed per invocation — there is no conflict resolution for applying more than one. `-kind=refactor` matches every kind nested under it (kinds are hierarchical).

Note: actions of kind `source.test` are not returned unless explicitly requested via `-kind`.

## Introspection

```bash
gopls stats            # JSON summary of workspace info relevant to performance; populates the file cache as a side effect
gopls stats -anon      # same, with fields that could leak user/file names or source redacted
gopls version          # print gopls version info
gopls api-json         # print gopls' full API surface as JSON
gopls bug              # report a bug in gopls
gopls licenses         # print licenses of bundled software
```

## Server modes

```bash
gopls serve                              # default when no command given — LSP server over stdio
gopls serve -mcp.listen=localhost:8092   # LSP server + attached MCP server (SSE/HTTP), shares memory with the LSP session
gopls mcp                                # standalone, detached MCP server over stdio — no LSP client needed
gopls mcp -listen=localhost:3000         # standalone MCP server over SSE/HTTP
gopls mcp -instructions                  # print gopls' MCP model instructions and exit
```

See [mcp.md](mcp.md) for the full breakdown of attached vs. detached mode and every MCP tool.

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
