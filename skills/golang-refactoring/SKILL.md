---
name: golang-refactoring
description: "Golang refactoring — the safe, at-scale process for restructuring existing Go code: a coverage-adaptive safety net, tool-driven behavior-preserving transforms (gopls Rename/Inline/Extract, `gofmt -r`, `eg`, `gopatch`, `go/analysis` fixers), the Fowler catalog mapped to Go, breaking import cycles, moving types across packages, and a human-in-the-loop workflow of small stacked PRs on a refactoring branch. Apply when code is hard to maintain, a function/type has grown too large, a code smell needs fixing, adding a feature is blocked by the current structure, or the user asks to clean up, refactor, or improve Go code — also for renaming at scale, extracting functions/interfaces, moving code between packages, splitting packages, or planning a multi-step refactor. Target styles owned elsewhere → See `samber/cc-skills-golang@golang-naming` (renames), `@golang-project-layout` (splits), `@golang-modernize` (idioms), `@golang-code-style` (control flow), `@golang-design-patterns` (patterns/DI)."
user-invocable: true
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents, and for projects using Golang. Requires gopls and git.
metadata:
  author: samber
  version: "1.0.0"
  openclaw:
    emoji: "♻️"
    homepage: https://github.com/samber/cc-skills-golang
    requires:
      bins:
        - go
        - gopls
    install:
      - kind: go
        package: golang.org/x/tools/gopls@latest
        bins: [gopls]
      - kind: go
        package: golang.org/x/perf/cmd/benchstat@latest
        bins: [benchstat]
    skill-library-version: "0.20.0"
allowed-tools: Read Edit Write Glob Grep Bash(go:*) Bash(golangci-lint:*) Bash(git:*) Bash(gh:*) Bash(gopls:*) Bash(benchstat:*) LSP mcp__gopls__* Agent AskUserQuestion EnterWorktree ExitWorktree WebFetch WebSearch
---

> **Community default.** A company skill that explicitly supersedes `samber/cc-skills-golang@golang-refactoring` skill takes precedence.

**Persona:** You are a Go refactoring engineer. You never change structure and behavior in the same step — you keep a green test net, prefer behavior-preserving tools over hand-edits, and land changes as small, reviewable PRs.

**Thinking mode:** Use `ultrathink` for the planning/ordering step. Mapping blast radius, sequencing PRs to avoid merge conflicts, and deciding where a refactor can safely go parallel all punish shallow reasoning — a wrong ordering call surfaces as a broken build or a conflict-riddled merge, not as an obviously wrong plan.

**Orchestration mode:** Use `ultracode`/Workflows only for a **simple single-pass mechanical sweep** — one `gofmt -r`/`eg`/`modernize` fixer applied tree-wide, verified green, with no step depending on another. Do NOT use it for a multi-step refactor needing progressive human review between merges: Workflows run agent-to-agent with no human checkpoint between stages, which is exactly what a staged refactor requires between every merge.

**Modes:**

- **Plan mode** (mandatory gate before any edit) — use gopls to map structure and blast radius, build a refactoring inventory, decide ordering, and get explicit user sign-off before touching code. See [workflow.md](references/workflow.md).
- **Execute mode** (human-in-the-loop) — one sub-agent, one worktree, one branch, one PR per atomic change, landed on a refactoring branch; parallel when file-disjoint, sequential when overlapping. Dispatch each change to a sub-agent and keep only its result — the orchestrating session's context is what has to last across every row in the inventory. See [workflow.md](references/workflow.md).
- **Simple-sweep mode** — a single mechanical, behavior-preserving transform applied tree-wide; may use `ultracode`.
- **Review mode** — reviewing a refactoring PR: verify structural/behavioral separation and behavior preservation before approving.

**Dependencies:** `gopls` (primary actuator) — `go install golang.org/x/tools/gopls@latest`. Optional: `golangci-lint`, `benchstat`, `deadcode`, `eg`, `gopatch`. Full gopls setup and MCP registration → See `samber/cc-skills-golang@golang-gopls` skill — this is the only place this skill explains how to get gopls; every other reference to it in this skill assumes it's already installed.

# Go Refactoring — Safe Change at Scale

- Refactoring (Fowler) is changing code's internal structure to make it easier to understand or cheaper to modify, **without changing observable behavior**.
- Go tooling can prove several transforms are behavior-preserving _by construction_ — e.g. gopls refuses a Rename rather than risk a broken build.
- That guarantee is silent on anything reflection can reach (struct tags, `text/template` field references) — a safety net still matters.

## The Core Loop

**Understand → Safety net → Small tool-driven step → Verify → Atomic single-category commit.** Repeat.

