# P01 licence report

Status: proposed P01 synthesis from `weave-inventory.md` §A and `upstream-surfaces.md` §1.1,
§2, §3; machine-readable pins in `contracts/upstream-pins.v1.json`. This is an engineering
inventory of licence files and notice obligations, **not legal advice**. No upstream code
has been copied into Remora by P01.

## Remora's own licence

**Undecided.** `NOTICE.md` states that no distribution licence has been selected, that no
upstream implementation was copied, and that Remora's licence must not be inferred from a
dependency's licence. P01 does not change `NOTICE.md` and makes no licence recommendation
(README Q13).

## Per pinned upstream

| Upstream (commit) | Licence (SPDX basis) | Licence file digest (SHA-256) | Notice files | Copyright line |
| --- | --- | --- | --- | --- |
| Weave `e7c3f3cab1e25994b96a948cbe27c96bb061d5a8` | MIT; text matches the template and `LICENSES/MIT.txt` is byte-identical; `REUSE.toml:15-92` annotates `tools/weave_workflow/**`, `docs/development/*.md`, `.claude/**`, `.github/**` as MIT; maintainer decision `docs/decisions/0002-licence-terms.md` | `LICENSE` `b578d9a7c9556921a95db16fe27e74c6526fa9b71c4bbf0a2da68037534f0b71` | No root NOTICE. Other licence texts (BSD-2-Clause, Bitstream-Vera, LicenseRef-Arev-Fonts, OFL-1.1-RFN) cover specification PDFs, fonts and `weave.sty`, not the controller | "Copyright (c) 2026 Thomas F. Hagelien" |
| Weave baseline `d8010aec6746bbdcc54b21801c537d28917c0533` | MIT (same `LICENSE`); controller paths identical to the pin | same | same | same |
| gh-aw `28f2101d8af447fdb90ffd70dd2579e4ad64a21c` | MIT; SPDX inferred from text, not declared in the file | `2510b446bc1f0cf9702453075d20cd88631e20e5642658edb7325d9c1eb534f7` | No top-level NOTICE found | "Copyright GitHub, Inc." |
| Symphony `be10a1b79df723d6d7612b5651c8522704dafb2e` | Apache-2.0 (text; `README.md:41`) | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` | `NOTICE` "Copyright 2025 OpenAI", `38c76eb8701e52953f63154a77b407667a6ee34c3a2a8785c8f8b2cd5494d09d` | (in NOTICE) |
| Beads `e226083653b893998614df4225f73b6688ca9166` | MIT; SPDX inferred ("MIT License" heading) | `caa2c60efbbf71e18b45ef6006a18213f8a42554b235af88883f6f1ec240b7db` | `THIRD_PARTY_LICENSES` lists Dolt and go-mysql-server under Apache-2.0, `50b7ae5d2cbdb67ff26f255f118002241ff27bc2ad0535d0c4ec7639b12224aa` | "Copyright (c) 2025 Beads Contributors" |

## What reuse would require

| Upstream | Proposed use (contract-comparison) | Copying source into Remora | Depending without copying |
| --- | --- | --- | --- |
| Weave | Reuse-as-is or reuse-with-adapter of generic controller modules (`schema.py`, digests, scheduler, gates, review binding, integration, ordering); see `weave-migration-boundaries.md` §4 | MIT condition: keep the copyright and permission notice in copies or substantial portions (`W:LICENSE:12-13`). Add an attribution section to `NOTICE.md` and per-file SPDX/copyright annotations. That edit is outside P01's allowed paths: `scope-requests.md` item 1 | The controller is not identified as a published package in the research [inference]; a Git submodule or vendored copy is still copying for notice purposes [inference] |
| gh-aw | Fallback backend candidate; safe-output *pattern* | Copying handlers (`actions/setup/js/*.cjs`) would need the MIT notice | Using the `gh aw` extension and SHA-pinned actions does not place gh-aw source in Remora; generated `.lock.yml` files would live in consuming repositories. The licence status of compiler-generated workflow files is **unverified** |
| Symphony | Vocabulary only (`WORKFLOW.md` layout, `dispatchable`, `blocked_by`) | Apache-2.0: include the licence, retain the NOTICE content, mark modified files (Apache-2.0 section 4) [documented by licence text; not re-read for P01] | Running Symphony is not proposed for the pilot |
| Beads | Readiness-explanation shape only | Copying Go types would need the MIT notice; Dolt-related code adds Apache-2.0 third-party terms | Not adopted (plan section 2) |

Borrowing vocabulary or a data shape without copying code is not, in itself, treated as
copying here; whether a specific borrowed text is "substantial" is a human/legal question.

## Flags for the human owner (not assessed)

- Weave records that commits touching `tools/weave_workflow/` carry `Co-Authored-By`
  trailers naming an AI coding assistant, with a single human author
  (`W:docs/decisions/0002-licence-terms.md:259-267`). No legal assessment is made.
- Whether the Weave rights holder and the Remora owner are the same person is **unverified**.
- `W:REUSE.toml:9` says Weave's REUSE metadata "is not a completed provenance audit".
- gh-aw's canonical repository is `github/gh-aw`; the plan's `githubnext/gh-aw` resolved
  to the same SHA, but a formal redirect was not verified.
