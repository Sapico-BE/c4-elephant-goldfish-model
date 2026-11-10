<p align="center">
  <a href="https://egm.dev"><img src="docs/assets/readme-header.svg" width="480" height="116" alt="Elephant-Goldfish Model"></a>
</p>

<p align="center">Design with an elephant. Review with a goldfish.</p>

<p align="center">
  <a href="#install">Install</a> &ensp;·&ensp;
  <a href="#try-your-first-design">Quickstart</a> &ensp;·&ensp;
  <a href="docs/getting_started.md">Documentation</a> &ensp;·&ensp;
  <a href="https://egm.dev">Website</a>
</p>

<br>

Develop ideas with context and review documents with fresh eyes. EGM is an open-source plugin for AI assistants.

This repository is a fork of the original [Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model). It adds the `c4` skill, which takes a greenfield project through the [C4 model](https://c4model.com), and it replaces the original brainstorm and draft skills. The plugin is named `c4` and appears as **c4 Elephant-Goldfish Model** in plugin lists.

You can install it next to the original `egm` plugin. Every name in this fork uses `c4` instead of `egm`, so the two plugins never share a command, skill, or reviewer name:

| | Original EGM | This fork |
| --- | --- | --- |
| Plugin | `egm` | `c4` |
| Skills | `egm-review`, `egm-resolve`, … | `c4`, `c4-review`, `c4-resolve`, `c4-review-loop`, `c4-bootstrap`, `c4-drift-report` |
| Reviewers | `egm-design`, `egm-zoom-out`, … | `c4-design`, `c4-zoom-out`, … |
| Claude Code command | `/egm:egm-review` | `/c4:c4-review` |

**Elephant** holds your project context and drafts the specification. **Goldfish** reviewers examine the draft and referenced source material without the earlier conversation, helping expose unstated assumptions and blind spots. **You** make the architectural trade-offs and approve the specification before implementing.

The built-in C4 design and review workflow targets software specifications. For other documents, choose reviewers and standards with `/c4-review-loop`. Bootstrap and drift reporting apply to software codebases.

https://github.com/user-attachments/assets/93c799a2-10a3-4266-af02-eb79dd33a9a2

## Install

Choose your coding agent. Install the complete plugin so its skills can read the reviewer prompts and document standards. Install from this repository: the published ChatGPT and Codex desktop listing installs the original EGM plugin, which does not include `c4`.

### Antigravity CLI

```sh
agy plugin install https://github.com/Sapico-BE/c4-elephant-goldfish-model
```

For the **Antigravity App** and **Antigravity for IDEs** (Visual Studio Code extension), run `/plugin` or see the [installation instructions](docs/harnesses.md#antigravity-app-and-antigravity-for-ides).

### Claude Code

```sh
claude plugin marketplace add Sapico-BE/c4-elephant-goldfish-model
claude plugin install c4@c4
```

### Codex CLI

```sh
codex plugin marketplace add Sapico-BE/c4-elephant-goldfish-model
codex plugin add c4@c4
```

Start a new session after installation. The plugin shows up as **c4 Elephant-Goldfish Model**. For **Claude Cowork** and **ChatGPT Work**, see the [setup guide](docs/harnesses.md).

## Try your first design

Open your project in your coding agent and choose a feature that needs design decisions. This example adds webhook delivery: what should happen when a delivery fails, or the same event arrives twice?

The commands below are shown without a prefix. In Antigravity (agy CLI) and Claude Code, add the `/c4:` prefix, for example `/c4:c4` or `/c4:c4-review`. On agy CLI 1.4.10 an unprefixed name is completed to the prefixed command ([#220](https://github.com/google/elephant-goldfish-model/issues/220)), but 1.4.8 does not ([#196](https://github.com/google/elephant-goldfish-model/issues/196)), so keep the prefix. In Codex, select the corresponding `c4` skill from the skill picker. The C4 workflow and review require a session that can create fresh subagents.

<img src="skills/c4/assets/icon.svg" width="20" height="20" align="top" alt=""> **Design it with C4**

```text
/c4 Add webhook delivery to this project.
```

The agent grills you on the problem, then drafts C1 (system context), C2 (containers), and C3 (components) documents under `docs/architecture/`. Fresh reviewers challenge each level, and you approve it before the next. Once the design is approved, the C4 code step writes a build plan and builds the project in test-first slices.

Progress lives in a task ledger, so the work survives across sessions. Run `/c4:c4` with no argument to resume the next ready task. Name a level (`c1`, `c2`, `c3 <container>`, or `c4`) to run it, or to reopen an approved level after confirming which later work becomes stale.

<img src="skills/c4-review/assets/icon.svg" width="20" height="20" align="top" alt=""> **Review a standalone document**

```text
/c4-review docs/designs/my-feature.md
```

Use `c4-review` for a design document you wrote yourself, outside the C4 flow. Fresh reviewers check the design, its clarity, its fit with the code, and its implementation plan. Choose which findings to address.

When the code exists, run `c4-drift-report` to compare the checked-in documents with the current source.

See the [workflow guide](docs/getting_started.md) for the full process.

## How it works

<table>
  <thead><tr><th align="left">Role</th><th align="left">Context</th><th align="left">Responsibility</th></tr></thead>
  <tbody>
    <tr valign="top"><td><strong>Elephant</strong></td><td>Your project, requirements, and earlier decisions</td><td>Explore the problem, draft the specification, and build it.</td></tr>
    <tr valign="top"><td><strong>Goldfish</strong></td><td>The document and its referenced source material, without the earlier conversation</td><td>Find missing assumptions, unclear requirements, and implementation risks.</td></tr>
    <tr valign="top"><td><strong>You</strong></td><td>The goals and constraints that matter</td><td>Resolve trade-offs, approve the design, and decide what to build.</td></tr>
  </tbody>
</table>

Goldfish reviews require fresh subagent contexts. If your agent cannot create them, EGM stops the review. A review does not replace tests or human judgment. See [supported environments and verification limits](docs/harnesses.md#support-status--contributing-other-harnesses).

## Choose a skill

You can use each skill when you need it. You do not have to follow the full sequence.

<table>
  <thead><tr><th align="left">Skill</th><th align="left">Use it to…</th></tr></thead>
  <tbody>
    <tr valign="top"><td width="160" valign="top"><img src="skills/c4/assets/icon.svg" width="20" height="20" alt="" align="top">&nbsp;<a href="skills/c4/SKILL.md">C4</a></td><td>Take a greenfield project through C1, C2, and C3 designs, then build it in test-first slices.</td></tr>
    <tr valign="top"><td width="160" valign="top"><img src="skills/c4-resolve/assets/icon.svg" width="20" height="20" alt="" align="top">&nbsp;<a href="skills/c4-resolve/SKILL.md">Resolve</a></td><td>Work through review findings and agree on changes.</td></tr>
    <tr valign="top"><td width="160" valign="top"><img src="skills/c4-bootstrap/assets/icon.svg" width="20" height="20" alt="" align="top">&nbsp;<a href="skills/c4-bootstrap/SKILL.md">Bootstrap</a></td><td>Create or update documentation for an existing codebase.</td></tr>
    <tr valign="top"><td width="160" valign="top"><img src="skills/c4-review/assets/icon.svg" width="20" height="20" alt="" align="top">&nbsp;<a href="skills/c4-review/SKILL.md">Review</a></td><td>Review a design with fresh agents across five stages.</td></tr>
    <tr valign="top"><td width="160" valign="top"><img src="skills/c4-review-loop/assets/icon.svg" width="20" height="20" alt="" align="top">&nbsp;<a href="skills/c4-review-loop/SKILL.md">Review&nbsp;loop</a></td><td>Run a configured group of reviewers for a specific review task.</td></tr>
    <tr valign="top"><td width="160" valign="top"><img src="skills/c4-drift-report/assets/icon.svg" width="20" height="20" alt="" align="top">&nbsp;<a href="skills/c4-drift-report/SKILL.md">Drift&nbsp;report</a></td><td>Compare checked-in documents with the current source code.</td></tr>
  </tbody>
</table>

## Learn more

- [Getting started](docs/getting_started.md): the workflow and project layout.
- [How c4 works](docs/explainers/c4.html): a visual walkthrough of the C4 flow, from grilling to test-first slices. Open the file in a browser; GitHub shows HTML as source.
- [Setup](docs/harnesses.md): installation, agent capabilities, and known limits.
- [C4 design](https://github.com/Sapico-BE/c4-elephant-goldfish-model/blob/main/docs/designs/c4.md): the design behind `c4`, its task ledger, and its rounds.
- [Architecture](https://github.com/Sapico-BE/c4-elephant-goldfish-model/blob/main/docs/designs/architecture.md): how skills and reviewers fit together.
- [Testing](https://github.com/Sapico-BE/c4-elephant-goldfish-model/blob/main/TESTING.md): checks, execution records, and verification limits.
- [Original EGM](https://github.com/google/elephant-goldfish-model): the upstream project this fork is based on.
- [Dave Rensin’s original essay](https://medium.com/@drensin/elephants-goldfish-and-the-new-golden-age-of-software-engineering-c33641a48874): the ideas behind EGM.

## Contribute

See the [accessibility statement](https://github.com/Sapico-BE/c4-elephant-goldfish-model/blob/main/ACCESSIBILITY.md)
for accessibility goals, known limits, and how to report barriers.

Read [contributing](https://github.com/Sapico-BE/c4-elephant-goldfish-model/blob/main/CONTRIBUTING.md) for PRs. Issues and discussions for the shared skills and reviewers live in the original project: [issues](https://github.com/google/elephant-goldfish-model/issues) for bugs, and [discussions](https://github.com/google/elephant-goldfish-model/discussions) for questions.

## License

[Apache 2.0](LICENSE). This is not an officially supported Google product.
