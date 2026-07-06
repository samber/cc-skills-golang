# Refactoring Workflow — Plan, Stage, Land

- A refactor of any real size is a choreography problem before it is a coding problem.
- This file covers: how to plan the sequence, order the steps so they don't collide, stage them as small human-reviewed PRs, and persist the plan itself — in the code, not just in a conversation that will eventually run out of context — for the intermediate states that are deliberately imperfect and for the ideas that would otherwise be lost.

## 1. The Planning Gate (mandatory, before any edit)

**Thinking mode:** use `ultrathink` here. A wrong ordering call does not surface as an obviously wrong plan — it surfaces later as a broken build or a conflict-riddled merge, once several PRs are already in flight. Getting the sequencing right up front is cheaper than untangling it after the fact.

- Before touching a single line of code, map the blast radius with gopls:
  - find every reference to the symbols you intend to change
  - walk the call hierarchy in both directions
  - check the package's exported API surface for anything an external module might depend on
- Workspace symbol search and `gopls codeaction` surface the mechanical options available at each site — its day-to-day mechanics (rename, browsing references, call hierarchy) are owned by the `samber/cc-skills-golang@golang-gopls` skill.

Once the blast radius is mapped, turn it into a **refactoring inventory** — one row per atomic change, so the whole refactor is visible as a single artifact before any PR exists:

| Transform | Files / callers touched | Risk | S/B |
| --- | --- | --- | --- |
| Extract `validateOrder` from `ProcessOrder` | `internal/orders/process.go` (1 file, no external callers) | Low | S |
| Rename `Client.Send` → `Client.Publish` | `pkg/client/*.go`, 14 call sites across 3 packages | Low | S |
| Break import cycle `billing` ↔ `orders` via consumer-side interface | `internal/billing/service.go`, `internal/orders/service.go` | High | S |
| Move `Invoice` type to `pkg/billing`, alias from old location | `internal/orders/invoice.go` → `pkg/billing/invoice.go`, ~9 call sites | High | S |
| Replace `Invoice.Total`'s O(n²) discount-lookup loop with a map lookup | `pkg/billing/invoice.go` | Medium | S |
| Switch `Invoice.Total` computation to Decimal instead of float64 | `pkg/billing/invoice.go` and its tests | Medium | B |

- Risk tiers match the Risk Stratification table in `SKILL.md` (Low/Medium/High).
- The **S/B** column marks each row Structural or Behavioral in Kent Beck's sense — a change that alters code shape without altering observable behavior versus a change that alters what the code does.
- **Never let one PR carry both letters.** A rename and a bug fix touching the same function are two rows, two PRs, two review postures.
- The same one-row-one-concern discipline holds even within a single letter:
  - the move and the loop-optimization rows above are both marked S, but they still earn two separate rows and two sequential PRs
  - a move is verified by gopls plus a green build/test run, while an optimization needs benchmarks (→ See `samber/cc-skills-golang@golang-benchmark` skill) and a closer read for subtle correctness changes
  - bundling them asks one reviewer to do both jobs at once and denies the move the fast review it earns on its own
  - they also touch the same file, so Ordering (b) below puts them in sequence regardless — never split a move-then-optimize pair across parallel worktrees
- The inventory is not busywork — it is the object every later ordering decision is computed from, and it is what you show the human for sign-off.

**This step ends with explicit user sign-off before any code is touched.** This is a hard gate, not a suggestion: present the inventory and the staged PR plan derived from it (see below), and wait for approval. A refactor that starts moving code before the human has seen the shape of the whole plan cannot be course-corrected cheaply — by the time a wrong assumption surfaces, several PRs may already be staged on top of it.

## 2. Three Interacting Orderings

Once the inventory is approved, three independent ordering concerns combine to produce the final sequence. Each answers a different question, and a plan that gets one right while ignoring the others still fails.

