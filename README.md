# IDI Travel Policy Flight Booking

**Source of the handbook:** https://idi.no/wp-content/uploads/2024/10/2025-IDI-Travel-Policy.pdf. The agent reads it verbatim (bundled at `src/plugin/data/policy.txt`); flights, fares and trips are synthetic.

**No affiliation with the INTOSAI Development Initiative (IDI).** The handbook is the IDI's *IDI Travel Policy*
(2025 edition, effective 1 December 2025), a published nonprofit policy (the text names
https://www.idi.no/our-resources/idi-administrative; the source URL of the pinned PDF was not recorded and is
unverified), bundled verbatim for research. Every traveller, name and sign-off in the scenarios is invented.

A `nanoagent.plugin/v0001` plugin. An agent handles one traveller's flight request under the IDI's real travel
policy: it reads the trip record, searches a simulated flight world and submits **BOOK**, **REFUSE** or
**FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and policy section. A deterministic Python verifier,
with no LLM, rebuilds the offers and the policy's answer itself and checks every field. Built from the
original-handbook template (`handbook_plugins/_template`); `tests/build_scenarios.py` writes the scenario files.

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 3,290 words, 303 lines, 22,100 bytes, sha256 `83d8d0e1...abebe7`,
equal to `pilot_work/originals/idi/frozen/SHA256SUMS`) is never paraphrased, and the task text restates no rule.
Under stock NanoAgent the agent does not see it: the plugin then runs as the `off` baseline. The `harness.policy`
switch of the NanoAgent fork (github.com/tejassaboo/nanoagent, branch `policy-switch`) adds it to the system prompt:
`harness.policy: full` adds all of it, and the selection methods add parts of it. These plugins are meant to run
with `query: instructions+input`, so a selector sees the traveller's request.

**Size.** At 1.33 tokens a word the policy alone is about 4,400 tokens; calibrated on the paid Thornton and NJC runs
(about 0.2 tokens a character plus 1,800) the first `full` call is about 6,200 input tokens. A run makes 3 calls
(`get_trip`, `search_flights`, `submit`) of about 6,200, 6,600 and 7,000 to 7,600 (2 to 8 offers): about 20,000 input
tokens per run, plus about 7,800 for the final message. Far under the hosted cap of 65,536, even with repeated
searches. `larch-mere` pins a second search (the usual travel date its record names).

## Task

- **Input:** `TaskInput`: `scenario` (one of 24 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on the trip's route and date (every case buys one one-way ticket),
  then `submit`.
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when refusing),
  `reason_code`, `approver` and `clause`, each from a closed list. The reason list is the template's shared list plus
  five codes of this policy (`CABIN_EXEMPTION_AUTHORIZED`, `COURSE_TRAVEL_ECONOMY`, `VACATION_SEGMENT_ECONOMY`,
  `NEXT_OF_KIN_TRAVEL`, `DIRECT_ECONOMICAL_ROUTE`) and twelve decoy codes from other handbooks' rules. Fares are in
  øre of Norwegian kroner (`currency: NOK`; the policy converts claims to NOK, line 277).
- **Success:** every field is one the answer key accepts; the cabin is graded as the chosen offer's own. Score =
  fields right / 6.
- **Reasons on a declined request.** The task instructions say that when the booking is not what the traveller asked
  for, the reason code gives why the request is declined. Such a booking accepts only the codes that name the
  policy's ground, not `LOWEST_FARE`: a cabin outside the criteria (`UPGRADE_NOT_ELIGIBLE`,
  `LONG_FLIGHT_CONDITION_NOT_MET`), a course (`COURSE_TRAVEL_ECONOMY`), leave before the event
  (`VACATION_SEGMENT_ECONOMY`), an exemption for premium economy only (`CABIN_EXEMPTION_AUTHORIZED`,
  `PREMIUM_ECONOMY_ALLOWED`). `saffron-isle` keeps `LOWEST_FARE`, because line 155's "most direct and economical
  route" is itself the ground for declining the routing asked for.
- **No hidden facts:** no scenario has `answer_key_inputs`.

