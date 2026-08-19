# Configure mode — force-trigger Go skills in a project

This workflow writes two independent things to the project's agent-config file(s) (CLAUDE.md, AGENTS.md, or equivalent):

1. An **always-load directive** for `golang-how-to` itself — a single sentence, unconditional, no user confirmation needed.
2. An optional `## Required Go skills` block that force-triggers a specific, user-confirmed set of secondary skills.

## When to use

- Any new Go project should get the always-load directive (see below) — this is the common case.
- The project additionally has a hard requirement on specific skills (e.g., `golang-security` must always apply, not just when the user mentions "security").
- The team has agreed on a fixed set of Go standards to enforce on every AI interaction.
- A company skill overrides a community default (⚙️ skills) and must always win.

## Always-load directive

Every Go project should carry a one-line directive telling the coding agent to load the `samber/cc-skills-golang@golang-how-to` orchestrator skill before starting Go work, so it in turn routes to whichever other Go skills the task actually needs. Unlike the `## Required Go skills` block below, this directive needs no user confirmation: it costs one skill description (~100 tokens) and is never wrong, since `golang-how-to` only routes to other skills — it does not impose project-specific choices.

### Template

```markdown
Before any Go coding, review, debugging, troubleshooting, or setup task, load the `samber/cc-skills-golang@golang-how-to` skill first — it routes to whichever other Go skills the task needs.
```

### When it gets written

- **At project creation** — the `samber/cc-skills-golang@golang-project-layout` skill writes this directive automatically as part of its Initialization Checklist, without asking the user.
- **On demand** — running `/golang-how-to configure` writes it too (if missing), in addition to any `## Required Go skills` block confirmed in Step 3 below.

### Insertion point

- If a `## Required Go skills` block already exists or is being created in the same pass, insert the directive as its own line directly above that heading, separated by a blank line.
- Otherwise, append it under a `## Go development` heading (create the heading if the file has no such section).

### Idempotency

Grep for the exact sentence before writing:

```bash
grep -n 'load the `samber/cc-skills-golang@golang-how-to` skill first' CLAUDE.md
```

Skip writing if already present.

## Step 1 — Detect the project config file(s)

Every harness reads its own agent-config file or directory. None is more "primary" than another — detect and write to whichever exist, and write to all of them if more than one does:

| File / directory | Harness(es) | Format |
| --- | --- | --- |
| `CLAUDE.md` | Claude Code | Markdown, single file, appended to |
| `AGENTS.md` | Codex, OpenCode, and other multi-agent harnesses | Markdown, single file, appended to |
| `GEMINI.md` | Gemini CLI, Antigravity | Markdown, single file, appended to |
| `.cursor/rules/*.mdc` | Cursor | **Directory** of `.mdc` files, each with its own YAML frontmatter — not a single markdown file to append to |
| `.github/copilot-instructions.md` | GitHub Copilot | Markdown, single file, appended to |

Check which of these exist at the project root. If multiple exist, write to all of them — different harnesses read different files, and a project may support several. If none exist, ask the user which one(s) to create.

## Step 2 — Idempotency check

For the markdown files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.github/copilot-instructions.md`), grep each one for the always-load directive and an existing `## Required Go skills` block before writing:

```bash
grep -n 'load the `samber/cc-skills-golang@golang-how-to` skill first' CLAUDE.md
grep -n "## Required Go skills" CLAUDE.md
```

For Cursor, check whether `.cursor/rules/golang-skills.mdc` already exists instead — its presence itself is the idempotency signal, since it's a dedicated file rather than a shared section inside a larger document.

Write the always-load directive if it's missing, regardless of what Step 3 decides. If a `## Required Go skills` block (or, for Cursor, the rule file) already exists, read it and confirm with the user whether to update it in place (replace the existing list) or skip.

## Step 3 — Confirm the skill set with the user

Confirm which skills to always load — one question, one round of confirmation, not a running back-and-forth. Present the ⭐️ recommended skills as the default selection. Remind the user of the token budget (each always-loaded skill adds its description tokens to every session — the 11 recommended skills add ~1,100 tokens at startup).

