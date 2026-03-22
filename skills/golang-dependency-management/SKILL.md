---
name: golang-dependency-management
description: Provides dependency management strategies for Golang projects including go.mod management, installing/upgrading packages, semantic versioning, Minimal Version Selection, vulnerability scanning, outdated dependency tracking, dependency size analysis, automated updates with Dependabot/Renovate, conflict resolution, and dependency graph visualization. Use this skill whenever adding, removing, updating, or auditing Go dependencies, resolving version conflicts, setting up automated dependency updates, analyzing binary size, or working with go.work workspaces.
user-invocable: false
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents, and for projects using Golang.
metadata:
  author: samber
  version: "1.1.0"
  openclaw:
    emoji: "📦"
    homepage: https://github.com/samber/cc-skills-golang
    requires:
      bins:
        - go
        - govulncheck
    install:
      - kind: go
        package: golang.org/x/vuln/cmd/govulncheck@latest
        bins: [govulncheck]
allowed-tools: Read Edit Write Glob Grep Bash(go:*) Bash(golangci-lint:*) Bash(git:*) Agent Bash(govulncheck:*)
---

**Persona:** You are a Go dependency steward. You treat every new dependency as a long-term maintenance commitment — you ask whether the standard library already solves the problem before reaching for an external package.

# Go Dependency Management

## AI Agent Rule: Ask Before Adding Dependencies

**Before running `go get` to add any new dependency, AI agents MUST ask the user for confirmation.** AI agents can suggest packages that are unmaintained, low-quality, or unnecessary when the standard library already provides equivalent functionality. Using `go get -u` to upgrade an existing dependency is safe.

Before proposing a dependency, present:

- Package name and import path
- What it does and why it's needed
- Whether the standard library covers the use case
- GitHub stars, last commit date, and maintenance status (check via `gh repo view`)
- License compatibility
- Known alternatives

The `samber/cc-skills-golang@golang-popular-libraries` skill contains a curated list of vetted, production-ready libraries. Prefer recommending packages from that list. When no vetted option exists, favor well-known packages from the Go team (`golang.org/x/...`) or established organizations over obscure alternatives.

## Key Rules

- `go.sum` MUST be committed — it records cryptographic checksums of every dependency version, letting `go mod verify` detect supply-chain tampering. Without it, a compromised proxy could silently substitute malicious code
- `govulncheck ./...` before every release — catches known CVEs in your dependency tree before they reach production
- Check maintenance status, license, and stdlib alternatives before adding a dependency — every dependency increases attack surface, maintenance burden, and binary size
- `go mod tidy` before every commit that changes dependencies — removes unused modules and adds missing ones, keeping go.mod honest

## go.mod & go.sum

### Essential Commands

| Command           | Purpose                                      |
| ----------------- | -------------------------------------------- |
| `go mod tidy`     | Add missing deps, remove unused ones         |
| `go mod download` | Download modules to local cache              |
| `go mod verify`   | Verify cached modules match go.sum checksums |
| `go mod vendor`   | Copy deps into `vendor/` directory           |
| `go mod edit`     | Edit go.mod programmatically (scripts, CI)   |
| `go mod graph`    | Print the module requirement graph           |
| `go mod why`      | Explain why a module or package is needed    |

### Vendoring

Use `go mod vendor` when you need hermetic builds (no network access), reproducibility guarantees beyond checksums, or when deploying to environments without module proxy access. CI pipelines and Docker builds sometimes benefit from vendoring. Run `go mod vendor` after any dependency change and commit the `vendor/` directory.

## Installing & Upgrading Dependencies

### Adding a Dependency

```bash
go get github.com/pkg/errors           # Latest version
go get github.com/pkg/errors@v0.9.1    # Specific version
go get github.com/pkg/errors@latest    # Explicitly latest
go get github.com/pkg/errors@master    # Specific branch (pseudo-version)
```

### Upgrading

```bash
go get -u ./...            # Upgrade ALL direct+indirect deps to latest minor/patch
go get -u=patch ./...      # Upgrade to latest patch only (safer)
go get github.com/pkg@v1.5 # Upgrade specific package
```

**Prefer `go get -u=patch`** for routine updates — patch versions change no public API (semver promise), so they're unlikely to break your build. Minor version upgrades may add new APIs but can also deprecate or change behavior unexpectedly.

### Removing a Dependency

```bash
go get github.com/pkg/errors@none   # Mark for removal
go mod tidy                          # Clean up go.mod and go.sum
```

### Installing CLI Tools

```bash
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
```

`go install` builds and installs a binary to `$GOPATH/bin`. Use `@latest` or a specific version tag — never `@master` for tools you depend on.

### The tools.go Pattern

Pin tool versions in your module without importing them in production code:

```go
//go:build tools

package tools

import (
    _ "github.com/golangci/golangci-lint/cmd/golangci-lint"
    _ "golang.org/x/vuln/cmd/govulncheck"
)
```

The build constraint ensures this file is never compiled. The blank imports keep the tools in `go.mod` so `go install` uses the pinned version. Run `go mod tidy` after creating this file.

## Deep Dives

- **[Versioning & MVS](./references/versioning.md)** — Semantic versioning rules (major.minor.patch), when to increment each number, pre-release versions, the Minimal Version Selection (MVS) algorithm (why you can't just pick "latest"), and major version suffix conventions (v0, v1, v2 suffixes for breaking changes).

- **[Auditing Dependencies](./references/auditing.md)** — Vulnerability scanning with `govulncheck`, tracking outdated dependencies, analyzing which dependencies make the binary large (`goweight`), and distinguishing test-only vs binary dependencies to keep `go.mod` clean.

- **[Dependency Conflicts & Resolution](./references/conflicts.md)** — Diagnosing version conflicts (what `go get` does when you request incompatible versions), resolution strategies (`replace` directives for local development, `exclude` for broken versions, `retract` for published versions that should be skipped), and workflows for conflicts across your dependency tree.

- **[Go Workspaces](./references/workspaces.md)** — `go.work` files for multi-module development (e.g., library + example application), when to use workspaces vs monorepos, and workspace best practices.

- **[Automated Dependency Updates](./references/automated-updates.md)** — Setting up Dependabot or Renovate for automatic dependency update PRs, auto-merge strategies (when to merge automatically vs require review), and handling security updates.

- **[Visualizing the Dependency Graph](./references/visualization.md)** — `go mod graph` to inspect the full dependency tree, `modgraphviz` to visualize it, and interactive tools to find which dependency chains cause bloat.

## Cross-References

- → See `samber/cc-skills-golang@golang-continuous-integration` skill for Dependabot/Renovate CI setup
- → See `samber/cc-skills-golang@golang-security` skill for vulnerability scanning with govulncheck
- → See `samber/cc-skills-golang@golang-popular-libraries` skill for vetted library recommendations

## Quick Reference

```bash
# Start a new module
go mod init github.com/user/project

# Add a dependency
go get github.com/pkg/errors@v0.9.1

# Upgrade all deps (patch only, safer)
go get -u=patch ./...

# Remove unused deps
go mod tidy

# Check for vulnerabilities
govulncheck ./...

# Check for outdated deps
go list -u -m -json all | go-mod-outdated -update -direct

# Analyze binary size by dependency
goweight

# Understand why a dep exists
go mod why -m github.com/some/module

# Visualize dependency graph
go mod graph | modgraphviz | dot -Tpng -o deps.png

# Verify checksums
go mod verify
```
