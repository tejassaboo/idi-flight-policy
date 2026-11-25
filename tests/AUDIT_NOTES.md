# Independent audit: idi-flight-policy (2026-11-25)

Audited the builder's commit 979a20b against `pilot_work/tier_plan/build/WAVE3_AUDIT_BRIEF.md`, the wave 3 build
brief (lessons 1-12), MASTER_PLAN section 4 and EDGE_CASES sections 1-3 and 5. No money spent, nothing pushed. Line
numbers are lines of the frozen handbook (`src/plugin/data/policy.txt`).

## Method

I printed every scenario's `get_trip` record and every pinned `search_flights` listing through the plugin's own
tools, with local and UTC times. I then answered each case from the handbook alone (lines 57-58, 115, 122-123,
131-136, 149, 155-166, 169, 176, 195, 234-242, 251-253), and only afterwards compared my answers with the accept sets
(decision, offer, cabin, reason, approver, clause).

## Verdict

**Pass after one fix.** Every decision and offer in the key agrees with my reading on all 21 non-flag cases. The
three flags are sound:

- `violet-crag` (a 490-minute daytime nonstop, 08:00-18:10) splits only on the grouping of "or ... and where travel
  involves overnight flights" (lines 159-161). Both held offers are accepted.
- `willow-burn` (525 minutes in the air, 605 door to door, the first leg overnight) splits only on whether "the total
  journey" counts the time on the ground. Both held offers are accepted.
- `yarrow-spit` is clear on the text: the flight qualifies, and the exemption is pending with the DG.

The request lint passes, the requests carry no thresholds, and the decline sentence is in the task instructions.
Every BOOK has `engagement_starts` after every listed arrival.

## Defect found and fixed: twins differed in two facts

On the exemption side, each boundary pair differed in two facts: the flight, and whether the exemption was signed
(eligible side) or pending (ineligible side).

- **The pairs:** `fennel-quay`/`garnet-brook`, `heather-cove`/`iris-shoal`, `juniper-moss`/`kelp-ridge`.
- **The fix:** each ineligible twin now has the same signed DG business exemption as its partner, and the same request
  words. The request in all six cases says: "The DG has signed my exemption for business, provided the flight
  qualifies under the policy." The fallback sentence (lesson 3) is kept.
- **What each pair now differs in:**
  - `fennel-quay`/`garnet-brook`: 361 or 360 minutes.
  - `heather-cove`/`iris-shoal`: the Delhi departure, 20:30 or 09:00.
  - `juniper-moss`/`kelp-ridge`: the journey. That is 550 flying minutes to Copenhagen, or 540 minutes door to door to
    Istanbul. The destination has to change to get under 9 hours, as before.
- **Why the conditional clause is needed:** a bare DG signature on a flight outside the criteria would split readers.
  One reader would say "the DG authorised it, book business". Another would say "such exemptions will only be
  considered for flights where ...", so it is void. The builder was right about that, so a plain "both signed" would
  have created a split-reader case. Saying the signature is conditional on the flight qualifying removes the
  deferential reading. It names no threshold and no rule wording (lesson 6), and the twins carry it identically.
- **What changed in the key:** the ineligible twins stay BOOK economy, with the same reasons
  (`UPGRADE_NOT_ELIGIBLE`, `LONG_FLIGHT_CONDITION_NOT_MET`) and clauses. Their approver set grows to
  {ASSISTANT_DIRECTOR_GENERAL, DIRECTOR_GENERAL, NONE}, because the unused exemption is now on file (SYNC_NOTES 4(b),
  as in `aspen-fjord`).
- **Rules change:** `rules.premium` no longer raises on an exemption granted for a flight outside the criteria. It
  returns the economy answer. Both copies of `rules.py` are byte-identical.
- **`yarrow-spit`:** it is now the one-fact partner of `fennel-quay` (pending or signed, same flights) and stays one
  minute from `garnet-brook`.
- **Small error corrected:** the `juniper-moss` twin_fact said "620 door to door". It is 610 (285 + 60 + 265).
- Ids, worlds and categories are unchanged.

`quartz-heath`/`umber-loch` (the next-of-kin pair) still differ in the illness and the ADG's authorisation. I kept
this on purpose, because either one-fact variant creates a split-reader case:

