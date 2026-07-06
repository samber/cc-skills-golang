# gopls settings reference

Source: [tip.golang.org/gopls/settings](https://tip.golang.org/gopls/settings). Settings are passed via the LSP client's `initializationOptions` (editor-specific config file/UI) — there is no `gopls.json` read from the workspace by default. Full canonical list: `gopls api-json`. Store the settings in CLAUDE.md.

## Table of contents

- [Build](#build)
- [Formatting](#formatting)
- [Diagnostics](#diagnostics)
- [Documentation](#documentation)
- [Inlay hints](#inlay-hints)
- [Navigation](#navigation)

## Build

| Setting | Type | Default | Purpose |
| --- | --- | --- | --- |
| `buildFlags` | `[]string` | `[]` | Extra flags for the build system, most commonly `-tags=<tag>` to bring build-tagged files into scope |
| `env` | `map[string]string` | `{}` | Environment variables for external commands gopls shells out to (`go list`, etc.) |
| `directoryFilters` | `[]string` | `["-**/node_modules"]` | Include/exclude workspace directories from loading and from workspace-symbol search, using `+`/`-` prefixed glob patterns |
| `expandWorkspaceToModule` | `bool` | `true` | Whether the enclosing module (not just the opened directory) counts as "workspace" for diagnostics scope |
| `templateExtensions` | `[]string` | `[]` | File extensions treated as Go template files (templates have no canonical extension, so this is empty by default) |

**When it matters:** a symbol behind a build tag (`//go:build integration`) is invisible to `references`/`go_search` until `buildFlags: ["-tags=integration"]` is set — this is the same root cause as the References build-configuration scoping gotcha in [features.md](features.md#navigation).

## Formatting

| Setting | Type | Default | Purpose |
| --- | --- | --- | --- |
| `local` | `string` | `""` | Import path prefix treated as "local" for import grouping/sort order — equivalent to `goimports -local` |
| `gofumpt` | `bool` | `false` | Format with `mvdan.cc/gofumpt`'s stricter ruleset instead of plain `gofmt` |

## Diagnostics

| Setting | Type | Default | Purpose |
| --- | --- | --- | --- |
| `analyses` | `map[string]bool` | `{}` | Enable/disable individual analyzers by name (the `go vet`-based framework plus gopls's own) |
| `staticcheck` | `bool` | `false` | Enable the staticcheck.io analyzer suite in addition to the built-in analyzers |
| `vulncheck` | enum: `Off`\|`Imports`\|`Prompt` | `"Prompt"` (or `"Off"` in some client defaults) | Whether/how vulnerability-driven diagnostics on `go.mod` run |
| `diagnosticsDelay` | `time.Duration` | `"1s"` | Idle time after an edit before workspace-wide analysis diagnostics recompute (open-file compile errors update sooner regardless) |
| `diagnosticsTrigger` | enum: `Edit`\|`Save` | `"Edit"` | Whether diagnostics recompute on every edit or only on save |
| `pullDiagnostics` | `bool` | `false` | Let the client request diagnostics on demand (`textDocument/diagnostic`) instead of only receiving pushed updates |

**When it matters:** a large monorepo with `diagnosticsTrigger: "Edit"` (the default) can feel laggy under `diagnosticsDelay: "1s"` on every keystroke pause — switching to `"Save"` trades immediacy for fewer full-workspace recomputations. Turning on `staticcheck` surfaces a materially different (larger) set of findings than the default analyzer set — expect more `go_diagnostics`/`gopls check` output afterward, not a regression.

## Documentation

| Setting | Type | Default | Purpose |
| --- | --- | --- | --- |
| `hoverKind` | enum: `FullDocumentation`\|`SingleLine`\|`Structured`\|`NoDocumentation`\|`SynopsisDocumentation` | `"FullDocumentation"` | How much doc text Hover renders |
| `linksInHover` | `bool` | `true` | Whether hover markdown includes doc-comment links |
| `linkTarget` | `string` | `"pkg.go.dev"` | Base host used when generating documentation links (hover, Document Link, diagnostics) |

## Inlay hints

| Setting | Type | Default | Purpose |
| --- | --- | --- | --- |
| `hints` | `map[string]bool` | `{}` (all off) | Enables specific inlay hint kinds — keys are `parameterNames`, `assignVariableTypes`, `compositeLiteralFields`, `compositeLiteralTypes`, `constantValues`, `functionTypeParameters`, `rangeVariableTypes` |

Example:

```json
"hints": {
  "parameterNames": true,
  "assignVariableTypes": true
}
```

## Navigation

| Setting | Type | Default | Purpose |
| --- | --- | --- | --- |
| `symbolMatcher` | enum: `FastFuzzy`\|`Fuzzy`\|`CaseSensitive`\|`CaseInsensitive` | `"FastFuzzy"` | Matching algorithm for `workspace/symbol` / `go_search` |
| `symbolScope` | enum: `all`\|`workspace` | `"all"` | Whether symbol search covers only workspace packages or every loaded package (including dependencies) |
| `symbolStyle` | enum | — | How matched symbols are qualified in the response (package-qualified vs. bare) |
| `codelenses` | `map[string]bool` | — | Enables/disables individual code lenses (e.g. `generate`, `tidy`, `vendor`, `run_tests`) |

---

For the complete, always-current settings surface (including experimental and client-specific keys), see `gopls api-json` or the upstream settings page linked above — this table covers the settings most likely to change how navigation, diagnostics, or refactors behave day-to-day, not the full API.
