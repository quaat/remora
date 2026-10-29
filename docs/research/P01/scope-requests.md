# P01 scope requests (changes outside P01's allowed paths)

P01 may edit only `docs/research/P01/**`, `docs/decisions/**`, `contracts/**` and
`tests/contracts/**`. The changes below are proposed for the human to approve and assign;
none has been made.

## 1. `NOTICE.md` attribution when Weave code is first copied

- **When:** only when a later task (likely P03, P05 or P08) actually copies Weave source.
  P01 copied nothing, so `NOTICE.md` is accurate today.
- **Prerequisite:** README Q13 (Remora licence) and Q14 (copy vs re-implement).
- **Proposed text to add** (adjust once the files are known):

  ```text
  Portions of src/remora/... are derived from Weave
  (https://github.com/quaat/weave, commit e7c3f3cab1e25994b96a948cbe27c96bb061d5a8),
  Copyright (c) 2026 Thomas F. Hagelien, licensed under the MIT License.
  The MIT licence text is reproduced in LICENSES/MIT.txt. Copied files carry
  SPDX-License-Identifier and SPDX-FileCopyrightText headers.
  ```

- Replace the sentence "No Weave, Symphony, gh-aw, Beads or other upstream implementation
  was copied" with an accurate list.
- Requester: the copying task, through its issue. Policy-affecting; needs explicit review.

## 2. `.remora/bootstrap-policy.json` pointer to the matrix

- Current value: `"permission_matrix": "not yet implemented; P01 deliverable"`.
- Proposed: `"permission_matrix": "contracts/permission-matrix.v1.json (proposed, matrix_version 1.0.0; human decisions DP-01..DP-09 open)"`,
  after P01 is accepted.
- Policy file; the review packet binds its digest, so the change needs its own review.

## 3. `docs/development/validation.md` test count

- It records "45 tests passed". After P01 the suite has 71 tests (45 bootstrap + 26
  contract tests under `tests/contracts/`). Update the validation record when P01 is
  integrated, with the actual run provenance.

## 4. No change requested

- `.github/workflows/ci.yml` already runs `python3 -m unittest discover -s tests -v`, which
  discovers `tests/contracts/` (it has `__init__.py`). No CI edit is needed.
- `AGENTS.md`, `README.md`, `.remora/tasks.json` and `bootstrap/**`: no change required by
  P01's deliverables.