| Ordering | Question it answers | Why it matters |
| --- | --- | --- |
| **(a) Beck ordering** | Within a dependency chain, does this row change structure or behavior? | Structural first, behavioral last. `git blame` stays meaningful — the last change touching a line is the one a future reader actually needs to understand, not an incidental rename that happened to pass through. It also lets reviewers wear one hat at a time: a structural PR gets a fast, low-scrutiny pass (is this reversible? did tests stay green?), a behavioral PR gets full scrutiny (does this do the right thing?). Mixing the two forces every reviewer into both postures on every PR. |
| **(b) Conflict-avoidance ordering** | Do two rows touch the same files or the same symbols/callers? | PRs sharing files or symbols must land sequentially — one merges to the refactoring branch before the next starts — or the second PR is rebasing against a moving target for its whole review cycle. PRs that are file-disjoint can run in parallel worktrees with no coordination cost. |
| **(c) Dependency ordering** | Does this row require structural groundwork from another row first? | Breaking an import cycle, extracting a shared package, or introducing a type alias for a cross-package move are prerequisites, not peers — you cannot move a function into a package that would still form a cycle. These rows must land before anything that assumes the groundwork is already there. |

- **A workspace-wide gopls rename is a barrier.**
  - Because it rewrites every reference to a symbol across the whole tree, it necessarily touches files that any other in-flight change might also touch — there is no way to know in advance that it is file-disjoint from everything else in the inventory.
  - Schedule it alone: land every other ready PR before it starts, or hold every other PR until it lands.
  - Do not attempt to run a tree-wide rename concurrently with anything else, even a change that looks unrelated.

### Parallel vs. sequential — decision checklist

Run this checklist for every pair of inventory rows you're considering executing at the same time:

| Question | If yes |
| --- | --- |
| Do the two changes touch the same file? | Sequential |
| Do they touch the same symbol, or one's callers overlap the other's? | Sequential |
| Does one depend on structural groundwork the other lands (cycle break, extracted package, alias)? | Sequential — groundwork first |
| Is either change a workspace-wide rename? | Sequential — the rename runs alone |
| None of the above | Safe to parallelize in separate worktrees |

If any answer is yes, the two rows are sequential. Only when every answer is no is it safe to run them concurrently.

## 3. The Git Model

- This is a deliberate, explicit choice for staged refactors — not the only way to refactor, and not necessarily how every Go team runs things day to day.
- Many teams instead land small, independent PRs directly on a fast-moving trunk, treating each one as complete and shippable on its own. That works well when changes are truly independent.
- The model below is chosen here because a _staged_ refactor is not a set of independent changes — it is one coherent transformation broken into reviewable steps, and it needs a place to accumulate before the whole thing is ready to expose to `main`.
- Reviewability and a human-in-the-loop checkpoint on every step are the tradeoff being made; the cost is an extra integration branch and a final merge step.

The shape:

1. Create a long-lived `refactor/<topic>` branch off `main`, and seed it with `// REFACTOR(step N): ...` markers for the plan itself — see Step 5.
2. For each atomic change in the inventory, in the order established in Step 2, **dispatch it to a sub-agent via the `Agent` tool** rather than executing it directly in the orchestrating session. The sub-agent, scoped to a fresh worktree, does the work:
   - Enter a fresh worktree with `EnterWorktree`.
   - Create a branch for that one change, based on the current tip of `refactor/<topic>`.
   - Apply the single change — and nothing else. If the inventory row is turning out larger than **~100–500 lines**, that's a signal it's actually two rows: split it before it grows into a diff nobody can review in one sitting.
   - Verify: `go build ./... && go vet ./... && go test ./...` (add `-race` or `benchstat`-backed `-bench` per the Risk Stratification table in `SKILL.md`).
     - A staged refactor produces many small PRs in sequence, so weigh the project's actual CI duration against the pace of the refactor: if CI is slow enough that waiting on it between steps would meaningfully stall the sequence — a few minutes is rarely worth front-loading, but a pipeline that takes much longer, repeated across many staged PRs, adds up fast — run the same checks locally first and let CI serve as the final confirmation rather than the primary feedback loop.
     - If CI is already fast, there's no need to duplicate it locally.
   - Open a **PR targeting the refactoring branch**, not `main` — ready for review, not a draft, since the whole point of staging is for the human to review and merge it promptly:

     ```bash
     gh pr create --base refactor/<topic> --title "..." --body "..."
     ```

   - The orchestrating session's own context is the scarcest resource across a long refactor — spending it on every intermediate edit, failed attempt, and tool-output while executing one row leaves less of it for tracking the other rows still ahead and for the ordering decisions in Step 2.
   - Have the sub-agent report back a short result (pass/fail, verification output, PR link) and keep that in the orchestrating session's context — not the sub-agent's full working transcript.