Recommended ⭐️ set for most projects:

```
golang-code-style
golang-data-structures
golang-design-patterns
golang-documentation
golang-error-handling
golang-modernize
golang-naming
golang-safety
golang-security
golang-testing
golang-troubleshooting
```

Additional skills to suggest based on codebase context:

- Database layer detected (`sql`, `gorm`, `sqlc`) → suggest `golang-database`
- CI config detected (`.github/workflows/`) → suggest `golang-continuous-integration`
- Cobra imports detected → suggest `golang-spf13-cobra`
- Viper imports detected → suggest `golang-spf13-viper`
- samber/lo imports detected → suggest `golang-samber-lo`
- Any other library-specific import → suggest the matching library skill

## Step 4 — Write the block

### Markdown targets (CLAUDE.md, AGENTS.md, GEMINI.md, copilot-instructions.md)

Template:

```markdown
Before any Go coding, review, debugging, troubleshooting, or setup task, load the `samber/cc-skills-golang@golang-how-to` skill first — it routes to whichever other Go skills the task needs.

## Required Go skills

The following Go skills from `samber/cc-skills-golang` MUST always be applied when working on this project. Load them at the start of every Go-related task, regardless of whether the user explicitly mentions them.

- `samber/cc-skills-golang@golang-error-handling`
- `samber/cc-skills-golang@golang-security`
- `samber/cc-skills-golang@golang-testing`
```

Replace the skill list with the confirmed set from Step 3. Use the fully-qualified `samber/cc-skills-golang@<name>` identifier for each skill. If Step 2 found the always-load directive already present elsewhere in the file, don't duplicate it — write only the `## Required Go skills` block.

Insertion point:

- If the file is empty: write the block at the top.
- If the file has existing content: append after the last section, separated by a blank line.
- If a `## Required Go skills` block already exists: replace only the bullet list inside it, preserving surrounding content.

Edit the file directly, rather than shelling out to a script — that keeps the change reviewable as a normal diff. Perform an idempotency check after writing: re-read the file and verify the block appears exactly once.

### Cursor target (`.cursor/rules/*.mdc`)

`.cursor/rules` is a directory, not a file — each rule lives in its own `.mdc` file with YAML frontmatter (`description`, `globs`, `alwaysApply`). Do not try to append to it as if it were a single markdown document; the append-and-replace logic above does not apply here.

Create `.cursor/rules/golang-skills.mdc` (create the `.cursor/rules/` directory first if it doesn't exist) using [cursor-go-skills.mdc](../assets/cursor-go-skills.mdc) as the starting template, with `alwaysApply: true` so it always loads — matching the unconditional behavior of the markdown targets' always-load directive. Replace the placeholder `## Required Go skills` list with the confirmed set from Step 3, same as the markdown targets. If the file already exists, replace only the bullet list, preserving its frontmatter and surrounding content.

## Step 5 — Confirm to the user

After writing, summarize:

- Which file(s) or rule(s) were updated
- Whether the always-load directive for `golang-how-to` was added or was already present
- Which skills were added to the always-load list
- Approximate startup token cost (number of skills × ~100 tokens per description)
- Note: skills marked ⚙️ (overridable) will be superseded if a company skill explicitly declares the override in its body

## Notes on company overrides (⚙️ skills)

Skills marked ⚙️ in the README support company overrides. If the project has a company skill that supersedes a community default (e.g., `acme/cc-skills@golang-error-handling-acme` supersedes `samber/cc-skills-golang@golang-error-handling`), use the company skill FQN in the block instead — do NOT list both.

To declare an override in a company skill body, add near the top:

```
> This skill supersedes `samber/cc-skills-golang@golang-error-handling` for [Company] projects.
```

Overridable skills: `golang-code-style`, `golang-concurrency`, `golang-context`, `golang-database`, `golang-dependency-injection`, `golang-design-patterns`, `golang-documentation`, `golang-error-handling`, `golang-naming`, `golang-observability`, `golang-structs-interfaces`, `golang-testing`.