- If `umber-loch` also had the ADG's authorisation, some readers would book the companion because the manager signed.
- If the authorisation were removed from `quartz-heath`, some readers would hold under line 131 ("All travel ... shall
  be pre-authorised").

The authorisation is a consequence of the injury, so the pair tests one condition.

## The builder's unsure list, settled

1. **Twins in two facts:** fixed as above.
2. **Pending application on a non-qualifying flight keyed BOOK economy.** With the fix, no non-qualifying flight has a
   pending application any more: the three ineligible twins now carry a conditional signature. The pending cases left
   are `yarrow-spit` (it qualifies, so it is held), the two flags, and `maple-tarn`. The question of whether to hold
   for the DG no longer arises.
3. **`maple-tarn` (course): economy, not a hold.** Kept.
   - Line 176 says "should always be on economy class ticket", and line 46 says the provisions are mandatory.
   - The exemption mechanism of lines 156-161 is about the flight. Line 176 is about the purpose of the travel, so the
     DG has nothing to decide.
   - The traveller's own fallback ("If the policy rules business out ... book what it allows") makes BOOK economy
     the answer a careful reader gives.
   - The pending application is kept on purpose: it is what makes missing line 176 visible (an agent that misses it
     holds, as in `yarrow-spit`).
   - The answer format has only one decision per case, so a hold cannot be accepted alongside the BOOK. The residual
     risk is a model that holds anyway.
4. **`nutmeg-vale` (medical ground without the duration criteria): business.** Kept.
   - Line 164 is its own numbered paragraph: "Exemptions may **also** be made for duly certified medical reasons".
     That is a second, separate ground, not a sub-case of the flight criteria.
   - The certificate and the DG's business exemption are both on file.
   - Reading the duration criteria into line 164 would make it redundant. I do not count that as a defensible
     second reading.
5. **Approver on `yarrow-spit`: DIRECTOR_GENERAL only, no DEPUTY_DIRECTOR_GENERAL.** Kept.
   - Line 149 gives "the staff member's manager (DG/DDGs)" the class of travel in general.
   - The specific exemption clauses name the DG alone. Line 136: "the DG needs to be added". Line 165: "authorized by
     IDI Director General for all IDI staff". Line 166: "applied to the Director General only".
   - The trip record and the request both say the application went to the DG.
   - The awaited sign-off is the DG's, and naming a DDG names someone who is not deciding.
   - On the two unclear holds, DDG stays accepted, because what is open there is whether an exemption can be
     considered at all, and line 149 then applies.

## Seen and kept

- `iris-shoal`: the Delhi-Doha flight is 03:30-07:00 UTC, inside 22:00-06:00 only on the UTC clock. It is 09:00-12:30
  Delhi time and 06:30-10:00 Doha time. Night in line 115 is local, so no reasonable reader calls it overnight.
- `willow-burn`: the Delhi-Istanbul leg is 01:30-07:25 on the Delhi clock and 23:00-04:55 on the Istanbul clock, so it
  is overnight on any reading. Only the journey phrase is open.
- `larch-mere`: the cap of lines 240-242 holds on every reading. NOK 8,200 is below the usual date's economy fare of
  8,900, which is below business.
- `saffron-isle` keeps LOWEST_FARE, because line 155's economical-route rule is itself the ground for the decline
  (lesson 12).
- `rowan-strand`: the 11:15 flight lands at 12:35, before the 15:00 meeting.

`MAX_PASS_ALWAYS_LOWEST`: **4 -> 4** (`aspen-fjord`, `dune-sorrel`, `quartz-heath`, `saffron-isle`; 17%). The cases that
changed are keyed with `UPGRADE_NOT_ELIGIBLE`/`LONG_FLIGHT_CONDITION_NOT_MET`, so a `LOWEST_FARE` answer still fails
there. `MAX_PASS_ALWAYS_FLAG` is still 2.

## Files changed

- `src/plugin/rules.py` and `verifier/rules.py` (byte-identical): an economy answer on an ineligible flight with an
  exemption on file.
- `tests/build_scenarios.py`: the `SIGNED` sentence, six requests, three trip records, three approver sets, design
  notes and twin facts.
- 7 scenario JSON files, regenerated.
- `README.md`: the `garnet-brook` row.

## Check outputs (audit commit)

- `uv run pytest -q`: 209 passed.
- `uv run ruff check .`: all checks passed.
- `uv lock --check`: ok.
- `python3 ../_template/check_shared.py .`: ok.
- `tools/stock_verify.py .`: 24 scenarios, 0 failures.
- `nanoagent plugin inspect .`: exit 0.