| Scenario | Category | Expected decision (offer; cabin) | Frozen lines |
|---|---|---|---|
| `aspen-fjord` | easy | BOOK (saa-economy; ECONOMY): exemption on file, economy asked | 155, 156-161 |
| `birch-lagoon` | easy | BOOK (kenya-business; BUSINESS) | 115, 135-136, 156-161, 165-166 |
| `cobalt-tern` | easy | BOOK (egyptair-economy; ECONOMY): 265-minute day flight | 155, 156-161 |
| `dune-sorrel` | easy | BOOK (airindia-economy; ECONOMY) | 155, 156-161 |
| `ember-kestrel` | easy | BOOK (airindia-premium; PREMIUM_ECONOMY) | 135-136, 156-161, 165-166 |
| `fennel-quay` | boundary_twin | BOOK (kenya-business; BUSINESS), 361 minutes, exemption signed | 115, 135-136, 156-161, 165-166 |
| `garnet-brook` | boundary_twin | BOOK (kenya-economy; ECONOMY), 360 minutes, the same signed exemption | 155, 156-161 |
| `heather-cove` | boundary_twin | BOOK (qatar-business; BUSINESS), 570 flying minutes, overnight | 115, 135-136, 156-161, 165-166 |
| `iris-shoal` | boundary_twin | BOOK (qatar-economy; ECONOMY), the same by day | 115, 155, 156-161 |
| `juniper-moss` | boundary_twin | BOOK (egyptair-business; BUSINESS), 550 flying minutes | 115, 135-136, 156-161, 165-166 |
| `kelp-ridge` | boundary_twin | BOOK (egyptair-economy; ECONOMY), 540 minutes door to door | 155, 156-161 |
| `larch-mere` | multi_rule | BOOK (klm-economy; ECONOMY): leave before the event | 156-161, 165-166, 240-242 |
| `maple-tarn` | multi_rule | BOOK (saa-economy; ECONOMY): a course | 156-161, 176 |
| `nutmeg-vale` | multi_rule | BOOK (kenya-business; BUSINESS): certified medical reason | 156-161, 164, 165-166 |
| `oriole-peak` | multi_rule | BOOK (avianca-premium; PREMIUM_ECONOMY): exemption for premium economy only | 135-136, 156-161, 165-166 |
| `plover-glen` | hidden_clause | BOOK (aeromexico-business; BUSINESS): Board member, the Chair's exemption | 115, 156-161, 165-166 |
| `quartz-heath` | hidden_clause | BOOK (kenya-economy; ECONOMY): next of kin of an injured staff member | 131-132, 156-161, 251-253 |
| `rowan-strand` | distractor | BOOK (midday-economy; ECONOMY): train/bus class rule | 155, 156-161 |
| `saffron-isle` | distractor | BOOK (lufthansa-economy; ECONOMY): lounge on a long stopover | 122-123, 155 |
| `tamarind-wold` | refusal | REFUSE: weekend at a place of personal choice | 234-239 |
| `umber-loch` | refusal | REFUSE: a family member joining a workshop | 57-58, 251-253 |
| `violet-crag` | flag | FLAG_FOR_APPROVAL (emirates-business or emirates-economy), UNCLEAR_POLICY_TEXT (or APPROVAL_REQUIRED) | 115, 135-136, 156-161, 165-166 |
| `willow-burn` | flag | FLAG_FOR_APPROVAL (turkish-business or turkish-economy), UNCLEAR_POLICY_TEXT (or APPROVAL_REQUIRED) | 115, 135-136, 156-161, 165-166 |
| `yarrow-spit` | flag | FLAG_FOR_APPROVAL (kenya-business; BUSINESS), APPROVAL_REQUIRED, DIRECTOR_GENERAL | 115, 135-136, 156-161, 165-166 |

Every accepted reason, approver and section per case is in the scenario files and `tests/BUILD_NOTES.md`.

**Duration (`rules.over`, `rules.overnight`, `rules.eligible`).** Lines 156-161: premium economy or business "will
only be considered for flights where: One leg of the journey lasts for more than 6 hours ... or the total journey
lasts for more than 9 hours, and where travel involves overnight flights (Flights between 2200 to 0600 hours)". The
`leg` rule is one flight over 360 scheduled minutes (strict); the `journey` rule is over 540 minutes, True when the
flights alone add to more than 540, False when the first departure to the last arrival is 540 or less, unclear in
between (only `willow-burn`). A flight is overnight when at least four hours of it (or all of it) fall in 22:00-06:00
on both its departure and arrival clocks, and not overnight when none does. The grouping of "or ... and where travel
involves overnight flights" is read both ways; it splits only on a long daytime leg (only `violet-crag`).

**Approvers.** A BOOK or REFUSE accepts `NONE` and the role of every sign-off on file (the ADG's travel authority,
the DG's or Board Chair's exemption; SYNC_NOTES 4'). A hold awaiting the exemption accepts only the role line 165
names (`yarrow-spit`: `DIRECTOR_GENERAL`). A hold over unclear words accepts `NOT_NAMED`, `DIRECTOR_GENERAL`
(exemptions, lines 135-136 and 165), `DEPUTY_DIRECTOR_GENERAL` and `ASSISTANT_DIRECTOR_GENERAL` (the manager who
authorises the class of travel, lines 131 and 149).

Degenerate agents (`tests/test_verifier.py`): always holding the right offer as unclear passes 2 cases (the two
unclear flags); always booking the cheapest seat with `LOWEST_FARE`, `NONE` and the right section passes 4.

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller, route, date, purpose and start of the work, cabin and connection asked for, leave attached, medical certificate, sign-offs and a pending application | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date: the pinned scenario offers only (no background offers); a search the case does not pin lists nothing and says so | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-idi-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this policy's scenario ids, approvers, sections, reason codes
  and trip record.
- `src/plugin/`: `world.py`, `scenarios.py`, `guide.py`, `answer.py`, `tools.py` (shared), `rules.py` (this
  policy's rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of the shared modules and `rules.py`, plus `booking.py` and `tools.py`.
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this policy's settings.
- `tests/build_scenarios.py`: writes the scenario files (an authoring aid, not a test).
- `tests/BUILD_NOTES.md`: design choices, the blind read and the acceptance outputs.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 ../_template/check_shared.py .
# from a NanoAgent checkout (read-only use):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/idi-flight-policy.tar.gz
# from this folder, with that checkout's Python:
/path/to/nanoagent/nanoagent/.venv/bin/python ../_template/tools/stock_verify.py .
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`).
