---
name: golang-continuous-integration
description: "Provides CI/CD pipeline configuration using GitHub Actions for Golang projects. Covers testing, linting, SAST, security scanning, code coverage, Dependabot, Renovate, GoReleaser, code review automation, and release pipelines. Use this whenever setting up CI for a Go project, configuring workflows, adding linters or security scanners, setting up Dependabot or Renovate, automating releases, or improving an existing CI pipeline. Also use when the user wants to add quality gates to their Go project."
user-invocable: true
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents, and for projects using Golang.
metadata:
  author: samber
  version: "1.1.2"
  openclaw:
    emoji: "🚀"
    homepage: https://github.com/samber/cc-skills-golang
    requires:
      bins:
        - go
        - goreleaser
        - gh
    install:
      - kind: brew
        formula: goreleaser
        bins: [goreleaser]
      - kind: brew
        formula: gh
        bins: [gh]
allowed-tools: Read Edit Write Glob Grep Bash(go:*) Bash(golangci-lint:*) Bash(git:*) Agent WebFetch Bash(goreleaser:*) Bash(gh:*) AskUserQuestion
---

**Persona:** You are a Go DevOps engineer. You treat CI as a quality gate — every pipeline decision is weighed against build speed, signal reliability, and security posture.

**Modes:**

- **Setup** — adding CI to a project for the first time: start with the Quick Reference table, then generate workflows in this order: test → lint → security → release. Always check latest action versions before writing YAML.
- **Improve** — auditing or extending an existing pipeline: read current workflow files first, identify gaps against the Quick Reference table, then propose targeted additions without duplicating existing steps.

# Go Continuous Integration

Set up production-grade CI/CD pipelines for Go projects using GitHub Actions.

## Action Versions

The versions shown in the examples below are reference versions that may be outdated. Before generating workflow files, search the internet for the latest stable major version of each GitHub Action used (e.g., `actions/checkout`, `actions/setup-go`, `golangci/golangci-lint-action`, `codecov/codecov-action`, `goreleaser/goreleaser-action`, etc.). Use the latest version you find, not the one hardcoded in the examples.

## Quick Reference

| Stage         | Tool                        | Purpose                       |
| ------------- | --------------------------- | ----------------------------- |
| **Test**      | `go test -race`             | Unit + race detection         |
| **Coverage**  | `codecov/codecov-action`    | Coverage reporting            |
| **Lint**      | `golangci-lint`             | Comprehensive linting         |
| **Vet**       | `go vet`                    | Built-in static analysis      |
| **SAST**      | `gosec`, `CodeQL`, `Bearer` | Security static analysis      |
| **Vuln scan** | `govulncheck`               | Known vulnerability detection |
| **Docker**    | `docker/build-push-action`  | Multi-platform image builds   |
| **Deps**      | Dependabot / Renovate       | Automated dependency updates  |
| **Release**   | GoReleaser                  | Automated binary releases     |

---

## Testing

`.github/workflows/test.yml` — see [test.yml](./assets/test.yml)

Adapt the Go version matrix to match `go.mod`:

```
go 1.23   → matrix: ["1.23", "1.24", "1.25", "1.26", "stable"]
go 1.24   → matrix: ["1.24", "1.25", "1.26", "stable"]
go 1.25   → matrix: ["1.25", "1.26", "stable"]
go 1.26   → matrix: ["1.26", "stable"]
```

Use `fail-fast: false` so a failure on one Go version doesn't cancel the others.

Test flags:

- `-race`: CI MUST run tests with the `-race` flag (catches data races — undefined behavior in Go)
- `-shuffle=on`: Randomize test order to catch inter-test dependencies
- `-coverprofile`: Generate coverage data
- `git diff --exit-code`: Fails if `go mod tidy` changes anything

### Coverage Configuration

CI SHOULD enforce code coverage thresholds. Configure thresholds in `codecov.yml` at the repo root — see [codecov.yml](./assets/codecov.yml)

---

## Integration Tests

`.github/workflows/integration.yml` — see [integration.yml](./assets/integration.yml)

Use `-count=1` to disable test caching — cached results can hide flaky service interactions.

---

## Linting

`golangci-lint` MUST be run in CI on every PR. `.github/workflows/lint.yml` — see [lint.yml](./assets/lint.yml)

### golangci-lint Configuration

Create `.golangci.yml` at the root of the project. See the `samber/cc-skills-golang@golang-linter` skill for the recommended configuration.

---

## Security & SAST

`.github/workflows/security.yml` — see [security.yml](./assets/security.yml)

CI MUST run `govulncheck`. It only reports vulnerabilities in code paths your project actually calls — unlike generic CVE scanners. CodeQL results appear in the repository's Security tab. Bearer is good at detecting sensitive data flow issues.

### CodeQL Configuration

Create `.github/codeql/codeql-config.yml` to use the extended security query suite — see [codeql-config.yml](./assets/codeql-config.yml)

Available query suites:

- **default**: Standard security queries
- **security-extended**: Extra security queries with slightly lower precision
- **security-and-quality**: Security queries plus maintainability and reliability checks

### Container Image Scanning

If the project produces Docker images, Trivy container scanning is included in the Docker workflow — see [docker.yml](./assets/docker.yml)

---

## Dependency Management

### Dependabot

`.github/dependabot.yml` — see [dependabot.yml](./assets/dependabot.yml)

Minor/patch updates are grouped into a single PR. Major updates get individual PRs since they may have breaking changes.

#### Auto-Merge for Dependabot

