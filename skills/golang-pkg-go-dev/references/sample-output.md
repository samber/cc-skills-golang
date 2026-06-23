# godig sample output

Representative `-o md` output for each command, captured against `godig` v0.1.0. Empty cells are shown as `—`. Field sets mirror the pkg.go.dev API and may grow over time.

## overview

`godig overview github.com/samber/ro -o md`

| field             | value                          |
| ----------------- | ------------------------------ |
| isStandardLibrary | false                          |
| latestVersion     | v0.3.0                         |
| licenses          | ["Apache-2.0"]                 |
| modulePath        | github.com/samber/ro           |
| name              | ro                             |
| path              | github.com/samber/ro           |
| recentVersions    | ["v0.3.0","v0.2.0","v0.1.0"]   |
| repoUrl           | <https://github.com/samber/ro> |

## search

`godig search ro --limit 3 -o md`

| modulePath | packagePath | synopsis | version |
| --- | --- | --- | --- |
| github.com/samber/ro | github.com/samber/ro | — | v0.3.0 |
| github.com/blevesearch/bleve | github.com/blevesearch/bleve/analysis/lang/ro | — | v1.0.14 |
| github.com/blevesearch/bleve/v2 | github.com/blevesearch/bleve/v2/analysis/lang/ro | — | v2.6.0 |

## package info

`godig package info github.com/samber/ro -o md`

| field             | value                |
| ----------------- | -------------------- |
| goarch            | all                  |
| goos              | all                  |
| isLatest          | true                 |
| isRedistributable | true                 |
| isStandardLibrary | false                |
| modulePath        | github.com/samber/ro |
| name              | ro                   |
| path              | github.com/samber/ro |
| version           | v0.3.0               |

## package imports

`godig package imports github.com/samber/ro -o md` — a plain list (no `--limit`):

```text
- context
- errors
- fmt
- ...
```

## versions

`godig versions github.com/samber/ro --limit 3 -o md`

| commitTime | deprecated | deprecationReason | hasGoMod | isRedistributable | latestVersion | modulePath | retracted | retractionReason | version |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-03-02T15:16:08Z | false | — | true | true | v0.3.0 | github.com/samber/ro | false | — | v0.3.0 |
| 2025-10-25T22:20:38Z | false | — | true | false | v0.3.0 | github.com/samber/ro | false | — | v0.2.0 |
| 2025-10-14T12:21:03Z | false | — | true | false | v0.3.0 | github.com/samber/ro | false | — | v0.1.0 |

## major-versions

`godig major-versions github.com/samber/lo -o md`

| isLatest | major | modulePath           | version |
| -------- | ----- | -------------------- | ------- |
| true     | v1    | github.com/samber/lo | v1.53.0 |

## imported-by

`godig imported-by github.com/samber/ro --limit 3 -o md`

| package                                |
| -------------------------------------- |
| github.com/CooperCorona/websocket      |
| github.com/CooperCorona/websocket/test |
| github.com/samber/ro/ee/plugins/otel   |

## vulns

`godig vulns github.com/dgrijalva/jwt-go -o md`

| details | fixedVersion | id | summary |
| --- | --- | --- | --- |
| Authorization bypass in github.com/dgrijalva/jwt-go | — | GO-2020-0017 | — |

`vulns` returns an empty list when a module has no known vulnerabilities.

## dependencies

`godig dependencies github.com/samber/ro -o md` — one section per go.mod block (`requires`, `replaces`, `excludes`, `go` directive):

```markdown
## requires

| path                       | version | indirect |
| -------------------------- | ------- | -------- |
| github.com/samber/lo       | v1.52.0 | —        |
| github.com/davecgh/go-spew | v1.1.1  | true     |
```

## module info

`godig module info github.com/samber/ro -o md`

| field             | value                          |
| ----------------- | ------------------------------ |
| commitTime        | 2026-03-02T15:16:08Z           |
| goVersion         | 1.18                           |
| hasGoMod          | true                           |
| isLatest          | true                           |
| isRedistributable | true                           |
| isStandardLibrary | false                          |
| path              | github.com/samber/ro           |
| repoUrl           | <https://github.com/samber/ro> |
| size              | 137530                         |
| version           | v0.3.0                         |

## packages

`godig packages github.com/samber/ro --limit 4 -o md`

| isRedistributable | name | path | synopsis |
| --- | --- | --- | --- |
| true | ro | github.com/samber/ro | — |
| true | constraints | github.com/samber/ro/internal/constraints | — |
| true | xatomic | github.com/samber/ro/internal/xatomic | — |
| true | xerrors | github.com/samber/ro/internal/xerrors | — |

## symbols

`godig symbols github.com/samber/ro --limit 4 -o md`

| kind     | name              | parent          | synopsis                  |
| -------- | ----------------- | --------------- | ------------------------- |
| Type     | Backpressure      | Backpressure    | type Backpressure int8    |
| Constant | BackpressureBlock | Backpressure    | const BackpressureBlock   |
| Constant | BackpressureDrop  | Backpressure    | const BackpressureDrop    |
| Type     | ConcurrencyMode   | ConcurrencyMode | type ConcurrencyMode int8 |

## symbol doc

`godig symbol doc github.com/samber/lo Map -o md` — token-efficient vs `package doc`:

| field | value |
| --- | --- |
| goarch | all |
| goos | all |
| kind | Function |
| name | Map |
| path | github.com/samber/lo |
| signature | func Map[T, R any](collection []T, transform func(item T, index int) R) []R |
| synopsis | Map manipulates a slice and transforms it to a slice of another type. |
| version | v1.53.0 |

## Raw / large output

`package doc`, `package examples`, `symbol examples` and `module readme` return raw Markdown (use `-o md` or `-o raw`), e.g.:

```markdown
# package ro

## Constants

...
```

`package licenses` and `module licenses` return the full license text.
