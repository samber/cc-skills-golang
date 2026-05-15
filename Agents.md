# Agents Helper — Go Skills

Purpose: a compact, in-editor helper that points you to focused Go skills from the `cc-skills-golang` repository and suggests quick actions you can take while editing Go code.

**How To Use**
- **Open summary**: see the compact index in [GO_SKILLS_SUMMARY.md](cc-skills-golang/GO_SKILLS_SUMMARY.md#L1).
- **Search a topic**: press `Ctrl+Shift+F` and search for `SKILL.md` or a topic name (e.g. `concurrency`, `observability`).
- **Jump to docs**: follow the links below to open the full skill guides in your editor.

**Quick Topics**
- **Concurrency**: patterns for goroutines, channels, select; safe synchronization. ([cc-skills-golang/skills/golang-concurrency/SKILL.md](cc-skills-golang/skills/golang-concurrency/SKILL.md#L1))
- **Context & Cancellation**: use `context.Context` for tracing and cancellations. ([cc-skills-golang/skills/golang-context/SKILL.md](cc-skills-golang/skills/golang-context/SKILL.md#L1))
- **Testing**: unit, integration, helpers and mocking strategies. ([cc-skills-golang/skills/golang-testing/SKILL.md](cc-skills-golang/skills/golang-testing/SKILL.md#L1))
- **Dependency Management**: `go.mod` workspaces, versioning, and conflict handling. ([cc-skills-golang/skills/golang-dependency-management/SKILL.md](cc-skills-golang/skills/golang-dependency-management/SKILL.md#L1))
- **Performance & Profiling**: pprof, CPU/memory optimization, observability. ([cc-skills-golang/skills/golang-performance/SKILL.md](cc-skills-golang/skills/golang-performance/SKILL.md#L1))
- **Security**: threat modeling, secrets, cryptography, and secure defaults. ([cc-skills-golang/skills/golang-security/SKILL.md](cc-skills-golang/skills/golang-security/SKILL.md#L1))
- **Project Layout**: recommended repository organization and testing layout. ([cc-skills-golang/skills/golang-project-layout/SKILL.md](cc-skills-golang/skills/golang-project-layout/SKILL.md#L1))
- **Observability**: logging, metrics, tracing and dashboards. ([cc-skills-golang/skills/golang-observability/SKILL.md](cc-skills-golang/skills/golang-observability/SKILL.md#L1))
- **Error Handling**: idiomatic error patterns and review flags. ([cc-skills-golang/skills/golang-error-handling/SKILL.md](cc-skills-golang/skills/golang-error-handling/SKILL.md#L1))

**In-Editor Quick Actions**
- **Open the full guide**: click any link above to open that skill's `SKILL.md`.
- **Copy example snippets**: SKILL pages often include small examples—select and paste into your code.
- **Search for references**: use the workspace search to find `references/*.md` for deep dives (e.g. pprof, tracing, testing helpers).

**Snippets & Automation (optional)**
- I can generate a VS Code `snippets` file containing ready-to-use templates for: test skeletons, `context` patterns, common `pprof` commands, and concurrency helpers. Tell me which ones you want and I'll add them under `.vscode/snippets/go.json`.

**Next Steps**
- Want me to generate VS Code snippets now? Reply with the topics you want (examples: `tests`, `context`, `concurrency`, `pprof`).
- Want the agent to add editor commands or a lightweight extension to surface these topics? I can draft that next.

---
Generated from the `cc-skills-golang` repository. See the full index: [GO_SKILLS_SUMMARY.md](cc-skills-golang/GO_SKILLS_SUMMARY.md#L1).
