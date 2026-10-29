# P01 research: runtime support and required GitHub identities/permissions

Task: P01 (Reuse and authority decision). Sub-scope: runtime support and required
GitHub identities/permissions. Status: research evidence for the permission
matrix author, not a decision. Researcher: delegated Remora researcher (Claude).
All sources were accessed on 2026-10-29 (UTC) unless stated otherwise. Source IDs
match `permission-evidence.json` in this directory.

Conventions:

- **Documented**: quoted or closely paraphrased from the cited page.
- **Inference**: my reasoning from documented facts. It must be confirmed by a
  live test (P02a or P02b) or by maintainer review before the matrix relies on it.
- **Unverified / not found**: the documentation was searched and did not
  establish the claim. The places searched are listed.

Permission names are written as the docs present them: fine-grained PAT and App
permissions use the display name (for example "Contents") and, where the docs
give one, the URL parameter name (for example `contents`). Actions keys are
`GITHUB_TOKEN` `permissions:` keys (for example `contents: write`). OAuth and
classic PAT scopes are scope names (for example `project`). These three namespaces
are different. Do not copy names from one into another (see
`docs/development/github-setup.md`).

## Sources

GitHub docs were fetched through `https://docs.github.com/api/article/body?pathname=<path>`,
which returns the article body as Markdown. The canonical page URLs are listed here.

| ID | Page |
| --- | --- |
| S-gh-fgpat | https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens |
| S-gh-fg-endpoints | https://docs.github.com/en/rest/authentication/endpoints-available-for-fine-grained-personal-access-tokens |
| S-gh-appperms | https://docs.github.com/en/rest/authentication/permissions-required-for-github-apps |
| S-gh-app-choose | https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app |
| S-gh-app-iat | https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app |
| S-gh-app-auth-inst | https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation |
| S-gh-rest-installations | https://docs.github.com/en/rest/apps/installations |
| S-gh-app-keys | https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/managing-private-keys-for-github-apps |
| S-gh-app-suspend | https://docs.github.com/en/apps/maintaining-github-apps/suspending-a-github-app-installation |
| S-gh-pat-manage | https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens |
| S-gh-token-exp | https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/token-expiration-and-revocation |
| S-gh-org-pat-review | https://docs.github.com/en/organizations/managing-programmatic-access-to-your-organization/reviewing-and-revoking-personal-access-tokens-in-your-organization |
| S-gh-org-pat-policy | https://docs.github.com/en/organizations/managing-programmatic-access-to-your-organization/setting-a-personal-access-token-policy-for-your-organization |
| S-gh-oauth-scopes | https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps |
| S-gh-actions-token | https://docs.github.com/en/actions/concepts/security/github_token |
| S-gh-actions-token-howto | https://docs.github.com/en/actions/tutorials/authenticate-with-github_token (the plan's "automatic-token-authentication" path now serves this article) |
| S-gh-workflow-permissions | https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions |
| S-gh-actions-repo-settings | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository |
| S-gh-actions-events | https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows |
| S-gh-projects-api | https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects |
| S-gh-projects-actions | https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/automating-projects-using-actions |
| S-gh-gql-projects | https://docs.github.com/en/graphql/reference/projects |
| S-gh-gql-forming | https://docs.github.com/en/graphql/guides/forming-calls-with-graphql |
| S-gh-rules-available | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets |
| S-gh-rules-about | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets |
| S-gh-rules-create | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository |
| S-gh-rest-rules | https://docs.github.com/en/rest/repos/rules |
| S-gh-rest-refs | https://docs.github.com/en/rest/git/refs |
| S-gh-gql-commits | https://docs.github.com/en/graphql/reference/commits |
| S-gh-gql-git | https://docs.github.com/en/graphql/reference/git |
| S-gh-rest-checks | https://docs.github.com/en/rest/checks/runs |
| S-gh-rest-statuses | https://docs.github.com/en/rest/commits/statuses |
| S-gh-cli-auth-login | https://cli.github.com/manual/gh_auth_login |
| S-gh-cli-auth-refresh | https://cli.github.com/manual/gh_auth_refresh |
| S-gh-cli-auth-logout | https://cli.github.com/manual/gh_auth_logout |
| S-gh-cli-project | https://cli.github.com/manual/gh_project |
| S-git-push | https://git-scm.com/docs/git-push (page reports "git-push last updated in 2.55.0") |
| S-docker-sbx | https://docs.docker.com/ai/sandboxes/ |
| S-docker-sbx-security | https://docs.docker.com/ai/sandboxes/security/ |
| S-docker-sbx-defaults | https://docs.docker.com/ai/sandboxes/security/defaults/ |
| S-docker-sbx-isolation | https://docs.docker.com/ai/sandboxes/security/isolation/ |
| S-docker-sbx-install | https://docs.docker.com/ai/sandboxes/install/ |
| S-docker-sbx-credentials | https://docs.docker.com/ai/sandboxes/configuration/credentials/ |
| S-docker-sbx-settings | https://docs.docker.com/ai/sandboxes/configuration/settings/ |
| S-docker-sbx-network | https://docs.docker.com/ai/sandboxes/governance/access-controls/network/ |
| S-docker-sbx-faq | https://docs.docker.com/ai/sandboxes/faq/ |
| S-docker-engine-security | https://docs.docker.com/engine/security/ |
| S-docker-rootless | https://docs.docker.com/engine/security/rootless/ |
| S-docker-rootless-tips | https://docs.docker.com/engine/security/rootless/tips/ |
| S-docker-build-secrets | https://docs.docker.com/build/building/secrets/ |
| S-devcontainer-schema | https://github.com/devcontainers/spec/blob/d424cc157e9a110f3bf67d311b46c7306d5a465d/schemas/devContainer.base.schema.json (latest commit touching the file on `main` at access time, 2024-01-17) |
| S-claude-auth | https://code.claude.com/docs/en/authentication.md |
| S-codex-auth | https://developers.openai.com/codex/auth (redirected to https://learn.chatgpt.com/docs/auth) |
| S-codex-noninteractive | https://developers.openai.com/codex/noninteractive (redirected to https://learn.chatgpt.com/docs/non-interactive-mode) |