`.github/workflows/dependabot-auto-merge.yml` — see [dependabot-auto-merge.yml](./assets/dependabot-auto-merge.yml)

> **Security warning:** This workflow requires `contents: write` and `pull-requests: write` — these are elevated permissions that allow merging PRs and modifying repository content. The `if: github.actor == 'dependabot[bot]'` guard restricts execution to Dependabot only. Do not remove this guard. Note that `github.actor` checks are not fully spoof-proof — **branch protection rules are the real safety net**. Ensure branch protection is configured (see [Repository Security Settings](#repository-security-settings)) with required status checks and required approvals so that auto-merge only succeeds after all checks pass, regardless of who triggered the workflow.

### Renovate (alternative)

Renovate is a more mature and configurable alternative to Dependabot. It supports automerge natively, grouping, scheduling, regex managers, and monorepo-aware updates. If Dependabot feels too limited, Renovate is the go-to choice.

Install the [Renovate GitHub App](https://github.com/apps/renovate), then create `renovate.json` at the repo root — see [renovate.json](./assets/renovate.json)

Key advantages over Dependabot:

- **`gomodTidy`**: Automatically runs `go mod tidy` after updates
- **Native automerge**: No separate workflow needed
- **Better grouping**: More flexible rules for grouping PRs
- **Regex managers**: Can update versions in Dockerfiles, Makefiles, etc.
- **Monorepo support**: Handles Go workspaces and multi-module repos

---

## Release Automation

GoReleaser automates binary builds, checksums, and GitHub Releases. The configuration varies significantly depending on the project type.

### Release Workflow

`.github/workflows/release.yml` — see [release.yml](./assets/release.yml)

> **Security warning:** This workflow requires `contents: write` to create GitHub Releases. It is restricted to tag pushes (`tags: ["v*"]`) so it cannot be triggered by pull requests or branch pushes. Only users with push access to the repository can create tags.

### GoReleaser for CLI/Programs

Programs need cross-compiled binaries, archives, and optionally Docker images.

`.goreleaser.yml` — see [goreleaser-cli.yml](./assets/goreleaser-cli.yml)

### GoReleaser for Libraries

Libraries don't produce binaries — they only need a GitHub Release with a changelog. Use a minimal config that skips the build.

`.goreleaser.yml` — see [goreleaser-lib.yml](./assets/goreleaser-lib.yml)

For libraries, you may not even need GoReleaser — a simple GitHub Release created via the UI or `gh release create` is often sufficient.

### GoReleaser for Monorepos / Multi-Binary

When a repository contains multiple commands (e.g., `cmd/api/`, `cmd/worker/`).

`.goreleaser.yml` — see [goreleaser-monorepo.yml](./assets/goreleaser-monorepo.yml)

### Docker Build & Push

For projects that produce Docker images. This workflow builds multi-platform images, generates SBOM and provenance attestations, pushes to both GitHub Container Registry (GHCR) and Docker Hub, and includes Trivy container scanning.

`.github/workflows/docker.yml` — see [docker.yml](./assets/docker.yml)

> **Security warning:** Permissions are scoped per job: the `container-scan` job only gets `contents: read` + `security-events: write`, while the `docker` job gets `packages: write` (to push to GHCR) and `attestations: write` + `id-token: write` (for provenance/SBOM signing). This ensures the scan job cannot push images even if compromised. The `push` flag is set to `false` on pull requests so untrusted code cannot publish images. The `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets must be configured in the repository secrets settings — never hardcode credentials.

Key details:

- **QEMU + Buildx**: Required for multi-platform builds (`linux/amd64,linux/arm64`). Remove platforms you don't need.
- **`push: false` on PRs**: Images are built but never pushed on pull requests — this validates the Dockerfile without publishing untrusted code.
- **Metadata action**: Automatically generates semver tags (`v1.2.3` → `1.2.3`, `1.2`, `1`), branch tags (`main`), and SHA tags.
- **Provenance + SBOM**: `provenance: mode=max` and `sbom: true` generate supply chain attestations. These require `attestations: write` and `id-token: write` permissions.
- **Dual registry**: Pushes to both GHCR (using `GITHUB_TOKEN`, no extra secret needed) and Docker Hub (requires `DOCKERHUB_USERNAME` + `DOCKERHUB_TOKEN` secrets). Remove the Docker Hub login and image line if not needed.
- **Trivy**: Scans the built image for CRITICAL and HIGH vulnerabilities and uploads results to the Security tab.
- Adapt the image names and registries to your project. For GHCR-only, remove the Docker Hub login step and the `docker.io/` line from `images:`.

---

## Repository Security Settings

After creating workflow files, ALWAYS tell the developer to configure GitHub repository settings (branch protection, workflow permissions, secrets, environments) — see [repo-security.md](./references/repo-security.md)

---

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Missing `-race` in CI tests | Always use `go test -race` |
| No `-shuffle=on` | Randomize test order to catch inter-test dependencies |
| Caching integration test results | Use `-count=1` to disable caching |
| `go mod tidy` not checked | Add `go mod tidy && git diff --exit-code` step |
| Missing `fail-fast: false` | One Go version failing shouldn't cancel other jobs |
| Not pinning action versions | GitHub Actions MUST use pinned major versions (e.g. `@vN`, not `@master`) |
| No `permissions` block | Follow least-privilege per job |
| Ignoring govulncheck findings | Fix or suppress with justification |

## Related Skills

See `samber/cc-skills-golang@golang-linter`, `samber/cc-skills-golang@golang-security`, `samber/cc-skills-golang@golang-testing`, `samber/cc-skills-golang@golang-dependency-management` skills.
