# Build Remora, then put Remora in charge

1. **Bootstrap now:** human assignment, fresh independent review and manual
   integration. Use the source plan and checked manifest. No distributed claims,
   runtime trust or automated Done semantics are claimed.
2. **M0:** complete P01; run P02a and P02b as separate spikes. Within P02a assess
   gh-aw and test the narrow adapter concurrently. Hold the three-day gh-aw box.
   Require the joint A17 stop/fencing result before M0 exit. P03 can proceed after
   P01, independently of spike outcomes.
3. **M2:** exercise the implemented controller on disposable tasks in explicit
   `unverified_pilot` mode. Do not migrate the live Remora backlog merely because
   the demo loop ran. Manual pilot acceptances remain distinguishable from PASS.
4. **After P09 and relevant qualification:** propose a Remora self-hosting cutover.
   The human decides whether the demonstrated safety/evidence profile is adequate.
   This is separate from the mandatory Weave migration in P12.
5. **P11/P12:** qualify the integrated release and conduct the specified two-project
   pilot. Remora dogfooding is useful additional evidence; it does not replace
   Weave plus a differently configured existing project.

## Remora cutover checklist

- Pause bootstrap intake and active work. Confirm no active developer/reviewer or
  unresolved publication; an expired claim is not proof of physical termination.
- Archive task definitions, issue decisions, candidate references and every review
  round across attempts. Resolve ambiguous counts with the human before import.
- Record policy/plan revisions and a cutover decision. Import manual completions
  with their actual evidence provenance; do not relabel them trusted CI.
- Initialize one authority epoch without importing live claims. Disable the old
  assignment convention, scripts or triggers that could still change authority.
- Verify blockers, questions, budgets, candidates and completion mappings. Enable
  one selected backend only after a reviewable reconciliation diff is accepted.
- For rollback, fence/drain the new controller and map newer work back explicitly.
  Never restore an old snapshot over newly completed work.

No automated self-hosting cutover is shipped in this starter.
