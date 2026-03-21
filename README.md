# Claude Code Skills for production-ready Golang projects

AI agent skills are reusable instruction sets that extend your coding assistant with domain-specific expertise — loaded on demand so they don't bloat your context. This repository covers **Go-specific** skills only (language, testing, security, observability, etc.); for dev workflow skills (git conventions, CI/CD, PR reviews) you'll want to add a separate skills plugin.

For generic skills, please visit [cc-skills](https://github.com/samber/cc-skills).

## 🚀 How to use

- **Fork it** to adapt the skills to your own company conventions (not recommended: [reference](#-overlap) this skill instead)
- **Copy-paste it** to create your own skills based on this repository (not recommended)
- **Install it** with the [skills CLI](https://skills.sh) or a tool-specific method below

**Install with [skills](https://skills.sh/) CLI** (universal — works with any [Agent Skills](https://agentskills.io)-compatible tool):

```bash
npx skills add https://github.com/samber/cc-skills-golang
# or a single skill:
npx skills add https://github.com/samber/cc-skills-golang --skill golang-performance
```

<!-- prettier-ignore-start -->

<details>
<summary>Claude Code</summary>

```bash
/plugin marketplace add samber/cc
/plugin install cc-skills-golang@samber
```

</details>

<details>
<summary>Openclaw</summary>

Copy skills into the cross-client discovery directory:

```bash
git clone https://github.com/samber/cc-skills-golang.git ~/.openclaw/skills/cc-skills-golang
# or in workspace:
git clone https://github.com/samber/cc-skills-golang.git ~/.openclaw/workspace/skills/cc-skills-golang
```

</details>

<details>
<summary>Gemini CLI</summary>

```bash
gemini extensions install https://github.com/samber/cc-skills-golang
```

Update with `gemini extensions update cc-skills-golang`.

</details>

<details>
<summary>Cursor</summary>

Copy skills into the cross-client discovery directory:

```bash
git clone https://github.com/samber/cc-skills-golang.git  ~/.cursor/skills/cc-skills-golang
```

Cursor auto-discovers skills from `.agents/skills/` and `.cursor/skills/`.

</details>

<details>
<summary>Copilot</summary>

Copy skills into the cross-client discovery directory:

```bash
/plugin install https://github.com/samber/cc-skills-golang
# or
git clone https://github.com/samber/cc-skills-golang.git ~/.copilot/skills/cc-skills-golang
```

Copilot auto-discovers skills from `.copilot/skills/`.

</details>

<details>
<summary>OpenCode</summary>

Copy skills into the cross-client discovery directory:

```bash
git clone https://github.com/samber/cc-skills-golang.git ~/.agents/skills/cc-skills-golang
```

OpenCode auto-discovers skills from `.agents/skills/`, `.opencode/skills/`, and `.claude/skills/`.

</details>

<details>
<summary>Codex (OpenAI)</summary>

Clone into the cross-client discovery path:

```bash
git clone https://github.com/samber/cc-skills-golang.git ~/.agents/skills/cc-skills-golang
```

Codex auto-discovers skills from `~/.agents/skills/` and `.agents/skills/`. Update with `cd ~/.agents/skills/cc-skills-golang && git pull`.

</details>

<details>
<summary>Antigravity</summary>

Clone and symlink into the cross-client discovery path:

```bash
git clone https://github.com/samber/cc-skills-golang.git ~/.antigravity/skills/cc-skills-golang
```

Update with `cd ~/.antigravity/skills/cc-skills-golang && git pull`.

</details>

<!-- prettier-ignore-end -->

## 🧩 Skills

These skills are designed as **atomic, cross-referencing units**. A skill may reference conventions defined in another (e.g. error-handling rules that affect logging live in `golang-error-handling`, not `golang-observability`). Installing only a subset will give you a partial — and potentially inconsistent — view of the guidelines. For best results, install all general-purpose skills together.

Each skill lives in `skills/<name>/` with a `SKILL.md` entry point. The `SKILL.md` is kept small with internal references to advanced markdown files, so only the relevant content is loaded into context.

- **Description (tok)** — weight of the `description` field from YAML frontmatter, always loaded into Claude's context for skill triggering
- **SKILL.md (tok)** — weight of the full `SKILL.md` file loaded when the skill triggers
- **Directory (tok)** — weight of all files in the skill directory (SKILL.md + referenced markdown files)

Skills marked with ⭐️ are recommended as a starting point for most Go projects.

**General purpose:**

|  | Skill | Name | Cmd | Ultrathink | Overridable | Error rate gap | Description (tok) | SKILL.md (tok) | Directory (tok) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ⭐️ | ✅ Code style | `golang-code-style` |  |  | ⚙️ | -40% | 31 | 2,028 | 2,644 |
| ⭐️ | ✅ Data structures | `golang-data-structures` |  |  |  | -39% | 92 | 2,420 | 6,132 |
| ⭐️ | ✅ Database | `golang-database` |  |  | ⚙️ | -38% | 112 | 2,681 | 7,166 |
| ⭐️ | ✅ Design patterns | `golang-design-patterns` |  |  | ⚙️ | -37% | 66 | 2,567 | 9,273 |
| ⭐️ | ✅ Documentation | `golang-documentation` | ⚡ |  | ⚙️ | -53% | 73 | 2,636 | 10,507 |
| ⭐️ | ✅ Error handling | `golang-error-handling` |  |  | ⚙️ | -26% | 90 | 1,477 | 4,351 |
| ⭐️ | 👷 How-to | `golang-how-to` |  |  |  | — | 0 | 0 | 0 |
| ⭐️ | ✅ Modernize | `golang-modernize` | ⚡ |  |  | -61% | 113 | 2,434 | 7,557 |
| ⭐️ | ✅ Naming | `golang-naming` |  |  | ⚙️ | -23% | 158 | 2,822 | 7,190 |
| ⭐️ | ✅ Safety | `golang-safety` |  |  |  | -58% | 85 | 2,413 | 5,183 |
| ⭐️ | ✅ Testing | `golang-testing` | ⚡ | 🧠 | ⚙️ | -32% | 98 | 3,028 | 6,135 |
| ⭐️ | ✅ Troubleshooting | `golang-troubleshooting` | ⚡ | 🧠 |  | -32% | 106 | 2,633 | 15,799 |
| ⭐️ | ✅ Security | `golang-security` | ⚡ | 🧠 |  | -32% | 84 | 2,790 | 20,811 |
|  | ✅ Benchmark | `golang-benchmark` | ⚡ | 🧠 |  | -50% | 92 | 2,030 | 29,114 |
|  | ✅ CLI | `golang-cli` |  |  |  | -43% | 73 | 2,232 | 6,047 |
|  | ✅ Concurrency | `golang-concurrency` |  |  | ⚙️ | -39% | 71 | 1,831 | 6,296 |
|  | ✅ Context | `golang-context` |  |  | ⚙️ | -34% | 41 | 1,102 | 3,898 |
|  | ✅ Continuous integration | `golang-continuous-integration` | ⚡ |  |  | -59% | 105 | 2,745 | 6,387 |
|  | ✅ Dependency injection | `golang-dependency-injection` |  |  | ⚙️ | -47% | 104 | 2,800 | 5,071 |
|  | ✅ Dependency management | `golang-dependency-management` |  |  |  | -54% | 94 | 1,794 | 4,874 |
|  | ✅ Structs & interfaces | `golang-structs-interfaces` |  |  | ⚙️ | -35% | 110 | 2,956 | 2,956 |
|  | ✅ Linter | `golang-linter` |  |  |  | -41% | 119 | 1,639 | 5,418 |
|  | ✅ Observability | `golang-observability` | ⚡ |  | ⚙️ | -37% | 144 | 2,851 | 18,358 |
|  | ✅ Performance | `golang-performance` | ⚡ | 🧠 |  | -39% | 108 | 1,876 | 17,746 |
|  | ✅ Popular libraries | `golang-popular-libraries` |  |  |  | -30% | 61 | 746 | 4,089 |
|  | ✅ Project layout | `golang-project-layout` | ⚡ |  |  | -38% | 66 | 1,468 | 5,676 |
|  | ✅ Stay up to date | `golang-stay-updated` |  |  |  | -56% | 43 | 1,874 | 1,874 |

**Tools:**

| Skill | Name | Cmd | Ultrathink | Error rate gap | Description (tok) | SKILL.md (tok) | Directory (tok) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ❌ google/wire | `golang-google-wire` |  |  | — | 0 | 0 | 0 |
| ❌ GraphQL | `golang-graphql` |  |  | — | 0 | 0 | 0 |
| ✅ gRPC | `golang-grpc` |  |  | -41% | 69 | 2,086 | 4,902 |
| ❌ spf13/cobra | `golang-spf13-cobra` |  |  | — | 0 | 0 | 0 |
| ❌ spf13/viper | `golang-spf13-viper` |  |  | — | 0 | 0 | 0 |
| ❌ swaggo/swag | `golang-swagger` |  |  | — | 0 | 0 | 0 |
| ❌ uber-go/dig | `golang-uber-dig` |  |  | — | 0 | 0 | 0 |
| ❌ uber-go/fx | `golang-uber-fx` |  |  | — | 0 | 0 | 0 |
| ✅ samber/do | `golang-samber-do` |  |  | -81% | 70 | 1,704 | 3,227 |
| ❌ samber/hot | `golang-samber-hot` |  |  | — | 0 | 0 | 0 |
| ❌ samber/lo | `golang-samber-lo` |  |  | — | 0 | 0 | 0 |
| ❌ samber/mo | `golang-samber-mo` |  |  | — | 0 | 0 | 0 |
| ✅ samber/oops | `golang-samber-oops` |  |  | -59% | 69 | 2,338 | 2,650 |
| ❌ samber/ro | `golang-samber-ro` |  |  | — | 0 | 0 | 0 |
| ❌ samber/slog | `golang-samber-slog` |  |  | — | 0 | 0 | 0 |
| ❌ temporal | `golang-temporal` |  |  | — | 0 | 0 | 0 |
| ✅ stretchr/testify | `golang-stretchr-testify` |  |  | -47% | 89 | 1,641 | 2,460 |

Token counts are measured with `npm exec -- tiktoken-cli --exclude "evals" skills/{name}/`. Description tokens extracted with:

```bash
awk 'NR==1 && /^---$/{found=1; next} found && /^---$/{exit} found && /^description:/{print}' skills/<name>/SKILL.md | npx tiktoken-cli
```

## 🧪 Skill evaluations

|             | With Skill          | Without Skill       | Delta     |
| ----------- | ------------------- | ------------------- | --------- |
| **Overall** | **2823/2895 (97%)** | **1574/2895 (54%)** | **+43pp** |

See [EVALUATIONS.md](./EVALUATIONS.md) for the full per-skill breakdown.

## 🎯 Tuning Skill Triggers

If a skill triggers too often or not often enough, please [open an issue](https://github.com/samber/cc-skills-golang/issues) suggesting a description change. The `description` field in SKILL.md frontmatter is the primary triggering mechanism — small wording adjustments can significantly improve trigger accuracy. Some `SKILL.md` might have `When to use` section which is another level of exclusion. Finally, `SKILL.md` are a entrypoint for lazy loading references with deep knowledge located in `references/`.

## 🔄 Overlap

Claude reports very little overlap between skills in this repo, thanks to cross-reference. I suggest enabling most of the skills and leverage lazy loading. The recommended ⭐️ skills load ~1,100 tokens of descriptions at startup; full skill content is only pulled in when relevant. Note:

- I estimate that 50% of `golang-naming` and `golang-code-style` overlap with linters (golangci-lint).
- A large part of the security rules in `golang-security` have been distilled from Bearer (SAST) check list. The skill is still useful for methodology.
- If your team has its own conventions, create a company skill and declare the override explicitly near the top of its body: `"This skill supersedes \`samber/cc-skills-golang@golang-naming\` skill for [company] projects."` Skills marked ⚙️ in the table above support this mechanism.

## ✍️ Contribute

- **100 tokens per skill description** - what ? when use this skill ?
- **1.000–2.500 tokens per SKILL.md** — keep the main file focused on essentials
- **Use secondary markdown files for depth** — reference them from SKILL.md with relative links (e.g., `[Logging](./logging.md)`). Claude reads these on demand when the topic is relevant, so they don't count against the context budget until needed
- **Up to 10.000 tokens** for full skill and secondary files
- **2–4 skills loaded simultaneously** in a typical session — design skills to coexist
- **Stay below ~10k tokens of total loaded SKILL.md** anytime to avoid degrading response quality

For more guidelines, please check `CLAUDE.md`.

## 💫 Fuel the Revolution

- ⭐️ **Star this repo** - Your star powers the caffeine engine!
- ☕️ **Buy me a coffee** - I'll literally use it to build more skills while drinking actual coffee

[![GitHub Sponsors](https://img.shields.io/github/sponsors/samber?style=for-the-badge)](https://github.com/sponsors/samber)

## 📝 License

Copyright © 2026 [Samuel Berthe](https://github.com/samber).

This project is under [MIT](./LICENSE) license.