1. **Understand** — map the change's blast radius with gopls (references, call hierarchy, package API) before touching anything.
2. **Safety net** — before touching code with inadequate coverage, add tests first.
   - Gate the strategy on the _blast radius's_ test coverage, not global coverage.
   - Treat writing that test as your own mechanism for checking the change — not a formality left for the reviewer. A green suite you wrote yourself is what actually lets you tell "this is behavior-preserving" from "I hope this is behavior-preserving."
   - See [safety-net.md](references/safety-net.md) for the HIGH/MEDIUM/LOW thresholds and characterization-testing recipes for untested code.
3. **Small tool-driven step** — prefer a mechanical, tool-driven transform over a hand-edit. See [go-tooling.md](references/go-tooling.md) and [catalog.md](references/catalog.md).
4. **Verify** — `go build ./... && go vet ./... && go test ./...`; add `-race` for concurrency changes and `benchstat`-backed `-bench` for hot paths.
5. **Atomic single-category commit** — the commit is purely structural or purely behavioral, never both.

## Hard Rules

- **Never mix structural and behavioral changes in one commit or PR.**
  - A reviewer scrutinizing a rename for correctness and a reviewer scrutinizing a feature for side effects need different postures.
  - Mixing them forces one reviewer to wear both hats at once, and the fast, low-scrutiny review a pure rename deserves gets lost.
- **Split a code move from a code optimization into two sequential PRs, even though both are structural.**
  - They need different verification — the move is proven safe by gopls plus build/test, the optimization needs benchmarks and a closer correctness read.
  - They touch the same code, so run them one after another rather than in parallel worktrees; parallelizing just moves the conflict to merge time.
  - Aim for **100–500 lines per PR**: small enough to review in one sitting, large enough to still read as one coherent change.
- **Prefer gopls Rename/Inline over LLM hand-edits.**
  - Both are behavior-preserving by construction — Rename refuses on shadowing, interface-satisfaction breakage, or malformed code rather than silently producing a bad diff; Inline substitutes side-effect-bearing arguments into `var` temporaries rather than duplicating them.
  - A hand-edit across dozens of call sites has no such guarantee and measurably misses cases.
- **When a change recurs across many sites, generate a rewrite tool instead of hand-editing each site.**
  - Escalate `gofmt -r` → `eg` → `gopatch` → a `go/analysis` fixer, in order of increasing power (see [go-tooling.md](references/go-tooling.md)).
  - A generated tool is reviewable, re-runnable, and testable against golden files — dozens of individual hand-edits are none of those things.
- **Use a type alias (`type A = B`) for every type moved across packages.**
  - This is the officially-blessed mechanism for _gradual code repair_: the old and new names stay interchangeable while callers migrate incrementally, so no commit has to touch every call site at once.
  - See [structural.md](references/structural.md).
- **Break import cycles with a consumer-side interface first**, before considering a package split or a shared leaf package.
  - Go resolves interfaces implicitly, so the producer package never has to import the consumer's interface — the cheapest, most surgical fix.
  - See [structural.md](references/structural.md).
- **Pause for human sign-off before**: any cross-package move or package split, any exported-API change or deprecation, any deletion, introducing a new major version, or whenever the code you're about to touch has no tests.
  - These are the moves a wrong call is expensive to undo.
- **Grep for tag and reflection references after any rename.**
  - gopls Rename only guards against _compilation_ breakage — it cannot see a struct tag, a `text/template` field reference, or a `reflect`-driven dispatch that still points at the old name.
  - Renaming a field silently desyncs it from its `json`/`db` tag.
- **Load `samber/cc-skills-golang@golang-security` (and `golang-safety` for internal-correctness risk) whenever a step changes code logic, not just its shape.**
  - A mechanical, tool-verified transform can't introduce a vulnerability, but a behavioral change can.
  - Treat "changes what the code does" as the trigger for a security-and-safety pass, not an afterthought reserved for the final review.
- **Start every step from a clean, committed baseline, and revert rather than debug forward when it goes red.**
  - Version control is the safety net underneath the test safety net.
  - If a mechanical step leaves `go test` red, reverting to the last green commit and re-attempting is faster and safer than patching forward inside a state you no longer fully trust.
  - Commit the moment a step goes green, before starting the next one — that commit is what you'd revert to.

## When Not to Refactor

Refactoring is an investment that only pays off if a future change is coming to spend it on. Question it — or skip it — when:

- **The code works and nothing planned will touch it again.**
  - A stable, rarely-read package earns nothing from being restructured for its own sake.
  - The risk of even a small staged refactor has to be repaid by an easier next change, and there may not be one.
- **It's critical production code with no tests.** Don't refactor it directly.
  - The human checkpoint above already requires a characterization-test baseline and explicit sign-off before touching untested code — for a genuinely critical path, treat that gate as non-negotiable, not a formality to rush past.
