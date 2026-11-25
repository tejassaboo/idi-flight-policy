# Build notes: idi-flight-policy (wave 3, 2026-11-24)

Built from `_template` with `instantiate.py` (slug `idi`, `--task-id book-idi-flight`, `--currency NOK`,
`--background 0`, `--scenarios 24`). Frozen handbook: `pilot_work/originals/idi/frozen/idi_policy.txt`, 3,290 words
(under 10,000, so 24 scenarios), 303 lines, sha256 `83d8d0e1...abebe7`; raw PDF sha256 `a0360242...381e30`. The
source URL was not recorded (UNVERIFIED); the text itself names https://www.idi.no/our-resources/idi-administrative.
Decisions were taken without asking (the lead was away); each is recorded here.

## 1. What the handbook supports

Mandatory or checkable flight clauses (frozen line numbers):

| Lines | Clause | Operator / force | Used by |
|---|---|---|---|
| 131-132 | all travel pre-authorised by the manager (ADG) on a travel authority form | mandatory ("shall") | every staff record carries it; quartz-heath |
| 135-136 | premium economy/business: "the DG needs to be added for approval of all such travel" | mandatory | every exemption case |
| 155 | "the most direct and economical route available" | mandatory ("shall") | every booking; saffron-isle |
| 156-161 | economy default; exemption only where one leg is "more than 6 hours" or the journey "more than 9 hours", "and where travel involves overnight flights (Flights between 2200 to 0600 hours)" | strict; grouping open | 15 cases, two flags |
| 115 | night is 22:00 to 06:00 (definitions) | definition | overnight cases |
| 164 | exemptions "also" for duly certified medical reasons | permissive | nutmeg-vale |
| 165-166 | exemptions authorised by the DG for staff, the Board Chair for Board members and the DG | mandatory | plover-glen, yarrow-spit, all exemption bookings |
| 176 | courses and studies "should always be on economy class ticket" | strong should | maple-tarn |
| 234-239 | weekend at a location of personal choice: its transportation "shall not be reimbursed" | mandatory | tamarind-wold |
| 240-242 | vacation just before/after an event: "must travel economy class for that segment", price capped at the no-holiday ticket | mandatory | larch-mere |
| 57-58 | the policy "applies only to IDI staff and Board members" | scope | umber-loch |
| 251-253 | next of kin's transportation when a staff member is ill or injured on duty | permissive ("may be reimbursed") | quartz-heath, umber-loch |

Distractor clauses: lounge on a stopover "longer than three hours" (169), extra legroom "for long travels" (175),
business or premium class on train/bus (195), meals allowance hours (210-211), the 24-hour day (114), coordinators'
compensation for courses (296-297). Not used: travel agency/AmEx channel (177-180; every case books through the
tool), frequent-flyer points (181-183), excess baggage (172), hired cars and private car (184-193), travel advances
(257), claims (265-286). No rule on several travellers on one flight, so no `multi_traveller` overlay. No round-trip
case; the record has no return-date field.

## 2. Unclear points and how they are handled

- **The grouping of lines 159-161** ("One leg ... more than 6 hours ... or the total journey lasts for more than 9
  hours, and where travel involves overnight flights"): (leg or journey) and overnight, or leg or (journey and
  overnight). It splits only on a long leg flown by day. Flag `violet-crag` (490-minute daytime nonstop, exemption
  pending); twins `birch-lagoon` (long overnight leg, exemption signed: business) and `iris-shoal` (no long leg,
  long journey, daytime: economy). Every other case is on the same side under both groupings (rules.eligible
  evaluates both and raises on a split no scenario declares).
- **"the total journey"**: whether ground time counts. Flag `willow-burn` (525 minutes in the air, 605 door to door,
  overnight, exemption pending); twins `juniper-moss` (550 in the air: business) and `kelp-ridge` (540 door to door:
  economy). Every other connection is on the same side under both readings.
- **Which clock "between 2200 to 0600" uses**, and whether a flight partly in the window is "overnight". Avoided:
  every flight is either at least four hours (or wholly) inside the window on both its departure and arrival
  clocks, or wholly outside it on both; `rules.overnight` raises otherwise.
- **"most direct and economical"** (line 155) when a nonstop is dearer than a connection. Avoided: in every case the
  cheapest fare of the cabin booked also makes the fewest connections (`rules.cheapest_direct` raises otherwise),
  and background offers are off so no background nonstop can appear.
- **A DG exemption on a flight outside the criteria.** Avoided: an exemption is on file only where the criteria
  hold (or for the medical case). On the ineligible side of each twin the application is pending, and the key is
  economy (no exemption can be considered); see section 3.
