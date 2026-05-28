# Project analysis — discover and configure relevant skills

Run this analysis when setting up a new project or onboarding an existing one. The goal: detect which Go skills apply, confirm with the user, then write a `## Required Go skills` block to `CLAUDE.md` (or `AGENTS.md`).

## Step 1 — Read go.mod

Read `go.mod`. Extract all direct `require` entries and the `go` directive (language version).

Key signals:

| Dependency (go.mod) | Skill to load |
| --- | --- |
| `github.com/spf13/cobra` | `golang-spf13-cobra` |
| `github.com/spf13/viper` | `golang-spf13-viper` |
| `google.golang.org/grpc` | `golang-grpc` |
| `github.com/99designs/gqlgen` or `github.com/graphql-go/graphql` | `golang-graphql` |
| `github.com/swaggo/swag` | `golang-swagger` |
| `github.com/stretchr/testify` | `golang-stretchr-testify` |
| `github.com/google/wire` | `golang-google-wire` |
| `go.uber.org/dig` | `golang-uber-dig` |
| `go.uber.org/fx` | `golang-uber-fx` |
| `github.com/samber/do` | `golang-samber-do` |
| `github.com/samber/lo` | `golang-samber-lo` |
| `github.com/samber/mo` | `golang-samber-mo` |
| `github.com/samber/ro` | `golang-samber-ro` |
| `github.com/samber/oops` | `golang-samber-oops` |
| `github.com/samber/slog-*` | `golang-samber-slog` |
| `github.com/samber/hot` | `golang-samber-hot` |
| `database/sql`, `gorm.io/gorm`, `github.com/jmoiron/sqlx`, `github.com/sqlc-dev/sqlc`, `github.com/volatiletech/sqlboiler` | `golang-database` |
| `go.opentelemetry.io/otel` or `github.com/prometheus/client_golang` | `golang-observability` |
| `go.temporal.io/sdk` | `golang-temporal` ⚠️ (skill not yet available — inform user) |
| `go` directive ≥ 1.21 | `golang-modernize` |

## Step 2 — Scan directory structure

Use `Glob` or `Bash(find ...)` on the project root. Infer project type and architecture from what exists.

| Directory / file pattern | Signal |
| --- | --- |
| `cmd/` with subfolders | Multi-binary or subcommand CLI → `golang-cli`, `golang-spf13-cobra` |
| `internal/` | Structured package layout → `golang-design-patterns` |
| `pkg/` | Exported library → `golang-structs-interfaces` |
| `api/` or `proto/` or `*.proto` | Protocol Buffers / gRPC → `golang-grpc` |
| `migrations/` or `schema/` | Database migrations → `golang-database` |
| `.github/workflows/` | CI pipeline → `golang-continuous-integration` |
| `*_test.go` files present | Tests exist → `golang-testing` |
| No `*_test.go` files | No tests yet → `golang-testing` (critical, flag to user) |
| `docker-compose.yml` or `Dockerfile` | Production service → `golang-observability` |

## Step 3 — Scan top-level imports

Grep imports across `cmd/`, `internal/`, `pkg/` to detect actual usage patterns:

```bash
grep -rh '"' --include="*.go" cmd/ internal/ pkg/ 2>/dev/null | grep -oP '"[^"]*"' | sort -u
```

| Import pattern | Signal |
| --- | --- |
| `"context"` used broadly | `golang-context` |
| `"sync"`, `"sync/atomic"`, `"golang.org/x/sync/errgroup"` | `golang-concurrency` |
| `"database/sql"` or ORM | `golang-database` |
| `"log/slog"` | `golang-observability`, `golang-samber-slog` (if samber/slog-* in go.mod) |
| `"crypto/*"` or `"crypto/tls"` | `golang-security` |
| `"os/exec"` or `"net/http"` with user input | `golang-security` |
| Complex error wrapping (`fmt.Errorf`, `errors.As`) | `golang-error-handling` |

## Step 4 — Infer project stage and type

| Observation | Inference |
| --- | --- |
| < 10 Go files, no tests | Early stage — prioritize `golang-testing`, `golang-project-layout`, `golang-lint` |
| Tests exist, no CI | Growing project — add `golang-continuous-integration` |
| Has CI, has Docker, has observability imports | Production service — add `golang-observability`, `golang-security` |
| Library (no `cmd/`, exported API in `pkg/`) | Library project — add `golang-documentation`, `golang-structs-interfaces` |
| Multiple `go.mod` files | Monorepo — add `golang-dependency-management` |
| CLI tool (cobra + viper, single binary) | `golang-cli`, `golang-spf13-cobra`, `golang-spf13-viper` |
| gRPC service | `golang-grpc`, `golang-error-handling`, `golang-observability` |
| REST API | `golang-swagger` (if swag present), `golang-security`, `golang-observability` |

## Step 5 — Always-on baseline

Regardless of project type, always include these:

- `golang-code-style`
- `golang-naming`
- `golang-error-handling`
- `golang-safety`
- `golang-testing`

## Step 6 — Confirm with user

Use `AskUserQuestion` to present the detected skill set:

- **Detected** (pre-selected, from steps 1–4)
- **Baseline** (always included, from step 5)
- **Optional** (skills that might apply — ask if uncertain)

If the project is ambiguous (no go.mod, empty repo, monorepo root), ask the user to clarify the project type before proceeding.

## Step 7 — Write to CLAUDE.md

Follow the configure-mode workflow from `samber/cc-skills-golang@golang-how-to` ([project-config.md](../../golang-how-to/references/project-config.md)):

1. Detect which agent config file exists (`CLAUDE.md` > `AGENTS.md` > `.cursor/rules`)
2. Check for existing `## Required Go skills` block (idempotency)
3. Write or update the block with the confirmed skill list using FQN identifiers (`samber/cc-skills-golang@<name>`)