Reachability: every URL above returned HTTP 200. The Docker docs `index.md`
variants returned 404, so the HTML pages were used. The Codex pages are served
from `learn.chatgpt.com` after a redirect from `developers.openai.com`. Nothing
in this report was filled in from memory where a page could not be fetched.

---

## A. Identity and credential types

### A.0 Branch-level write is not a token property

- **Documented scoping dimensions:**
  - Fine-grained PAT: a single "Resource owner", then "Repository access", then
    "Permissions". Repository permissions such as `contents` take
    `read`/`write` (S-gh-pat-manage, "Creating a fine-grained personal access
    token" steps 9–13 and the "Repository permissions" table).
  - GitHub App installation token: when minting, you can narrow it with
    `repositories`/`repository_ids` and `permissions`. "The installation access
    token cannot be granted permissions that the app was not granted"
    (S-gh-app-iat).
  - `GITHUB_TOKEN`: "The token's permissions are limited to the repository that
    contains your workflow" (S-gh-actions-token).
  - Classic PAT: "it will grant access to all repositories within the
    organizations that you have access to, as well as all personal repositories
    in your personal account" (S-gh-pat-manage).
- **No branch dimension was found** in any token type (searched: S-gh-pat-manage
  creation steps and permission tables, S-gh-fgpat, S-gh-app-iat,
  S-gh-workflow-permissions, S-gh-oauth-scopes).
- **Branch restriction is a ruleset feature:** "You can control things like who
  can push commits to a certain branch" (S-gh-rules-about). "Restrict updates: If
  selected, only users with bypass permissions can push to branches or tags whose
  name matches the pattern you specify" (S-gh-rules-available).
- **Consequence (inference, consistent with the plan's S14 statement):** any
  credential with repository `Contents: write` can write every branch that
  rulesets do not protect. That includes `main`, `harness/state` and every
  `agent/*` candidate. Branch authority comes from rulesets plus the trusted
  publisher's code, never from the token.

### A.1 Capability comparison

`✓` means documented; `✗` means documented as unavailable; `?` means unverified.

| Capability | Classic PAT | Fine-grained PAT | GitHub App installation token | OAuth app token via `gh auth login` | Actions `GITHUB_TOKEN` |
| --- | --- | --- | --- | --- | --- |
| Repository selection | ✗. Covers all repositories the user can access (S-gh-pat-manage). | ✓. One resource owner; all or selected repositories (S-gh-pat-manage). | ✓. Installation repositories, and can be narrowed per token (S-gh-app-iat). | ✗. Scope-based like a classic PAT. `repo` "Grants full access to public and private repositories" (S-gh-oauth-scopes). | Workflow repository only (S-gh-actions-token). |
| Contents (Git and refs) | `repo` scope (S-gh-oauth-scopes). Changing workflow files also needs `workflow` (S-gh-oauth-scopes). | "Contents" `contents` read/write. `PATCH /repos/{owner}/{repo}/git/refs/{ref}` needs Contents write, plus "Workflows" write when workflow files change (both rows marked "Additional Permissions" ✓; S-gh-fgpat). | "Contents" repository permission (S-gh-appperms). HTTPS Git needs "Contents" (S-gh-app-auth-inst). | `repo`; `gh` minimum scopes are `repo`, `read:org`, `gist` (S-gh-cli-auth-login). | `contents: read\|write` (S-gh-workflow-permissions). Workflow-file pushes: ? (no `workflows` key exists in the documented `permissions` list). |
| Issues and comments | `repo` | "Issues" `issues` read/write. Comment and milestone endpoints also accept "Pull requests" (S-gh-fgpat). | "Issues" (S-gh-appperms) | `repo` | `issues: write` (S-gh-workflow-permissions) |
| Pull requests | `repo` | "Pull requests" `pull_requests` | "Pull requests" | `repo` | `pull-requests: write`. A repository setting can block creating/approving PRs (S-gh-actions-repo-settings). |
| Check runs: create | ✗. "Write permission for the REST API to interact with checks is only available to GitHub Apps" (S-gh-rest-checks). | ✗. Listed gap: "Using fine-grained personal access token to call the Checks API" (S-gh-pat-manage). | ✓. "Checks" write (S-gh-appperms) | ✗ (S-gh-rest-checks) | ✓. `checks: write`. `GITHUB_TOKEN` is an App installation token (S-gh-actions-token, S-gh-workflow-permissions). |
| Check runs: read | `repo` on private repositories (S-gh-rest-checks) | ✗. Same Checks API gap (S-gh-pat-manage). | ✓ "Checks" read | `repo` | `checks: read` |
| Commit statuses | `repo` or `repo:status` (S-gh-oauth-scopes) | "Commit statuses" `statuses` read/write (S-gh-fgpat) | "Commit statuses" | `repo` | `statuses: read\|write` |
| Actions | `repo`/`workflow` | "Actions" `actions` read/write | "Actions" | `repo`/`workflow` | `actions: read\|write` |
| Projects v2: organization-owned | `project` / `read:project`. `repo` "also grants access to manage organization-owned resources including projects" (S-gh-oauth-scopes). | ✓. Organization permission "Projects" `organization_projects`: `read`, `write`, `admin`; organization resource owner only (S-gh-pat-manage, S-gh-fgpat). | ✓. Organization permission "Projects". Read/write is required; "permission to read and write repository projects will not be sufficient" (S-gh-projects-actions, S-gh-appperms). | `project` via `gh auth refresh -s project` (S-gh-cli-project) | ✗. "`GITHUB_TOKEN` is scoped to the repository level and cannot access projects" (S-gh-projects-actions). |
| Projects v2: user-owned | ✓. `project`: "Grants read/write access to user and organization projects"; `repo` "also grants the ability to manage projects owned by users" (S-gh-oauth-scopes). | ✗. Listed gap: "Using fine-grained personal access token to access Projects owned by a user account" (S-gh-pat-manage). | ? No App permission for user-owned Projects found (searched the "User permissions" sections of S-gh-appperms and S-gh-app-choose). S-gh-projects-actions recommends a PAT "for user projects". | ✓ `project` | ✗ (S-gh-projects-actions) |
| Rulesets: create/edit | `repo` (admin user) ? Exact scope not tabulated. | "Administration" write for `POST/PUT/DELETE /repos/{owner}/{repo}/rulesets` (S-gh-fgpat) | "Administration" write (S-gh-appperms) | `repo` (admin user) ? | ✗. No `administration` key in the documented `permissions` list (S-gh-workflow-permissions). |
| Rulesets: read effective rules | ✓ | "Metadata" read: `GET /repos/{owner}/{repo}/rules/branches/{branch}`, `GET .../rulesets` (S-gh-fgpat) | "Metadata" read | ✓ | ? (not tabulated) |
| Can be a ruleset bypass actor | ? Bypass goes to roles, teams or Apps, not tokens (S-gh-rules-create) | ? Same | ✓. "GitHub Apps" are eligible (S-gh-rules-create); REST `actor_type` `Integration` (S-gh-rest-rules) | ? | ? Not found (searched: S-gh-rules-create, S-gh-rules-about, S-gh-rules-available, S-gh-rest-rules for "GitHub Actions"/"github-actions") |
| Can be pinned as the required-status-check source | ✗ | ✗ | ✓. "you can select an app as the expected source"; REST `integration_id` (S-gh-rules-available, S-gh-rest-rules) | ✗ | ? |

**Ruleset bypass actors (documentation discrepancy).** The UI procedure lists
these as eligible for bypass (S-gh-rules-create):

- "Repository admins, organization owners, and enterprise owners"
- "The maintain or write role, or custom repository roles based on the write role"
- "Teams, excluding secret teams"
- "GitHub Apps"
- "Dependabot"

The REST API schema for "Create a repository ruleset" also accepts
`actor_type` values `DeployKey` and `User` (S-gh-rest-rules). Whether an
individual user account (for example a machine user that holds a PAT) can be a
working bypass actor on a repository ruleset is **unverified** and needs a live
test. `OrganizationAdmin` "is not applicable for personal repositories"
(S-gh-rest-rules).

### A.2 Expiry and revocation (documented procedures)

**Classic PAT**
- Expiry: optional. GitHub "automatically removes personal access tokens that
  haven't been used in a year" (S-gh-pat-manage).
- Revocation: delete it under the user's settings ("Deleting a personal access
  token"; S-gh-pat-manage), or use the credential revocation API, which accepts
  the `ghp_` prefix (S-gh-token-exp).
- Organization control: owners can restrict classic PAT access, and a maximum
  lifetime policy exists (S-gh-org-pat-policy). Organization owners cannot see
  or revoke classic PATs in the organization UI (S-gh-org-pat-review).

**Fine-grained PAT**
- Expiry: `expires_in` is "Integer between 1 and 366, or `none`". The default is
  30 days, "or less if the target has a token lifetime policy set"
  (S-gh-pat-manage).
- Organizations "can require approval". A pending token "will only be able to
  read public resources until it is approved" (S-gh-pat-manage).
- Revocation: the user deletes it, or organization owners revoke it in the UI or
  REST API. Those REST endpoints "can only be called by GitHub Apps"
  (S-gh-org-pat-review). The credential revocation API also accepts
  `github_pat_` (S-gh-token-exp).

**GitHub App installation token**
- Expiry: "The installation access token will expire after 1 hour"
  (S-gh-app-iat).
- Revoke one token: `DELETE /installation/token` "Revokes the installation token
  you're using to authenticate" (S-gh-rest-installations).
- The long-lived secret is the App private key. "Private keys do not expire and
  instead need to be manually revoked". There can be up to 25 keys, and "you
  must regenerate a new key before you can delete the existing key"
  (S-gh-app-keys).
- Emergency stop: suspend the installation ("you might want to suspend your
  GitHub App if you are worried that your app's credentials were leaked";
  S-gh-app-suspend).
- The credential revocation API list does not include `ghs_` installation tokens
  (S-gh-token-exp lists `ghp_`, `github_pat_`, `gho_`, `ghu_`, `ghr_`).
- Since 2026-04-27, a staged rollout gives new installation tokens a stateless
  `ghs_APPID_JWT` format. Do not assume a 40-character length (S-gh-app-iat).

**OAuth token via `gh auth login`**
- Storage: "stored securely in the system credential store", with a plaintext
  fallback if no store is available (S-gh-cli-auth-login).
- Expiry: `--expiring` is "a preference, not a guarantee" (S-gh-cli-auth-login).
  OAuth tokens unused for a year are revoked (S-gh-token-exp).
- `gh auth logout` "does not revoke authentication tokens". To revoke, open
  github.com/settings/applications, select "GitHub CLI", then "Revoke Access".
  That "will revoke all authentication tokens ever generated by the GitHub CLI
  across all your devices" (S-gh-cli-auth-logout).

**Actions `GITHUB_TOKEN`**
- Created per job. It "expires when the job finishes or after its effective
  maximum lifetime": 6 hours on GitHub-hosted runners. On self-hosted runners it
  can only be refreshed for up to 24 hours (S-gh-actions-token).
- No separate revocation procedure is documented beyond job completion.

---

## B. Role × resource evidence

Labels: **setup-only** = needed by `harness init` or the bootstrap import, not by
running workers. **runtime** = needed while the system operates. "Enforcement"
lists the GitHub setting that must complement the API permission, because the
permission alone is not enough (section A.0).

### B.1 setup-operator (setup-only)

These rows are grounded in the calls `bootstrap/github.py` makes:

- REST: `GET repos/{repo}`, `GET .../milestones`, `GET .../issues`,
  `GET .../assignees/{human}`, `POST .../milestones`, `POST .../issues`
- `gh project list|view|create|item-list|field-list|field-create|link|item-add|item-edit`
- GraphQL `updateProjectV2Field`

Rulesets are added because plan section 10 has `harness init` emit and check them.

| Resource | Minimal documented permission | Credential types | Notes and enforcement |
| --- | --- | --- | --- |
| Repository metadata | FG/App "Metadata" read (`GET /repos/{owner}/{repo}`; S-gh-fgpat) | FG PAT, App, classic/OAuth `repo` | – |
| Milestones: list, create | FG/App "Issues" or "Pull requests", read/write (`POST /repos/{owner}/{repo}/milestones` appears under both with "Additional Permissions" ✓; S-gh-fgpat) | FG PAT, App, classic/OAuth `repo` | – |
| Issues: list, create, assign; check assignee | "Issues" read/write (`POST /repos/{owner}/{repo}/issues`, `GET .../assignees/{assignee}`; S-gh-fgpat) | same | – |
| Project: create, list, link to repository, create fields, set Status options, add items, set item field | Org-owned: FG `organization_projects` (Projects) write or `admin`; App organization "Projects" read/write. User-owned: classic PAT or OAuth `project` only (S-gh-pat-manage gap; S-gh-oauth-scopes). `gh project` says "The minimum required scope for the token is: project" (S-gh-cli-project). | Org: FG PAT, App, classic/OAuth. User: classic/OAuth only. | Fine-grained/App REST covers org Project items, fields and views (S-gh-fgpat "Organization permissions for Projects"). No REST endpoint to create a Project, or to set single-select options, is listed for FG PATs (S-gh-fg-endpoints). Those are GraphQL (`createProjectV2`, `updateProjectV2Field`; S-gh-gql-projects). The FG/App permission level GraphQL needs (`write` vs `admin`) is **unverified**. For Apps, `createProjectV2` with `repositoryId` also needs "Contents" for that repository (S-gh-projects-api). |
| Rulesets: create/update | FG/App "Administration" write (S-gh-fgpat rows for `/repos/{owner}/{repo}/rulesets`). Actor needs "admin access to a repository, or a custom role with the 'edit repository rules' permission" (S-gh-rules-about, page header). | FG PAT, App, classic/OAuth for an admin user | Rulesets on private repositories require GitHub Pro, Team or Enterprise Cloud. On Free they exist only for public repositories (S-gh-rules-about header). |
| Actions default workflow permissions | Repository settings UI (S-gh-actions-repo-settings). API permission name not researched. | human UI | Default for new personal repositories: "`GITHUB_TOKEN` only has read access for the `contents` and `packages` scopes" (S-gh-actions-repo-settings). |
| Rulesets: verify (doctor) | "Metadata" read: `GET /repos/{owner}/{repo}/rules/branches/{branch}` (S-gh-fgpat) | any | Runtime-safe read for `harness doctor` |

Must not carry into runtime: "Administration" write; Project `admin`; the
classic `repo` scope covering other repositories.

### B.2 supervisor-runtime (runtime, default placement)

| Resource | Need | Minimal documented permission | Credential types | Enforcement that must complement it |
| --- | --- | --- | --- | --- |
| State branch `harness/state`: read | runtime | "Contents" read | App, FG PAT, classic/OAuth | – |
| State branch: conditional write | runtime | "Contents" write. REST ref PATCH, `createCommitOnBranch` or `updateRefs` (section C). | App (preferred: it can be named as a bypass actor), FG PAT, classic/OAuth | Ruleset on `harness/state`: Restrict deletions; Block force pushes (`non_fast_forward`); Restrict updates (and creations) with bypass only for the supervisor App (`actor_type: Integration`). See D for the two-ruleset layout. |
| Candidate branches `agent/**/*`: create and update | runtime | "Contents" write. Add "Workflows" write only if candidates may change `.github/workflows/*` (S-gh-fgpat "Workflows" rows for `git/refs` and `contents/{path}`; classic `workflow` scope per S-gh-oauth-scopes). | same | Ruleset on `agent/**/*`: Restrict creations/updates/deletions with bypass = publisher App; Block force pushes for generation-specific immutable names. Per-task branch ownership cannot be enforced by GitHub, because every candidate is published by one identity. The trusted publisher code must enforce it (inference; see D). |
| `main`: no write | runtime | Not separable. "Contents" write includes `PUT /repos/{owner}/{repo}/pulls/{pull_number}/merge` (listed under Contents write in S-gh-fgpat). | – | Ruleset on `main`: Require a pull request with ≥1 approval; required status checks from the trusted-CI App; supervisor App **not** on the bypass list; Block force pushes; Restrict deletions. Without Pull requests write the App cannot approve. Whether an App review counts toward required approvals is **unverified**. |
| Issue comments, labels | runtime | "Issues" write (`POST .../issues/{issue_number}/comments`; S-gh-fgpat) | App, FG PAT, classic/OAuth | – |
| Human command polling | runtime | "Issues" read (comments) | same | Authenticate the human through the comment author login plus enrollment (plan section 4). The token does not authenticate others. |
| Project status projection | runtime | Org: App organization "Projects" write or FG `organization_projects` write. User: classic/OAuth `project`. | Org: App/FG. User: classic PAT or OAuth only. | – |
| Checks and statuses: read (evidence) | runtime | App "Checks" read and "Commit statuses" read | App (FG PATs cannot call the Checks API: S-gh-pat-manage), classic/OAuth `repo` | Evidence identity is checked through the check run's App, not by the reader's token. |
| Pull requests (optional, opening integration PRs) | runtime (optional) | "Pull requests" write | App, FG, classic | Repository setting "Allow GitHub Actions to create and approve pull requests" applies only to `GITHUB_TOKEN` (S-gh-actions-repo-settings) |

Must not have: "Administration" write, "Checks" write (that belongs to trusted-ci),
Project `admin`, "Workflows" write unless explicitly approved, and any bypass on
the `main` ruleset.

### B.3 actions-publisher-fallback (runtime, Actions-hosted placement)

| Resource | `GITHUB_TOKEN` key | Gap or caveat |
| --- | --- | --- |
| State and candidate branches | `contents: write` | Whether `GITHUB_TOKEN` (the GitHub Actions App) can be a ruleset bypass actor is **not found**. Without that, the state-branch "Restrict updates" rule cannot name it. Minting an App installation token in the job ("create a GitHub App and generate an installation access token within your workflow"; S-gh-actions-token-howto) lets the bypass actor be that App. |
| Issue comments | `issues: write` | – |
| Project status | none available | "`GITHUB_TOKEN` ... cannot access projects" (S-gh-projects-actions). Needs an App token (org Project) or a stored PAT (user Project), which means a long-lived secret in Actions secrets. |
| Checks/statuses read | `checks: read`, `statuses: read` | – |
| Triggering CI | – | "events triggered by the `GITHUB_TOKEN` will not create a new workflow run", except `workflow_dispatch`/`repository_dispatch`. PR `opened`/`synchronize`/`reopened` events create runs "in an **approval-required** state" (S-gh-actions-token). Candidates pushed with `GITHUB_TOKEN` will not trigger push-based trusted CI. |
| Scheduling | – | `schedule` "can be delayed ... some queued jobs may be dropped"; runs only on the default branch; minimum interval 5 minutes; public repositories disable it after 60 days of inactivity (S-gh-actions-events). This matches the plan: no claims or renewals depend on scheduled runs. |
| Untrusted triggers | – | `pull_request_target` grants "read/write repository permission, even when it is triggered from a public fork" (S-gh-workflow-permissions). Do not use it for the reducer. |
| Workflow tampering | – | "Anyone with write access to a repository can modify the permissions granted to the `GITHUB_TOKEN` ... by editing the `permissions` key in the workflow file" (S-gh-actions-repo-settings). The workflow file is in the trusted computing base. Protect `.github/workflows/**` with a ruleset and review. |
| Token lifetime | – | ≤6 h on hosted runners; refresh ≤24 h on self-hosted (S-gh-actions-token) |

### B.4 developer-sandbox and B.5 reviewer-sandbox (runtime)

| Resource | Need | Evidence |
| --- | --- | --- |
| Any GitHub write credential | **none, by design** | Plan section 7. With the Docker Sandboxes credential proxy, configuring the built-in `github` service (`sbx secret set github --command 'gh auth token'`) injects the host token into requests to `api.github.com`, `github.com` and others. The agent can then use the token's full authority through the proxy without reading it (S-docker-sbx-credentials). Do not configure it. |
| Repository read | none required inside the sandbox | The supervisor imports or checks out the exact candidate/base into the private workspace (plan section 7). Public repositories are readable without a token. Every fine-grained PAT includes "read-only access to all public repositories" (S-gh-pat-manage). For private repositories, any read token placed in the sandbox would be exposed to the model. Inference: deliver source through the supervisor, with no GitHub token at all. |
| Issue/task text | none | The supervisor supplies the immutable packet |
| SSH agent | must be off | Docker Sandboxes: `ssh.agentForwardingEnabled` default `true` (S-docker-sbx-settings). Set it to `false`. |

Reviewer: same as the developer, plus a fresh clone and session per job (plan section 7).

### B.6 trusted-ci (runtime)

| Resource | Permission | Credential | Enforcement |
| --- | --- | --- | --- |
| Candidate source read | "Contents" read | CI App or `GITHUB_TOKEN` (`contents: read`) | – |
| Check runs: write | "Checks" write. Only Apps: "To create a check run, you must use a GitHub App" (S-gh-rest-checks). | Dedicated CI App, or `GITHUB_TOKEN` `checks: write` | Ruleset required status check with an App as source. "The app must be installed in the repository with the `statuses:write` permission, must have recently submitted a check run, and must be associated with a pre-existing required status check" (S-gh-rules-available). REST `integration_id` (S-gh-rest-rules). |
| Commit statuses: write | "Commit statuses" write. "Any person or integration with write permissions to a repository can set the state of any status check" (S-gh-rules-available). | any | Statuses from "any source" are spoofable by any writer. Pin the source App. |

Must not have: "Contents" write on `harness/state` or `main`, or any bypass.

### B.7 human-integrator (runtime)

- Who: a human account with write/maintain role, merging via a PR.
- Enforcement: the `main` ruleset described in B.2. Remove "Repository admins"
  from the bypass list, or accept that the human admin bypass is "outside the
  automation guarantee" (plan section 3).
- Bypass mode `exempt` means "rules will not be run for that actor and a bypass
  audit entry will not be created" (S-gh-rest-rules). Avoid it for auditability.

---

## C. Conditional publication transports

| Transport | Documented semantics | What it does not guarantee | Identities |
| --- | --- | --- | --- |
| REST `PATCH /repos/{owner}/{repo}/git/refs/{ref}` | Body `sha` (required) and `force`. With `force` false (the default) it will "make sure the update is a fast-forward update". Responses: `200`, `409 Conflict`, `422` "Validation failed, or the endpoint has been spammed" (S-gh-rest-refs). Commits are built with `POST .../git/blobs`, `.../git/trees`, `.../git/commits` (Contents write; S-gh-fgpat). | No expected-old-SHA parameter. Which status code signals a non-fast-forward rejection is not documented, so 409/422 are not uniquely contention results. Inference: if the new commit's only parent is the observed head, and rewinds are blocked by ruleset, a fast-forward check rejects a concurrent winner's descendant. That is CAS-like, but it must be proven in P02a. | Any identity with Contents write (+ Workflows when workflow files change) |
| GraphQL `createCommitOnBranch` | `expectedHeadOid` (GitObjectID!, required): "The git commit oid expected at the head of the branch prior to the commit". It "creates a commit whose parent is the HEAD of the provided branch and also updates that branch". Commits are "authored by the owner of the credential" and "automatically signed by GitHub if supported" (S-gh-gql-commits). | No author/committer control. Files only via `fileChanges`, with no arbitrary parents or merge commits. It appends to an existing branch, so new branches need `createRef`. The error shape on mismatch is not documented. The FG/App permission for this mutation is not tabulated (inferred Contents write; **unverified**). | PAT, App, OAuth (S-gh-gql-forming). `GITHUB_TOKEN`: ? |
| GraphQL `updateRefs` (not in the plan) | "All updates are performed atomically, meaning that if one of them is rejected, no other ref will be modified." `RefUpdate.beforeOid`: "The value this ref needs to point to before the update". An all-zero OID "can be used to verify that the references should not exist" (S-gh-gql-git). | Server-side race behaviour and error shape are not documented. The permission mapping is not tabulated (**unverified**). The commit object must exist first (REST Git database). | Same as above |
| GraphQL `updateRef` | `refId`, `oid`, `force` (S-gh-gql-git) | No expected-old value | – |
| `git push --force-with-lease=<refname>:<expect>` | Updates "only if the current value of the remote ref is the expected value"; an empty `<expect>` means "the named ref must not already exist". Forms without an explicit expected value "are still experimental". `--atomic`: "Either all refs are updated, or on error, no refs are updated. If the server does not support atomic pushes the push will fail." (S-git-push) | How atomic GitHub's server-side compare is, and its rejection messages, are not documented by GitHub (searched S-gh-rest-refs, S-gh-rules-available). It runs local `git`, which must be a clean controlled environment without candidate hooks, helpers or filters (plan section 4). | PATs over HTTPS only ("Personal access tokens can only be used for HTTPS Git operations"; S-gh-pat-manage). App via `x-access-token` with "Contents" (S-gh-app-auth-inst). `GITHUB_TOKEN`. |

For P02a: `updateRefs` with `beforeOid` gives documented multi-ref
expected-old-value semantics. With an all-zero `beforeOid`, it can also create
generation-specific `agent/*` refs that must not already exist. It is the only
GitHub-API transport found whose description includes an expected old value for
arbitrary commits. Live races are still required. Whether rulesets (Restrict
updates, Block force pushes) are enforced identically for REST, GraphQL and Git
push paths is not stated in the ruleset pages (searched S-gh-rules-available,
S-gh-rules-about, S-gh-rules-create). Test each chosen path.

---

## D. State-branch and candidate-branch protection

Documented rules (S-gh-rules-available; REST `type` names from S-gh-rest-rules):

- Restrict creations (`creation`): "only users with bypass permissions can create
  branches or tags whose name matches the pattern".
- Restrict updates (`update`, parameter `update_allows_fetch_and_merge`): "only
  users with bypass permissions can push to" matching refs.
- Restrict deletions (`deletion`): "This rule is selected by default."
- Block force pushes (`non_fast_forward`): "This rule is enabled by default."
  Force pushing "can also be used to delete branches or point a branch to commits
  that were not approved".
- Require status checks (`required_status_checks`, `integration_id`).
- Require linear history and Require a pull request: relevant to `main` only.

Bypass:

- Eligible actors are roles, non-secret teams, GitHub Apps and Dependabot
  (S-gh-rules-create). REST also lists `User` and `DeployKey` (S-gh-rest-rules);
  see the discrepancy note in A.1.
- A bypass can be limited to a single App (`actor_type: Integration`,
  `actor_id`). A specific human or machine-user PAT holder can be named only
  through the REST `User` actor type. That path is **unverified**.
- A user-owned repository has no teams, and `OrganizationAdmin` "is not
  applicable for personal repositories" (S-gh-rest-rules). Required-reviewer
  teams are "not available on user-owned repositories as they do not contain
  teams" (S-gh-rules-available).
- Bypass applies to "the rules in the ruleset" (S-gh-rules-about). Multiple
  rulesets are aggregated and "the most restrictive version of the rule applies"
  (S-gh-rules-about).
- **Inference, to test:** keep "Restrict deletions" and "Block force pushes" in
  a ruleset with an **empty** bypass list. Put "Restrict creations/updates" in a
  second ruleset whose only bypass actor is the publisher App. Then the
  publisher can fast-forward but cannot rewind or delete.

Patterns:

- `fnmatch` with `File::FNM_PATHNAME`: "`*` wildcard does not match directory
  separators (`/`)". Use `agent/**/*` for nested names (S-gh-rules-create).
- Patterns are enforcement configuration on the repository. They do not appear
  in any token's scope (A.0).

Plan availability:

- Rulesets need a public repository, or a private repository on GitHub Pro, Team
  or Enterprise Cloud (S-gh-rules-about).
- A private repository on GitHub Free therefore cannot enforce the state-branch
  profile. Per plan section 4, setup must report that gap and disable
  autonomous execution.

Doctor:

- `GET /repos/{owner}/{repo}/rules/branches/{branch}` ("Metadata" read) returns
  the effective rules on a branch (S-gh-fgpat). GraphQL `RefUpdateRule` exposes
  `viewerCanPush`, `allowsForcePushes` and `allowsDeletions` (S-gh-gql-git).

---

## E. Runtime support

### E.1 Docker Sandboxes (`sbx`)

**Platform** (S-docker-sbx-install):
- macOS Sonoma 14+ on Apple silicon.
- Windows 11 x86-64 with Windows Hypervisor Platform.
- Linux: "Ubuntu 24.04 or later" on x86-64 or Arm64, with KVM and the user in
  the `kvm` group. Nested virtualization is required inside VMs. "Docker does not
  test or support Docker Sandboxes on Ubuntu derivatives".
- Sign-in with `sbx login` (Docker OAuth) is required (S-docker-sbx-faq).
- Organization governance is "a separate paid subscription" (S-docker-sbx).
- Observation: this bootstrap host is Debian 11 ("bullseye"), which is not in
  the documented Linux support list. `/dev/kvm` was not visible from this
  agent's sandbox, which is not conclusive.

**Isolation claims** (S-docker-sbx-security, S-docker-sbx-isolation):
- A microVM with "its own Linux kernel" and a private Docker Engine, with "no
  path to your host Docker daemon".
- The agent has sudo inside the VM. "The hypervisor boundary is the isolation
  control, not in-VM privilege separation."
- Outbound TCP goes through a host proxy under a deny-by-default policy. DNS is
  policy-enforced, UDP is off and ICMP is blocked.
- Sandboxes cannot reach each other.
- Processes "can write text to your host clipboard".

**Credential proxy:**
- The host proxy "overwrites the auth header". "The real credential stays on the
  host ... the sandbox sees only a sentinel value" (S-docker-sbx-credentials).
- A kit can set OAuth `passthrough: true`, which "sends the real token response
  into the sandbox" (S-docker-sbx-credentials).
- Header injection still grants the token's authority to any request the agent
  makes to the listed domains (inference from the injection description; plan:
  "Credential isolation is insufficient if the model can invoke a proxy that
  grants arbitrary writes").

**Settings to set explicitly and record:**
- `ssh.agentForwardingEnabled=false`. The default is `true`, and the
  credentials page says "SSH agent forwarding is enabled by default".
- `skills.defaultMode=off`, or create sandboxes with `--skills=off`.
- `browser.enabled=false`. The default is `true`, and the setting also allows
  in-sandbox OAuth to localhost.
- `clipboard.imagePaste=false` (default `false`).
- `env.rememberHostCommands=false` (default). Environment-file host commands "run
  on your host with your permissions".
- `kit.allowedSources` (default Docker Hub only), plus `kit.requireSignature`.
- Do not `sbx secret set github`.
- Use clone mode (`--clone`) or mountless workspaces. Direct mode is read-write on
  the host working tree, including Git hooks (S-docker-sbx-security).
- Inspect and trim the network policy with `sbx policy ls`. "The default allowed
  domains include broad wildcards" such as `*.googleapis.com`
  (S-docker-sbx-security).
- Do not register local stdio MCP servers. They "run on the host"
  (S-docker-sbx-security).

**Documentation inconsistencies (reinforcing plan section 7):**
- The shared skills store is "read-only by default" on S-docker-sbx-security and
  S-docker-sbx-defaults, and `skills.defaultMode` defaults to `readonly`
  (S-docker-sbx-settings). But the same security page's isolation diagram says
  "Supported agents mount the host-side skills store read-write unless you opt
  out".
- The credential defaults say "No credentials are available to the sandbox
  unless you provide them" (S-docker-sbx-defaults), while SSH agent forwarding is
  on by default whenever `SSH_AUTH_SOCK` is set (S-docker-sbx-credentials).
- The default-domain list is referenced but not enumerated on the defaults page.
- P02b must measure the actual policy with `sbx settings ls --json` and
  `sbx policy ls` on the target host.

### E.2 Ordinary OCI profile (plan section 7)

| Profile item | Documentable now | Must be measured in P02b |
| --- | --- | --- |
| Non-root execution, rootless runtime | Rootless runs "both the daemon and the container ... without root privileges". It needs `newuidmap`/`newgidmap` and ≥65,536 subordinate IDs (S-docker-rootless). The daemon otherwise "requires `root` privileges", and "only trusted users should be allowed to control your Docker daemon" (S-docker-engine-security). | Rootless works on each supported host |
| Resource limits | Under rootless, cgroup flags are "supported only when running with cgroup v2 and systemd". When unmet, "rootless mode ignores the cgroup-related `docker run` flags" silently, and typically only `memory` and `pids` are delegated (S-docker-rootless-tips). | `docker info` Cgroup Driver; that limits are actually applied (doctor must fail closed) |
| Restricted capabilities | "By default, Docker starts containers with a restricted set of capabilities" (S-docker-engine-security) | The exact `--cap-drop` set, seccomp and AppArmor |
| No host mounts or Docker socket | A bind of `/` lets "the container ... alter your host filesystem without any restriction" (S-docker-engine-security) | Mount audit of the launched container |
| Read-only root filesystem, private workspace/tmp | – | Toolchain compatibility |
| Egress enforcement, including DNS and IPv6 bypass | Not documented in the fetched pages | Entirely P02b |
| Secrets not baked into images | Build args/env "persist in the final image"; use secret mounts (S-docker-build-secrets) | – |
| Separate caches by trust domain | – | P02b |

### E.3 Devcontainer fields that convey host authority (S-devcontainer-schema)

Review these before any execution, and refuse them or require human approval:

- `initializeCommand`: "A command to run locally (i.e Your host machine, cloud
  VM) before anything else". This is host code execution.
- In-container lifecycle commands run candidate-controlled code inside the
  container: `onCreateCommand`, `updateContentCommand`, `postCreateCommand`,
  `postStartCommand`, `postAttachCommand`.
- `mounts` ("See Docker's documentation for the --mount option") and
  `workspaceMount` ("The --mount parameter for docker run"). Through these, a
  Docker socket or home directory can be bind-mounted.
- `privileged` ("Passes the --privileged flag"), `capAdd`, `securityOpt`, and
  `runArgs` ("The arguments required when starting in the container"): arbitrary
  `docker run` flags such as `--network=host`, `-v` and `--pid=host`.
- `build.options` ("Additional arguments passed to the build command") and
  `build.args`.
- `features`: third-party install scripts. `dockerComposeFile`, `service` and
  `runServices`: Compose files can declare their own volumes and privileges.
- `appPort` and `forwardPorts` (host port exposure), `containerEnv` and
  `remoteEnv` (environment injection), and `updateRemoteUserUID` (host UID
  mapping).
- The schema has **no dedicated Docker-socket field**. Socket access arrives
  through `mounts`, `workspaceMount`, `runArgs`, Compose volumes or Features
  (inference from the schema; searched for "docker.sock").

---

## F. Provider unattended authentication

**Claude Code** (S-claude-auth):
- Precedence:
  1. Cloud provider (`CLAUDE_CODE_USE_BEDROCK`, `..._VERTEX`, `..._FOUNDRY`)
  2. `ANTHROPIC_AUTH_TOKEN`
  3. `ANTHROPIC_API_KEY` ("In non-interactive mode (`-p`), the key is always
     used when present")
  4. `apiKeyHelper`
  5. `CLAUDE_CODE_OAUTH_TOKEN` (a "one-year OAuth token" from
     `claude setup-token`, "for CI pipelines and scripts", requiring a Pro, Max,
     Team or Enterprise plan; "It can only make model requests")
  6. Profiles and federation
  7. `/login`
- Bare mode does not read `CLAUDE_CODE_OAUTH_TOKEN`.
- Managed settings (`forceLoginMethod`/`forceLoginOrgUUID`) can block
  environment credentials.
- The Docker Sandboxes `anthropic` service injects into `api.anthropic.com`,
  `console.anthropic.com`, `claude.ai` and `mcp-proxy.anthropic.com`
  (S-docker-sbx-credentials).

**Codex CLI** (S-codex-auth, S-codex-noninteractive):
- Login by API key with `printenv OPENAI_API_KEY | codex login --with-api-key`.
- "Use API key authentication for programmatic Codex CLI workflows, such as
  CI/CD jobs".
- `CODEX_API_KEY` works with `codex exec`. "Do not set `OPENAI_API_KEY` or
  `CODEX_API_KEY` as a job-level environment variable in workflows that check out
  or run repository-controlled code".
- Device code (`codex login --device-auth`, beta) for headless hosts.
- Enterprise "Codex access tokens" (`codex login --with-access-token`).
- Credentials are cached in plaintext `~/.codex/auth.json` or the OS store:
  "treat `~/.codex/auth.json` like a password".

Implication (inference): both providers support unattended API-key auth, but
through different variables. Any provider key placed in a sandbox environment
is readable by candidate code. A host-side injecting proxy (Docker Sandboxes) or
a provider-documented proxy (the Codex GitHub Action "starting a Responses API
proxy") is needed to keep the value out of the sandbox.

---

## G. Gaps for `harness init` and maintainer questions

### G.1 Documented gaps against plan section 10's credential specification

1. **User-owned Projects:**
   - Fine-grained PATs cannot access them (S-gh-pat-manage limitations list).
   - `GITHUB_TOKEN` cannot access any Project (S-gh-projects-actions).
   - No GitHub App permission for user-owned Projects was found (S-gh-appperms
     and S-gh-app-choose user-permission sections).
   - Only the classic PAT/OAuth `project` scope is documented (S-gh-oauth-scopes).
     It is not repository-scoped, and `gh` also requires `repo`, `read:org` and
     `gist` (S-gh-cli-auth-login).
   - Therefore a user-account deployment needs a separate broad classic or OAuth
     credential just for Project projection. `harness init` must emit it as a
     distinct credential with that exposure stated.
2. **Checks API:**
   - Fine-grained PATs cannot call it, even to read (S-gh-pat-manage).
   - Creating check runs requires a GitHub App (S-gh-rest-checks).
   - Supervisor evidence reads and trusted-CI writes therefore need an App, or a
     classic/OAuth token for reads.
3. **Bypass identity:**
   - Only Apps (and roles, teams, Dependabot) are documented UI bypass actors.
   - A PAT-based supervisor can be named only through the REST `User` actor type
     (unverified), or by granting a whole role. A write-role bypass would also
     cover the human and any other writer.
   - Inference: the state-branch "only the selected supervisor/publisher" rule
     (plan section 4) is reliably expressible only with a GitHub App.
4. **Actions fallback:**
   - `GITHUB_TOKEN` as a ruleset bypass actor: not found.
   - Its pushes do not trigger CI.
   - It cannot touch Projects.
   - The fallback therefore probably needs an App installation token minted in
     the workflow, which means an App private key stored as an Actions secret.
5. **Merge authority is not separable from Contents write** (S-gh-fgpat lists
   `PUT .../pulls/{pull_number}/merge` under "Contents" write). "No merge
   authority" (plan contract 10) is enforced only by the `main` ruleset, not by
   token permissions.
6. **Workflow files:**
   - Publishing a candidate that changes `.github/workflows/*` needs "Workflows"
     write (FG/App) or `workflow` (classic).
   - The `GITHUB_TOKEN` permission list has no workflows key.
   - The matrix must choose between rejecting such candidates and granting that
     extra power.
7. **Rulesets on private Free repositories are unavailable** (S-gh-rules-about).
8. **GraphQL permission mapping:**
   - The fine-grained/App permissions required by `createCommitOnBranch`,
     `updateRefs`, `createProjectV2`, `updateProjectV2Field` and
     `linkProjectV2ToRepository` are not tabulated.
   - The REST tables cover only REST.
   - S-gh-gql-forming says the API "will return an error message that states the
     scopes or permissions your token needs", so `doctor` can detect this.
     `init` cannot cite a documented name.
9. **Expiry differences:**
   - App private keys never expire; installation tokens last 1 h.
   - Fine-grained PATs: ≤366 days or `none`.
   - `gh` OAuth: non-expiring unless `--expiring` is honoured.
   - Revocation of `gh` tokens is all-devices only (S-gh-cli-auth-logout).
   - `ghs_` tokens are not on the credential revocation API list.
10. **Docker Sandboxes host support:** Linux is Ubuntu 24.04+ only. The current
    bootstrap host (Debian 11) is outside the documented support list.

### G.2 Unverified items needing live tests (P02a/P02b)

- REST ref PATCH: the status code on a non-fast-forward race (409 vs 422).
- The error shape on `expectedHeadOid` mismatch.
- `updateRefs` `beforeOid` behaviour under concurrent writers.
- Ruleset enforcement parity across REST, GraphQL and Git push.
- The two-ruleset bypass layout (D).
- A `User` bypass actor on a repository ruleset.
- `GITHUB_TOKEN` as a bypass actor.
- The FG/App permission level for Project GraphQL mutations.
- Whether an App can access a user-owned Project.
- Docker Sandboxes actual defaults on the target host.
- Rootless cgroup enforcement on the target host.

### G.3 Questions only the maintainer can answer

1. Will the pilot repositories and Projects be **organization-owned or
   user-owned**? This decides whether Project projection can use an App or
   fine-grained PAT, or needs a classic/OAuth `project` credential.
2. **GitHub App or PAT** for the supervisor/publisher? An App is the only
   documented way to name a single machine actor in ruleset bypass lists and to
   write check runs. It needs App registration, private-key custody and
   installation by an owner.
3. One App for supervisor publication and a **separate** App for trusted CI, as
   plan section 4 requires separate identities?
4. Repository visibility and **plan** (Free, Pro or Team)? Private-on-Free
   cannot use rulesets.
5. Should candidates be **allowed to modify `.github/workflows/**`**? This
   requires "Workflows" write.
6. Should repository admins stay on the `main` and state-branch **bypass
   lists**? Their overrides are "outside the automation guarantee".
7. Is a long-lived App private key acceptable as an **Actions secret** for the
   fallback placement?
8. Is a host that does not meet Docker Sandboxes requirements in scope (falling
   back to rootless OCI), or must P02b target an Ubuntu 24.04+/macOS host?