- **Approval required** (`yarrow-spit`): 361-minute overnight nonstop, exemption applied for but not decided: hold the
  business fare for the DIRECTOR_GENERAL only (lines 135-136, 165). Twins `fennel-quay` (same flights, signed:
  business) and `garnet-brook` (360 minutes, pending: economy), so yarrow-spit and garnet-brook differ in one fact.

Numeric twin pairs: 361/360 minutes on one leg (fennel-quay/garnet-brook), overnight/daytime departure on a
570-minute journey with no long leg (heather-cove/iris-shoal), 550 flying minutes against 540 door to door
(juniper-moss/kelp-ridge). Next-of-kin pair (hidden_clause/refusal): quartz-heath/umber-loch.

## 3. Choices made without asking

1. **Twins differ in two facts on the exemption side.** An exemption signed for a flight that fails the criteria
   would split readers (does the DG's signature override "will only be considered"?), so each eligible side has the
   DG's exemption signed and each ineligible side has it pending. The pending application makes "hold for the DG"
   the tempting wrong answer on the ineligible side, so the twins still test the boundary; `yarrow-spit` against
   `garnet-brook` is the strict one-fact pair (361/360, both pending).
2. **Ineligible + pending = BOOK economy, not a hold.** "Such exemptions will only be considered for flights
   where ..." leaves the DG nothing to decide. Requests say "If the policy rules business out for this flight,
   book what it allows; I have to be at the <event>" (lesson 3); the same sentence is in the eligible twins.
3. **Course (maple-tarn) = economy, not a hold**, though the flight meets the criteria and an application is pending:
   line 176 "should always be on economy class ticket" with line 46 "The provisions contained in this policy are
   mandatory". Residual risk: a model may hold for the DG.
4. **Medical (nutmeg-vale)**: "Exemptions may also be made" read as a second ground that does not need the duration
   criteria; the DG's exemption is on file (line 165 still applies).
5. **Leave before the event (larch-mere)**: economy despite the DG's business exemption ("must"). The cap is met on
   every reading (economy on the leave date NOK 8,200 < economy on the usual date NOK 8,900 < business). The record
   names the usual date, so that search is pinned (lesson 8).
6. **Family members**: no sign-off on the refusal (`umber-loch`, approver NONE only); the next-of-kin booking has the
   ADG's authorisation on file (approver ADG or NONE).
7. **Approvers** (SYNC_NOTES 4'): every BOOK and REFUSE accepts NONE plus every role on file (ADG's travel authority,
   DG's or Board Chair's exemption, used or not). The approval hold accepts DIRECTOR_GENERAL only. Line 149 gives the
   class of travel to "the staff member's manager (DG/DDGs)", but exemptions are the DG's alone (lines 136, 165), so
   DEPUTY_DIRECTOR_GENERAL is not accepted there. Unclear holds accept NOT_NAMED, DIRECTOR_GENERAL,
   DEPUTY_DIRECTOR_GENERAL, ASSISTANT_DIRECTOR_GENERAL.
8. **Reasons on declined requests** (lesson 12): cabin outside the criteria accepts UPGRADE_NOT_ELIGIBLE and
   LONG_FLIGHT_CONDITION_NOT_MET, not LOWEST_FARE; course COURSE_TRAVEL_ECONOMY/UPGRADE_NOT_ELIGIBLE; leave
   VACATION_SEGMENT_ECONOMY/UPGRADE_NOT_ELIGIBLE/PERSONAL_TRAVEL_NOT_COVERED; PE-only exemption
   CABIN_EXEMPTION_AUTHORIZED/PREMIUM_ECONOMY_ALLOWED/UPGRADE_NOT_ELIGIBLE. `saffron-isle` (routing declined) keeps
   LOWEST_FARE beside DIRECT_ECONOMICAL_ROUTE, ALTERNATE_ROUTE_TOO_EXPENSIVE, COST_SAVINGS and CONNECTION_TOO_LONG,
   because line 155's economical-route rule is itself the ground.
9. **Clauses**: economy bookings accept COMMERCIAL_AIR, COMMERCIAL_TRANSPORTATION, GENERAL_CONDITIONS (line 122) and
   GUIDING_PRINCIPLES (line 103); a cabin decline accepts the two air sections; exemption bookings and holds also
   accept PRE_AUTHORISATION (135-136) and TRANSPORT_AUTHORISATION (149-151).
10. **Currency NOK**: the only currency the policy names (line 277, conversion to Norwegian kroner). Fares in øre.
11. **Travellers are mostly regional staff** (Nairobi, Johannesburg, Delhi, Cairo, Bogota) and one Board member
    (Mexico City), because the shared world has no Oslo airport (template change request below). Norway-based staff
    appear only travelling on from Copenhagen (rowan-strand).
12. **Requests carry no rule wording** (lesson 6): no "overnight", "night", "six hours" or "nine hours"; departure
    times are given as times ("the 22:30 flight", "the morning departure"). Every BOOK case has `engagement_starts`
    after every listed arrival (lesson 4), identical within each twin pair.
13. **Background offers: 0 on every search**, so each search lists only its pinned offers.
14. **Decoy reason codes** (grepped; no subject in the text): FLY_AMERICA_US_CARRIER_REQUIRED, OPEN_SKIES_AGREEMENT,
    CREATIVE_TICKETING, EXTENDED_TRAVEL_SAVINGS, DENIED_BOARDING_NOT_ALLOWED, CHANCELLOR_WRITTEN_AUTHORIZATION,
    DOUBLE_BOOKING_PROHIBITED, CANDIDATE_TRIP_NOT_COVERED, SAME_CLASS_AS_CUSTOMER, TICKET_TOTAL_APPROVED,
    CHOSEN_AIRLINE_AT_LOWEST_FARE, TRAVEL_PACKAGE_NOT_ITEMIZED. Left out: WEEKEND_TRAVEL_HOME and
    WEEKEND_TRIP_NOT_EARNED (the policy has a weekend rule) and PRIVATE_AIRCRAFT_NOT_APPROVED (line 184's
    non-scheduled transport could be argued). NEXT_OF_KIN_TRAVEL, a decoy elsewhere, is a real code here. Approver
    decoys: TRAVEL_AGENCY, CHIEF_FINANCIAL_OFFICER, HUMAN_RESOURCES, VICE_PRESIDENT, SUPERVISOR.

## 4. Mix and overlays

5 easy, 6 boundary_twin, 4 multi_rule, 2 hidden_clause, 2 distractor, 2 refusal, 3 flag (12.5%). Decisions: 19 BOOK
(6 business, 2 premium economy, 11 economy), 2 REFUSE, 3 FLAG.
Overlays: multi_leg 6, date_arithmetic 2 (month_end 1), personal_travel 2, dearer_option 9, upgrade_not_taken 2,
outside_air_section 4. Degenerate agents: always-flag passes 2, always-cheapest passes 4 (aspen-fjord, dune-sorrel,
quartz-heath, saffron-isle; 17%). `MAX_PASS_ALWAYS_FLAG = 2`, `MAX_PASS_ALWAYS_LOWEST = 4`.

## 5. Independent blind read (non-flag scenarios)

Re-derived from the frozen text and the tool outputs only (the `get_trip` record and every pinned `search_flights`
listing, dumped per scenario with local and UTC times), not from rules.py, then compared with `expected`.

| Scenario | My reading from text + offers | Agrees |
|---|---|---|
| aspen-fjord | economy asked though a business exemption is on file; LH 7,450 sold out; cheapest seated economy SA 7,980 | yes |
| birch-lagoon | 505/510-minute nonstops leaving 23:30/23:55, overnight; DG exemption: cheapest business KQ 31,800 | yes |
| cobalt-tern | 265-minute day flight: no criterion met; economy, EgyptAir 3,650 | yes |
| dune-sorrel | economy asked; cheapest Air India 5,250 | yes |
| ember-kestrel | 485 minutes leaving 01:00/01:40; DG exemption for PE: Air India PE 9,200 | yes |
| fennel-quay | KQ 361 minutes (> 6 h), 22:30-07:01, overnight; signed: KQ business 21,500 | yes |
| garnet-brook | KQ 360 minutes: not "more than 6 hours", journey 360: no exemption possible despite the pending form; KQ economy 4,300 | yes |
| heather-cove | 210 + 360 minutes, 570 in the air (> 9 h either way); DOH-CPH 22:45-02:45: eligible on both groupings; QR business 33,800 | yes |
| iris-shoal | same, 09:00 departure, all daytime: no long leg, no overnight flight: economy QR 6,100 | yes |
| juniper-moss | 285 + 265 = 550 in the air; CAI-CPH 00:45-04:10: eligible; MS business 26,500 | yes |
| kelp-ridge | 540 minutes door to door, 405 in the air: not over 9 h; no long leg: economy MS 4,800 | yes |
| larch-mere | leave before the event: economy for that segment (240-242); KLM 8,200 below the usual date's 8,900 | yes |
| maple-tarn | a course: always economy (176); SA 7,700 | yes |
| nutmeg-vale | certified medical reason (164) and DG exemption; KQ business 14,800 | yes |
| oriole-peak | eligible, but the exemption allows PE only: Avianca PE 12,600 | yes |
| plover-glen | Board member, the Chair's exemption (165), 680 minutes overnight: AM business 44,500 | yes |
| quartz-heath | next of kin of a staff member injured on duty (251-253), ADG authorised: KQ economy 3,400 | yes |
| rowan-strand | 80 minutes: economy; train/bus class rule irrelevant; LH 11:15 1,690 lands 12:35 before 15:00 | yes |
| saffron-isle | LH via FRA 4,100 and 390 min against TK via IST 4,450 and 525 min: LH (155); lounge irrelevant | yes |
| tamarind-wold | weekend at a place of personal choice (234-239): refuse | yes |
| umber-loch | a family member joining, no illness: outside the policy (57-58): refuse | yes |

21 of 21 non-flag scenarios agree. The read found two accept-set gaps, both fixed before the first commit:
larch-mere now also accepts PERSONAL_TRAVEL_NOT_COVERED (the leave is the ground), and saffron-isle also accepts
CONNECTION_TOO_LONG (the Istanbul stop is what is declined). The flags were read too: each has two readings that give
different bookings, quoted in `ambiguity_note`.

## 6. Hosted-cap estimate

Full-handbook prompt: 22,100 bytes, 3,290 words; about 4,400 tokens at 1.33 a word, about 6,200 on the Thornton/NJC
calibration (0.2 a character plus 1,800). A 3-call run is about 20,000 input tokens before the final message (about
28,000 with it): far under the 65,536 cap.

## 7. Template change requests

1. **Add Oslo (OSL, Oslo Gardermoen, NO, UTC+60) and a Scandinavian carrier** (SAS `SK`, hubs CPH/OSL/ARN, or
   Norwegian `DY`, hub OSL) to the shared `world.py`. The IDI is Oslo-based and most of its staff fly from Oslo; the
   world has no Norwegian airport, so this plugin uses regional staff and Copenhagen instead. A new carrier with hubs
   at existing airports (CPH) can add background itineraries to other plugins' routes, so run `tools/world_diff.py`
   before adopting it; OSL alone (no new hub) changes nothing.
2. Observation (no change needed): the shared conventions sentence mentions a trip record's return date; this
   record has no such field, as in Standex.

## 8. Acceptance outputs

```
$ uv run pytest -q
209 passed in 1.62s
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages in 9ms
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .
exit 0
$ nanoagent plugin pack . /tmp/idi-flight-policy.tar.gz
packed . into /tmp/idi-flight-policy.tar.gz (156989 bytes)
$ python ../_template/tools/stock_verify.py .
aspen-fjord          right=True score=1.00 identical=True wrong-decision-rejected=True
birch-lagoon         right=True score=1.00 identical=True wrong-decision-rejected=True
cobalt-tern          right=True score=1.00 identical=True wrong-decision-rejected=True
dune-sorrel          right=True score=1.00 identical=True wrong-decision-rejected=True
ember-kestrel        right=True score=1.00 identical=True wrong-decision-rejected=True
fennel-quay          right=True score=1.00 identical=True wrong-decision-rejected=True
garnet-brook         right=True score=1.00 identical=True wrong-decision-rejected=True
heather-cove         right=True score=1.00 identical=True wrong-decision-rejected=True
iris-shoal           right=True score=1.00 identical=True wrong-decision-rejected=True
juniper-moss         right=True score=1.00 identical=True wrong-decision-rejected=True
kelp-ridge           right=True score=1.00 identical=True wrong-decision-rejected=True
larch-mere           right=True score=1.00 identical=True wrong-decision-rejected=True
maple-tarn           right=True score=1.00 identical=True wrong-decision-rejected=True
nutmeg-vale          right=True score=1.00 identical=True wrong-decision-rejected=True
oriole-peak          right=True score=1.00 identical=True wrong-decision-rejected=True
plover-glen          right=True score=1.00 identical=True wrong-decision-rejected=True
quartz-heath         right=True score=1.00 identical=True wrong-decision-rejected=True
rowan-strand         right=True score=1.00 identical=True wrong-decision-rejected=True
saffron-isle         right=True score=1.00 identical=True wrong-decision-rejected=True
tamarind-wold        right=True score=1.00 identical=True wrong-decision-rejected=True
umber-loch           right=True score=1.00 identical=True wrong-decision-rejected=True
violet-crag          right=True score=1.00 identical=True wrong-decision-rejected=True
willow-burn          right=True score=1.00 identical=True wrong-decision-rejected=True
yarrow-spit          right=True score=1.00 identical=True wrong-decision-rejected=True
24 scenarios, 0 failures
```