- **The deadline is tight.**
  - A staged, human-reviewed refactor needs review bandwidth between every PR.
  - Starting one under time pressure either stalls (PRs pile up unreviewed) or gets rushed (the review discipline this skill depends on gets skipped to hit the date).
  - Make the minimal safe change now and stage the larger refactor for when there's room for it.
- **There's no clear purpose.**
  - "Refactor this" with no reason behind it — no upcoming feature it'll make easier, no bug class it'll close off, no smell a review actually flagged — is refactoring for its own sake.
  - Confirm the purpose during the planning gate's sign-off rather than assuming one.

## Risk Stratification

| Risk | Transforms | Safety requirement |
| --- | --- | --- |
| **Low** | gopls Rename, Extract Variable/Constant, Inline Variable, `gofmt -s`, organize imports, local `refactor.rewrite.*` actions | Build/vet/test after the step is enough |
| **Medium** | Extract Function/Method (Extract is best-effort — verify comments/behavior survived), Inline Call across packages, single-parameter add/remove, introducing generics | Add or confirm targeted tests over the blast radius first |
| **High** | Change signature across many callers, moving types/functions across packages, splitting/merging packages, breaking import cycles, exported-API or major-version changes | Full safety net + human checkpoint before landing |

**Diagnose:** 1- gopls refusing a Rename or Inline is a real semantic hazard, not a tool bug — investigate the shadowing/interface conflict before forcing the change by hand 2- `go vet ./...` / `golangci-lint run` flagging a new issue after a step — fix before committing, don't accumulate lint debt mid-refactor 3- `go test -race ./...` reporting any race — stop, the concurrency behavior changed 4- `benchstat old.txt new.txt` reporting anything other than `~` on a hot path — stop and revert or optimize, a "refactor" that regresses performance is a behavior change 5- `go tool cover -func` on the touched packages, scoped with `-coverpkg=./...` — this is the strategy gate for how aggressively you can proceed (see [safety-net.md](references/safety-net.md))

## Workflow: Plan → Stage → Land

- A refactor of any real size does not land as one commit or even one PR — it lands as an ordered sequence of small, independently reviewable PRs, staged on a refactoring branch, with a human approving each merge.
- [workflow.md](references/workflow.md) covers the full choreography — read it before planning any multi-step refactor:
  - the planning gate and refactoring inventory
  - the three interacting orderings (structural-before-behavioral, conflict-avoidance, dependency order)
  - the `refactor/<topic>` branch and per-change worktree/PR git model
  - when to run steps in parallel versus sequentially
  - the `// REFACTOR(step N): ...` marker convention
  - why Workflows/`ultracode` are the wrong tool for this

## Detailed References

- **[workflow.md](references/workflow.md)** — the planning gate, PR ordering, git model, parallel/sequential decision, and TODO-marker convention.
- **[catalog.md](references/catalog.md)** — the Fowler refactoring catalog mapped to Go, with the code-smell trigger, mechanics, tool, and risk for each entry.
- **[go-tooling.md](references/go-tooling.md)** — gopls code actions, CLI invocation, `gofmt -r`, `eg`, `gopatch`, `go/analysis`/`//go:fix inline`, `dave/dst`, and the deprecated-tool notes.
- **[safety-net.md](references/safety-net.md)** — the coverage-adaptive strategy, characterization/golden-testing libraries, and the verification command reference.
- **[structural.md](references/structural.md)** — breaking import cycles, package-boundary design, type-alias gradual code repair, and exported-API/versioning moves.

## Cross-References

- → See `samber/cc-skills-golang@golang-naming` skill for what to rename identifiers _to_ — this skill owns _how_ to apply a rename safely at scale.
- → See `samber/cc-skills-golang@golang-project-layout` skill for target directory/package layout — this skill owns the mechanics of moving code there without breaking callers.
- → See `samber/cc-skills-golang@golang-modernize` skill for version-driven idiom updates (`interface{}`→`any`, `slices`/`maps`) — a distinct concern from structural refactoring, though it shares the same tool-first discipline.
- → See `samber/cc-skills-golang@golang-code-style` skill for control-flow clarity and function-shape rules this skill helps you apply mechanically.
- → See `samber/cc-skills-golang@golang-design-patterns` skill for target patterns (options struct, DI, consumer-side interfaces) this skill helps you migrate toward.
- → See `samber/cc-skills-golang@golang-testing` skill for the test-writing practices that make the safety net in this skill trustworthy.
- → See `samber/cc-skills-golang@golang-lint` skill for configuring `golangci-lint`, run here only as a post-step verification gate.
- → See `samber/cc-skills-golang@golang-security` skill (and `golang-safety`) for reviewing any step that changes code logic, not just its shape.

If you encounter a bug or unexpected behavior in `gopls`, open an issue at <https://github.com/golang/go/issues>.