3. A human reviews and merges each of these small PRs into `refactor/<topic>` at their own pace.
   - Structural PRs should move fast; behavioral PRs get full scrutiny (see Beck ordering above).
   - For any PR that changes code logic rather than just its shape, load `samber/cc-skills-golang@golang-security` (and `golang-safety` for internal-correctness risk) alongside this skill before approving it, since a logic change can introduce a vulnerability or a bug that a purely mechanical refactor never could.
4. Only once every row in the inventory has landed on `refactor/<topic>` — and the TODO-marker sweep in Step 5 is clean — open the **final PR** merging `refactor/<topic>` into `main`, and open this one **as a draft**: unlike the intermediate PRs, it represents the whole completed transformation and deserves a slower, more deliberate final look before it's marked ready.

**Never merge an intermediate PR directly to `main`.** The refactoring branch is the integration point for the entire duration of the refactor; `main` only ever sees the whole, completed transformation in one final merge. An intermediate PR landing directly on `main` defeats the purpose of staging — it exposes a deliberately incomplete state (aliases still in place, shims not yet removed) to every other branch built off `main` in the meantime.

## 4. Parallel vs. Sequential Execution

- When multiple inventory rows are ready — their dependency-order prerequisites have landed, and the checklist in Step 2 says "no" on every question — launch them concurrently, one sub-agent per row, each in its own worktree, its own branch off the current tip of `refactor/<topic>`, and its own PR.
  - This is where a large refactor's wall-clock time actually shrinks: three file-disjoint structural changes reviewed at once cost the same calendar time as one — and the orchestrating session still only keeps three short results, not three full working transcripts.
- When rows overlap — same file, same symbol, or a dependency relationship — run them one at a time: land the first on `refactor/<topic>` before branching the second off the new tip.
  - Trying to parallelize overlapping rows just moves the conflict from merge time to rebase time, and a human reviewer now has to untangle a diff that mixes two unrelated changes.
- The workspace-wide-rename-is-a-barrier rule from Step 2 applies here without exception: never schedule a tree-wide rename alongside any other in-flight worktree, regardless of how unrelated the files look on paper.

## 5. The `// REFACTOR(step N): ...` Marker Convention

The marker has two jobs, and the first matters more than it looks.

- **Job 1 — surviving context loss.** A multi-step refactor eats context fast:
  - it can span many sessions, and each new session (or a different agent picking up the work) starts with a fresh, limited context window that has no memory of the planning conversation
  - a conversation is a bad place to keep a plan safe; the codebase, committed to the refactoring branch, is not
  - so right when you create `refactor/<topic>` (Step 3), before any change lands, seed it liberally with markers at every point the inventory identifies future work, an idea worth not losing, or a decision that won't be obvious from a later diff — not only at points of deliberate imperfection
  - a marker survives exactly the kind of context loss a plan that only ever existed in conversation does not
  - **Skip this for a small refactoring.** A single-PR change, or the simple mechanical sweep in Section 6, doesn't have a plan large enough to be worth losing — seeding markers there is noise, not insurance. Reserve liberal marker-seeding for staged, multi-PR refactors, where the plan is genuinely too large to trust to any one session's memory.
