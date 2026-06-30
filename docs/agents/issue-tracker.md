# Issue tracker: GitHub (`lgxyc/deer-flow`)

Issues and PRDs for this working copy live as GitHub issues on **`lgxyc/deer-flow`**.

Do **not** infer the tracker repo from the local clone's `origin` remote, because this checkout tracks the upstream project (`bytedance/deer-flow`) while planning and implementation issues belong to the fork.

## Conventions

- **Create an issue**:
  `gh issue create --repo lgxyc/deer-flow --title "..." --body-file ...`
- **Read an issue**:
  `gh issue view <number> --repo lgxyc/deer-flow --comments`
- **List issues**:
  `gh issue list --repo lgxyc/deer-flow --state open`
- **Comment on an issue**:
  `gh issue comment <number> --repo lgxyc/deer-flow --body "..."`
- **Apply / remove labels**:
  `gh issue edit <number> --repo lgxyc/deer-flow --add-label "..."` /
  `--remove-label "..."`
- **Close an issue**:
  `gh issue close <number> --repo lgxyc/deer-flow --comment "..."`

## When a skill says "publish to the issue tracker"

Create a GitHub issue in `lgxyc/deer-flow`.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --repo lgxyc/deer-flow --comments`.
