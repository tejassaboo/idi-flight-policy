# Validation notes: idi-flight-policy (paid wave 3 validation, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w3_2026-11-25/idi-flight-policy@w3/`, arm
`full`, DeepSeek V4 Flash (Nebius), temperature 0, max_steps 6, max_tokens 8192, one run per scenario, at plugin
head f0cbbf5. Line numbers are lines of `src/plugin/data/policy.txt`.

## Results

21/24 valid (87.5%), mean field score 0.965, **easy 3/5** (aspen-fjord, ember-kestrel). Flags 2/3. $0.00120
billed per run, 4.0 calls per run, 8,164 prompt tokens per call.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| aspen-fjord | **easy** | right offer (SAA economy), approver and clause; reason COST_SAVINGS; key LOWEST_FARE only | **grader defect (narrow)** | The request: "The DG signed an exemption so I could go business, but our project budget is tight this year, so please put me in economy." The model: "The traveller explicitly said 'our project budget is tight this year' ... So we book economy for cost savings. Reason code COST_SAVINGS seems appropriate." The traveller sets aside a signed exemption to save money, and line 155 ("most direct and economical route") is the ground. uk-dbt cobalt-weir and alder-pennant (easy, a signed business form set aside to keep the cost down) and Standex sage-tundra key `COST_SAVINGS` beside `LOWEST_FARE` on the same facts. |
| ember-kestrel | **easy** | KLM premium economy 01:00 ($9,800); key Air India premium economy 01:40 ($9,200) | **scenario defect: the request names one flight, the world has two** | The request asked for "the early-morning departure", but both nonstops leave in the early morning (01:00 and 01:40). The model: "the request says 'the early-morning departure' singular, implying there's a specific early-morning flight they want ... I'll pick the earliest, KLM". It weighed line 155 ("Air India premium economy is cheaper") and let the definite article decide. The key (the cheaper of two qualifying flights) is right; the wording pointed at a single flight. |
| violet-crag | flag | BOOK Emirates economy, LONG_FLIGHT_CONDITION_NOT_MET; key FLAG | model slip | It read lines 159-161 one way only: "business class is only allowed ... where a leg exceeds 6 hours **and** the travel involves an overnight flight", and never weighed the reading where the overnight condition attaches to the journey test alone (the unclear phrase). The twins birch-lagoon and iris-shoal passed. |

## Fixes (this commit)

1. **aspen-fjord (grader):** `COST_SAVINGS` accepted beside `LOWEST_FARE` on an economy request that sets a signed
   cabin exemption aside (`economy()` in `src/plugin/rules.py` and the byte-identical `verifier/rules.py`; the key in
   `tests/build_scenarios.py`). Only aspen-fjord has an exemption on file with an economy request.
2. **ember-kestrel (scenario):** the request now reads "on one of the early-morning departures". Same flights, fares,
   key and id.
3. **birch-lagoon, oriole-peak and plover-glen (latent, same defect):** "the late-evening departure" (23:30 and
   23:55) and "the evening flight" (18:30 and 20:00; 17:30 and 18:45) also named one flight where the world has two
   qualifying ones. They now read "on one of the late-evening departures" and "on one of the evening flights". All
   three passed this run; in each the key is the cheaper flight, which is also the earlier one. plover-glen's
   change is a follow-up commit, found by scanning every request of the wave for "the <time> flight/departure".

Not loosened: violet-crag.

## Q2

The always-cheapest agent answers `LOWEST_FARE` with the cheapest seat; aspen-fjord already accepted that, so its
count is unchanged: **4/24 (17%)** (`MAX_PASS_ALWAYS_LOWEST = 4`).

## Re-score at the new head (stored answers)

22/24, easy 4/5 (ember-kestrel stays failed on its stored answer; its request changed).

## Re-run

Required (request changed): ember-kestrel (easy; must come back valid), birch-lagoon (easy), oriole-peak,
plover-glen.

## Checks

`uv run pytest -q` (209 passed), `uv run ruff check .`, `uv lock --check`, `check_shared.py`, byte-identical
`rules.py`, `tools/stock_verify.py` (24 scenarios, 0 failures), stock `nanoagent plugin inspect .` (exit 0).
