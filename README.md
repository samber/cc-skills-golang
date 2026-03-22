# Claude Code Skills for production-ready Golang projects

AI agent skills are reusable instruction sets that extend your coding assistant with domain-specific expertise, loaded on demand so they don't bloat your context. This repository covers **Go-specific** skills only (language, testing, security, observability, etc.); for dev workflow skills (git conventions, CI/CD, PR reviews) you'll want to add a separate skills plugin.

For generic skills, please visit [cc-skills](https://github.com/samber/cc-skills).

<img width="1414" height="491" alt="image" src="https://github.com/user-attachments/assets/620b5835-c1ba-4ea9-bf47-2293b58b879e" />

## 🚀 How to use

**Install with [skills](https://skills.sh/) CLI** (universal, works with any [Agent Skills](https://agentskills.io)-compatible tool):

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

These skills are designed as **atomic, cross-referencing units**. A skill may reference conventions defined in another (e.g. error-handling rules that affect logging live in `golang-error-handling`, not `golang-observability`). Installing only a subset will give you a partial and potentially inconsistent view of the guidelines. For best results, install all general-purpose skills together.

- ⭐️ Recommended
- ✅ Published
- 👷 Work in progress
- ❌ To-do
- ⚡ Command available
- 🧠 Ultrathink automatically
- ⚙️ Overridable (see doc below)
- **Description (tok)** — weight of the `description` field from YAML frontmatter, always loaded into Claude's context for skill triggering
- **SKILL.md (tok)** — weight of the full `SKILL.md` file loaded when the skill triggers
- **Directory (tok)** — weight of all files in the skill directory (SKILL.md + referenced markdown files)

**General purpose:**

|  | Skill | Flags | Error rate gap | Description (tok) | SKILL.md (tok) | Directory (tok) |
| --- | --- | --- | --- | --- | --- | --- |
| ⭐️ | ✅ `golang-code-style` | ⚙️ | -40% | 31 | 2,069 | 2,685 |
| ⭐️ | ✅ `golang-data-structures` |  | -39% | 92 | 2,464 | 6,176 |
| ⭐️ | ✅ `golang-database` | ⚙️ | -38% | 112 | 2,725 | 7,248 |
| ⭐️ | ✅ `golang-design-patterns` | ⚙️ | -37% | 66 | 2,610 | 9,316 |
| ⭐️ | ✅ `golang-documentation` | ⚡ ⚙️ | -53% | 73 | 2,678 | 10,549 |
| ⭐️ | ✅ `golang-error-handling` | ⚙️ | -26% | 90 | 1,520 | 4,394 |
| ⭐️ | 👷 `golang-how-to` |  | — | 0 | 0 | 0 |
| ⭐️ | ✅ `golang-modernize` | ⚡ | -61% | 113 | 2,476 | 7,599 |
| ⭐️ | ✅ `golang-naming` | ⚙️ | -23% | 158 | 2,865 | 7,233 |
| ⭐️ | ✅ `golang-safety` |  | -58% | 85 | 2,457 | 5,227 |
| ⭐️ | ✅ `golang-testing` | ⚡ 🧠 ⚙️ | -32% | 98 | 3,105 | 6,212 |
| ⭐️ | ✅ `golang-troubleshooting` | ⚡ 🧠 | -32% | 106 | 2,735 | 15,901 |
| ⭐️ | ✅ `golang-security` | ⚡ 🧠 | -32% | 84 | 2,873 | 20,894 |
|  | ✅ `golang-benchmark` | ⚡ 🧠 | -50% | 92 | 2,135 | 29,248 |
|  | ✅ `golang-cli` |  | -43% | 73 | 2,274 | 6,089 |
|  | ✅ `golang-concurrency` | ⚙️ | -39% | 71 | 1,873 | 6,338 |
|  | ✅ `golang-context` | ⚙️ | -34% | 41 | 1,144 | 3,940 |
|  | ✅ `golang-continuous-integration` | ⚡ | -59% | 105 | 2,835 | 6,477 |
|  | ✅ `golang-dependency-injection` | ⚙️ | -47% | 104 | 2,842 | 5,113 |
|  | ✅ `golang-dependency-management` |  | -54% | 94 | 1,877 | 4,957 |
|  | ✅ `golang-structs-interfaces` | ⚙️ | -35% | 110 | 2,999 | 2,999 |
|  | ✅ `golang-linter` |  | -41% | 119 | 1,714 | 5,493 |
|  | ✅ `golang-observability` | ⚡ ⚙️ | -37% | 144 | 2,921 | 18,453 |
|  | ✅ `golang-performance` | ⚡ 🧠 | -39% | 108 | 1,953 | 17,855 |
|  | ✅ `golang-popular-libraries` |  | -30% | 61 | 788 | 4,131 |
|  | ✅ `golang-project-layout` | ⚡ | -38% | 66 | 1,510 | 5,718 |
|  | ✅ `golang-stay-updated` |  | -56% | 43 | 1,916 | 1,916 |

**Tools:**

| Skill | Flags | Error rate gap | Description (tok) | SKILL.md (tok) | Directory (tok) |
| --- | --- | --- | --- | --- | --- |
| ❌ `golang-google-wire` |  | — | 0 | 0 | 0 |
| ❌ `golang-graphql` |  | — | 0 | 0 | 0 |
| ✅ `golang-grpc` |  | -41% | 69 | 2,149 | 4,965 |
| ❌ `golang-spf13-cobra` |  | — | 0 | 0 | 0 |
| ❌ `golang-spf13-viper` |  | — | 0 | 0 | 0 |
| ❌ `golang-swagger` |  | — | 0 | 0 | 0 |
| ❌ `golang-uber-dig` |  | — | 0 | 0 | 0 |
| ❌ `golang-uber-fx` |  | — | 0 | 0 | 0 |
| ✅ `golang-samber-do` |  | -81% | 70 | 1,746 | 3,269 |
| ✅ `golang-samber-hot` |  | -54% | 118 | 1,843 | 7,273 |
| ✅ `golang-samber-lo` | 🧠 | -40% | 155 | 2,410 | 10,031 |
| ✅ `golang-samber-mo` | 🧠 | -48% | 81 | 2,800 | 11,215 |
| ✅ `golang-samber-oops` |  | -59% | 69 | 2,380 | 2,692 |
| ✅ `golang-samber-ro` | 🧠 | -50% | 140 | 2,845 | 11,136 |
| ✅ `golang-samber-slog` |  | -19% | 118 | 2,588 | 9,234 |
| ❌ `golang-temporal` |  | — | 0 | 0 | 0 |
| ✅ `golang-stretchr-testify` |  | -47% | 89 | 1,714 | 2,533 |

Token counts are measured with `npm exec -- tiktoken-cli --exclude "evals" skills/{name}/`. Description tokens extracted with:

```bash
awk 'NR==1 && /^---$/{found=1; next} found && /^---$/{exit} found && /^description:/{print}' skills/<name>/SKILL.md | npx tiktoken-cli
```

## 🧪 Skill evaluations

|             | With Skill          | Without Skill       | Delta     |
| ----------- | ------------------- | ------------------- | --------- |
| **Overall** | **3065/3141 (98%)** | **1691/3141 (54%)** | **+44pp** |

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