- **Job 2 — flagging deliberate imperfection.** A staged refactor will, by design, pass through intermediate states that are imperfect on purpose — a type alias kept around so callers can migrate one PR at a time, a shim left in place until a later step removes it, an old code path still reachable until its last caller is gone.
  - **This is fine and expected.** The risk isn't the imperfection — it's forgetting about it once the PR that introduced it has merged and attention has moved on.

Mark every such spot — a plan note or a deliberate imperfection — with a comment that names the step and the reason:

```go
// REFACTOR(step 3): remove this alias once all callers in pkg/foo migrate to bar.New (see refactor/<topic>)
```

- Each marker earns its place twice over: it tells a reviewer looking at _this_ PR that the current state is intentional, not an oversight, and it hands context forward — to whichever later step, later PR, or entirely different agent session eventually acts on it — about exactly what is pending and why.
- Without it, a shim that "temporarily" bridges old and new callers has a way of becoming permanent simply because nothing points back at it, and an idea from the planning gate has a way of vanishing the moment the session that had it ends.

The **final sweep**, run just before opening the PR that merges `refactor/<topic>` into `main`, must find zero remaining markers:

```bash
grep -rn "REFACTOR(" .
```

**Diagnose:** `grep -rn "REFACTOR(" .` — must return no results before the final merge to `main`; any hit means a planned step never landed, and the refactor is not actually done even though every individual PR merged cleanly.

## 6. Workflows (`ultracode`) vs. Human-in-the-Loop

- Claude Code's Workflow feature (`ultracode`) orchestrates multiple sub-agents across multiple stages automatically, with no human checkpoint between them.
- That is exactly the wrong shape for a staged refactor, whose entire value proposition is a human reviewing and merging each small PR _before_ the next step is allowed to build on it.
- Running a multi-step refactor through Workflows collapses the review checkpoints this whole document exists to preserve — by the time a human looks at anything, several dependent stages may have already executed on top of a decision nobody signed off on.
- Reach for Workflows/`ultracode` only when the refactor is genuinely a **single mechanical sweep in one pass** — one `gofmt -r` rule, one `eg` template, or one `modernize`-style fixer applied tree-wide, verified green by the build/vet/test loop, with nothing else in the inventory depending on it.
  - That case has no staging problem to begin with: there is exactly one step, and it either lands or it doesn't.
- For anything requiring progressive review across multiple merges — which is the common case for a real refactor — use the worktree + PR + human-review flow in Steps 3 and 4 instead, and do not reach for Workflows.

## 7. Human Checkpoints

Pause and get explicit sign-off before proceeding past any of the following, even mid-refactor after the planning gate has already been cleared once:

- Any cross-package move or package split.
- Any exported-API change or deprecation.
- Any deletion of code, especially anything that might still have external callers you haven't found.
- Introducing a new major version (`/vN`).
- Touching code that has no tests — get sign-off on the characterization-test baseline (see [safety-net.md](safety-net.md)) before refactoring it, not after.

Structural-only PRs are reversible and low-risk by construction (Beck's separation is the whole reason they're safe to move fast on) and can be fast-reviewed. Behavioral PRs — anything that changes what the code does, not just how it's shaped — get full scrutiny every time, regardless of how small the diff looks.

## Cross-References

- [catalog.md](catalog.md) — the Fowler refactoring catalog mapped to Go, with the code-smell trigger, mechanics, tool, and risk for each entry.
- [go-tooling.md](go-tooling.md) — gopls code actions, CLI invocation, `gofmt -r`, `eg`, `gopatch`, and `go/analysis` fixers referenced throughout the inventory examples above.
- [safety-net.md](safety-net.md) — the coverage-adaptive strategy and characterization-testing recipes referenced in the Human Checkpoints section.
- [structural.md](structural.md) — import-cycle breaking, package-boundary design, and the type-alias gradual-repair mechanism referenced in the inventory example above.
- → See `samber/cc-skills-golang@golang-security` skill (and `golang-safety`) for reviewing any PR that changes code logic, per Step 3 above.
