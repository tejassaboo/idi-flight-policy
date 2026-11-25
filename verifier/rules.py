"""The answer key's rules for the IDI Travel Policy (2025 edition) of the INTOSAI Development Initiative, as exact
integer code. Byte-identical in src/plugin/rules.py and verifier/rules.py; it imports only modules a verifier
may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an answer
open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each unclear phrase at
most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a new scenario cannot fall
silently into untested logic.

The duration hook. Lines 156-161: economy is the default; premium economy or business "will only be considered for
flights where: One leg of the journey lasts for more than 6 hours from the airport of departure or the total
journey lasts for more than 9 hours, and where travel involves overnight flights (Flights between 2200 to 0600
hours)". Both thresholds are strict ("more than").

- "leg": one flight's scheduled minutes over 360. A leg is one flight, so any one segment over 360 is enough and
  segments are never added together.
- "journey": the whole one-way journey over 540 minutes. The text does not say whether the journey counts the time
  on the ground between flights. When the flights alone add to more than 540 minutes, it is over on both readings
  (True); when the first departure to the last arrival is 540 minutes or less, it is over on neither (False);
  otherwise it is unclear (None).

The overnight condition (also lines 17 and 161: night is 22:00 to 06:00) is not a duration rule; ``overnight``
reads it per flight, on the local clocks of both the airport it leaves and the airport it reaches. Which clock
counts is not stated, so a flight is overnight only when it spends at least four hours of night, or all its time,
inside 22:00-06:00 on both clocks, and not overnight only when it spends no time at all inside it on both. Anything
in between is not modelled (no scenario uses it).

The grouping of "... or the total journey lasts for more than 9 hours, and where travel involves overnight flights"
is open: (leg or journey) and overnight, or leg or (journey and overnight). ``eligible`` evaluates both groupings
and both journey readings; it returns the verdict when they all agree and None with the unclear phrase otherwise.
"""

from contract import Approver, Cabin, Clause, Decision, LeaveTiming, Passenger, Purpose, ReasonCode, SignOffSubject

from .world import utc_minute, utc_offset

HANDBOOK = "INTOSAI Development Initiative, IDI Travel Policy, 2025 edition"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.VERSION_DETAILS: "VERSION DETAILS",
    Clause.INTRODUCTION: "I. INTRODUCTION",
    Clause.AREA_OF_APPLICATION: "II. AREA OF APPLICATION",
    Clause.ROLES_RESPONSIBILITIES: "III. ROLES AND RESPONSIBILITIES",
    Clause.GUIDING_PRINCIPLES: "IV. PRINCIPLES GUIDING OFFICIAL IDI TRAVEL",
    Clause.DEFINITIONS: "V. DEFINITIONS",
    Clause.GENERAL_CONDITIONS: "VI. GENERAL CONDITIONS",
    Clause.PRE_AUTHORISATION: "VII. PRE-AUTHORISATION TO TRAVEL",
    Clause.TRANSPORT_AUTHORISATION: "VIII. AUTHORISATION OF TRANSPORTATION AND ACCOMMODATION",
    Clause.COMMERCIAL_TRANSPORTATION: "IX. COMMERCIAL TRANSPORTATION",
    Clause.COMMERCIAL_AIR: "Commercial Air",
    Clause.PRIVATE_CAR: "Use of private car",
    Clause.TRAIN_BUS: "Use of train/bus",
    Clause.ACCOMMODATION_MEALS: "X. ACCOMMODATION, MEALS AND INCIDENTAL EXPENSES",
    Clause.PERSONAL_TRAVEL_VACATION: "Personal travel on weekends / Vacation before and or after an event",
    Clause.SPECIAL_SITUATIONS: "XI. SPECIAL TRAVEL SITUATIONS",
    Clause.ILLNESS_ACCIDENT: "Illness, accident or family emergency",
    Clause.TRAVEL_CLAIM: "XII. TRAVEL CLAIM",
    Clause.TIME_COMPENSATION: "XIII. COMPENSATION FOR TIME SPENT WORKING AND TRAVELLING ON OFFICIAL TRIPS",
}

# The handbook's duration thresholds (the per-handbook duration hook; tests/test_duration.py tests both sides of
# each). ">" is strict ("more than").
DURATION_RULES = (
    {"name": "leg", "minutes": 360, "operator": ">", "lines": [159, 160],
     "quote": "One leg of the journey lasts for more than 6 hours from the airport of departure"},
    {"name": "journey", "minutes": 540, "operator": ">", "lines": [160, 160],
     "quote": "the total journey lasts for more than 9 hours"},
)
LIMITS = {rule["name"]: rule["minutes"] for rule in DURATION_RULES}

# Handbook-specific conventions shown by booking_requirements, beyond the template's (none here).
CONVENTIONS = ()

# Lines 17 and 161: night is 22:00 to 06:00. A flight with at least NIGHT_ENOUGH minutes of night (or all its
# minutes, if shorter) on both local clocks is overnight; one with none on both is not.
NIGHT_START, NIGHT_END = 22 * 60, 6 * 60
NIGHT_ENOUGH = 240

JOURNEY_PHRASE = "the total journey lasts for more than 9 hours"
GROUPING_PHRASE = "and where travel involves overnight flights"

# Who a hold over unclear words may name: no one is named to settle the text. The exemption is the Director
# General's to authorise (lines 135-136, 165); the manager (ADG, line 131; DG/DDGs, line 149) authorises the class
# of travel on the travel authority form.
UNCLEAR_ROLES = [Approver.NOT_NAMED, Approver.DIRECTOR_GENERAL, Approver.DEPUTY_DIRECTOR_GENERAL,
                 Approver.ASSISTANT_DIRECTOR_GENERAL]
# Such a hold also waits on the Director General's decision on the exemption, so APPROVAL_REQUIRED may stand
# beside UNCLEAR_POLICY_TEXT.
UNCLEAR_REASONS = [ReasonCode.UNCLEAR_POLICY_TEXT, ReasonCode.APPROVAL_REQUIRED]

AIR_CLAUSES = [Clause.COMMERCIAL_AIR, Clause.COMMERCIAL_TRANSPORTATION]
# Lines 131-136 (the DG added to the travel authority for premium travel) and 149-151 (the class stated on it).
EXEMPTION_CLAUSES = [*AIR_CLAUSES, Clause.PRE_AUTHORISATION, Clause.TRANSPORT_AUTHORISATION]
# The economical choice: line 155 (Commercial Air), line 122 (General Conditions), line 103 (Principles).
ECONOMY_CLAUSES = [*AIR_CLAUSES, Clause.GENERAL_CONDITIONS, Clause.GUIDING_PRINCIPLES]
CABIN_RANK = {Cabin.ECONOMY: 1, Cabin.PREMIUM_ECONOMY: 2, Cabin.BUSINESS: 3, Cabin.FIRST: 4}


def over(rule, offer):
    """True, False or None (unclear): whether ``offer``'s outbound flights are over the handbook's ``rule``
    (leg: one flight over 360 scheduled minutes; journey: the whole journey over 540 minutes, see the module
    docstring for the reading of the time on the ground)."""
    if rule == "leg":
        return any(segment.scheduled_minutes > LIMITS["leg"] for segment in offer.segments)
    if rule == "journey":
        if offer.flying_minutes > LIMITS["journey"]:
            return True
        if offer.elapsed_minutes <= LIMITS["journey"]:
            return False
        return None
    raise ValueError(f"unknown duration rule {rule!r}")


def night_minutes(start, end):
    """Minutes of [start, end) (minutes on a local clock, as minute numbers) inside 22:00-06:00."""
    total = 0
    day = start // 1440 - 1
    while day * 1440 + NIGHT_START < end:
        low, high = day * 1440 + NIGHT_START, (day + 1) * 1440 + NIGHT_END
        total += max(0, min(end, high) - max(start, low))
        day += 1
    return total


def segment_night(segment):
    """(minutes of night on the departure airport's clock, on the arrival airport's clock)."""
    start, end = utc_minute(segment.depart_utc), utc_minute(segment.arrive_utc)
    return tuple(night_minutes(start + utc_offset(code), end + utc_offset(code))
                 for code in (segment.origin, segment.destination))


def overnight(offer):
    """True when a flight of the offer is overnight on both local clocks, False when no flight touches the night
    on either clock; raises in between (not modelled)."""
    nights = [(segment_night(segment), segment.scheduled_minutes) for segment in offer.segments]
    if any(min(clocks) >= min(NIGHT_ENOUGH, minutes) for clocks, minutes in nights):
        return True
    if all(max(clocks) == 0 for clocks, _ in nights):
        return False
    raise ValueError("a flight partly in the night window is not modelled")


def eligible(offer):
    """(verdict, phrase): whether premium economy or business may be considered for this offer (lines 159-161).
    The verdict is None when the readings disagree; the phrase names the unclear words then."""
    leg, night = over("leg", offer), overnight(offer)
    journey = over("journey", offer)
    journeys = [journey] if journey is not None else [True, False]

    def grouped(value):
        return {(leg or value) and night, leg or (value and night)}

    verdicts = set().union(*(grouped(value) for value in journeys))
    if len(verdicts) == 1:
        return verdicts.pop(), ""
    if journey is None and all(len(grouped(value)) == 1 for value in journeys):
        return None, JOURNEY_PHRASE
    if journey is not None:
        return None, GROUPING_PHRASE
    raise ValueError("an offer unclear on both the journey and the grouping is not modelled")


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def on_file(trip):
    """Approvers a BOOK or REFUSE accepts (SYNC_NOTES 4' and 4(b)): NONE, and the role of every sign-off on file,
    whether the decision uses it (the travel authority, an exemption) or not."""
    return [Approver.NONE, *(record.role for record in trip.sign_offs)]


def in_cabin(offers, cabin):
    return [offer for offer in offers if offer.cabin == cabin]


def cheapest_direct(offers, what):
    """Line 155: 'the most direct and economical route available'. The cheapest offers, which must also make
    the fewest connections; a cheaper offer with more connections than a dearer one sets 'direct' against
    'economical' and is not modelled."""
    if not offers:
        raise ValueError(f"no {what} offer can be bought")
    low = min(offer.fare_cents for offer in offers)
    lowest = [offer for offer in offers if offer.fare_cents == low]
    if any(offer.stops < min(item.stops for item in lowest) for offer in offers):
        raise ValueError(f"a dearer {what} offer with fewer connections than the cheapest is not modelled")
    if any(offer.refundable for offer in lowest):
        raise ValueError("a refundable lowest fare is not modelled")
    return lowest


def lowest_economy(seated):
    return cheapest_direct(in_cabin(seated, Cabin.ECONOMY), "economy")


def exemption_giver(trip):
    """Line 165: exemptions are authorised by the Director General for staff and by the Chair of the IDI Board
    for Board members (and the Director General)."""
    if trip.passenger == Passenger.BOARD_MEMBER:
        return Approver.BOARD_CHAIR
    if trip.passenger == Passenger.STAFF_MEMBER:
        return Approver.DIRECTOR_GENERAL
    raise ValueError(f"an exemption for a {trip.passenger.value} is not modelled")


def exemptions(trip):
    records = [record for record in trip.sign_offs if record.subject == SignOffSubject.CABIN_EXEMPTION]
    giver = exemption_giver(trip)
    if any(record.role != giver for record in records):
        raise ValueError("an exemption signed by someone the handbook does not name for this traveller is not modelled")
    if len(records) > 1:
        raise ValueError("two exemptions on file are not modelled")
    if records and trip.exemption_pending:
        raise ValueError("an exemption both granted and pending is not modelled")
    return records


def trip_offers(trip, offers):
    """The offers on the trip's own route and day (other searches, e.g. the usual travel date, are kept apart)."""
    return [offer for offer in offers
            if offer.segments[0].origin == trip.origin.code and offer.segments[-1].destination == trip.destination.code
            and offer.segments[0].depart_local[:10] == trip.travel_date]


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers of the searches its scenario pins: the decision, and every
    accepted offer id, cabin, reason, approver and section. ``hidden`` (answer_key_inputs) is unused here."""
    if hidden:
        raise ValueError("this handbook's scenarios carry no answer_key_inputs")
    if any(offer.return_segments for offer in offers):
        raise ValueError("round-trip fares are not modelled: every case buys a one-way ticket")
    own = trip_offers(trip, offers)
    seated = [offer for offer in own if offer.seats_available]
    if trip.passenger == Passenger.FAMILY_MEMBER:
        return family(trip, seated)
    if trip.passenger not in (Passenger.STAFF_MEMBER, Passenger.BOARD_MEMBER):
        raise ValueError(f"a {trip.passenger.value} passenger is not modelled")
    if trip.goes_to or trip.staff_ill_on_duty:
        raise ValueError("next-of-kin facts on a staff or Board trip are not modelled")
    if trip.purpose_kind == Purpose.PERSONAL:
        return personal(trip)
    if trip.requested_cabin == Cabin.ECONOMY:
        return economy(trip, seated)
    if trip.requested_cabin not in (Cabin.PREMIUM_ECONOMY, Cabin.BUSINESS):
        raise ValueError(f"a {trip.requested_cabin.value} request is not modelled")
    return premium(trip, seated, offers)


def personal(trip):
    """Lines 234-239: a weekend at another location of personal choice; its transportation is not reimbursed."""
    if trip.requested_cabin != Cabin.ECONOMY or trip.leave_attached != LeaveTiming.NONE:
        raise ValueError("a personal trip outside economy or with leave attached is not modelled")
    return answer(Decision.REFUSE, [], [ReasonCode.PERSONAL_TRAVEL_NOT_COVERED, ReasonCode.OUTSIDE_POLICY_SCOPE],
                  on_file(trip), [Clause.PERSONAL_TRAVEL_VACATION, Clause.ACCOMMODATION_MEALS],
                  "Lines 234-239: the staff member is not required to stay at the duty location over the weekend and "
                  "chooses to spend it at another location of personal choice; transportation related to that stay "
                  "shall not be reimbursed. The IDI buys no ticket.")


def family(trip, seated):
    """Lines 57-58: the policy applies only to IDI staff and Board members. Lines 251-253: when a staff member
    becomes ill or injured on official duty and needs the presence of next of kin, actual and reasonable
    transportation may be reimbursed."""
    if not trip.goes_to or trip.requested_cabin != Cabin.ECONOMY:
        raise ValueError("a family member's trip with nobody to go to, or outside economy, is not modelled")
    if trip.staff_ill_on_duty:
        if not any(record.subject == SignOffSubject.TRAVEL_AUTHORITY for record in trip.sign_offs):
            raise ValueError("a next-of-kin trip without an authorisation on file is not modelled")
        return answer(Decision.BOOK, lowest_economy(seated), [ReasonCode.NEXT_OF_KIN_TRAVEL, ReasonCode.LOWEST_FARE],
                      on_file(trip), [Clause.ILLNESS_ACCIDENT, Clause.SPECIAL_SITUATIONS],
                      "Lines 251-253: the staff member was injured on official duty and needs her next of kin there, "
                      "so actual and reasonable transportation is covered; the travel is authorised (line 131). Economy, "
                      "the default (line 156), at the lowest fare.")
    if trip.sign_offs:
        raise ValueError("a family member's trip with a sign-off but no illness is not modelled")
    return answer(Decision.REFUSE, [],
                  [ReasonCode.OUTSIDE_POLICY_SCOPE, ReasonCode.COMPANION_NOT_COVERED,
                   ReasonCode.PERSONAL_TRAVEL_NOT_COVERED],
                  on_file(trip), [Clause.AREA_OF_APPLICATION, Clause.SPECIAL_SITUATIONS, Clause.ILLNESS_ACCIDENT],
                  "Lines 57-58: the policy applies only to IDI staff and Board members. A family member is covered only "
                  "when a staff member is ill or injured on duty and needs next of kin (lines 251-253), which is not "
                  "the case. The IDI buys no ticket.")


def economy(trip, seated):
    """An economy request: lines 155-156, the most direct and economical route, economy the default."""
    if trip.leave_attached != LeaveTiming.NONE or trip.purpose_kind == Purpose.COURSE:
        raise ValueError("an economy request with leave attached or for a course is not modelled")
    lowest = lowest_economy(seated)
    if trip.requested_connection:
        asked = [offer for offer in in_cabin(seated, Cabin.ECONOMY)
                 if any(segment.destination == trip.requested_connection for segment in offer.segments[:-1])]
        if not asked or any(offer in lowest for offer in asked):
            raise ValueError("a requested connection that is the cheapest, or not offered, is not modelled")
        if any(offer.elapsed_minutes < max(item.elapsed_minutes for item in lowest) for offer in asked):
            raise ValueError("a requested connection faster than the cheapest is not modelled")
        # The ground for declining the requested routing is line 155 itself: it is neither the more direct nor
        # the more economical route, so LOWEST_FARE names it beside the route codes.
        return answer(Decision.BOOK, lowest,
                      [ReasonCode.LOWEST_FARE, ReasonCode.DIRECT_ECONOMICAL_ROUTE,
                       ReasonCode.ALTERNATE_ROUTE_TOO_EXPENSIVE, ReasonCode.COST_SAVINGS,
                       ReasonCode.CONNECTION_TOO_LONG],
                      on_file(trip), ECONOMY_CLAUSES,
                      "Line 155: commercial air travel shall be the most direct and economical route available. The "
                      "connection the traveller asks for is dearer and takes longer; the lounge of line 169 is an "
                      "entitlement on a long stopover, not a ground to choose one. Book the cheapest economy fare.")
    return answer(Decision.BOOK, lowest, [ReasonCode.LOWEST_FARE], on_file(trip), ECONOMY_CLAUSES,
                  "Lines 155-156: the most direct and economical route, in economy, the default class. The traveller "
                  "asks for economy, so no exemption is used even where one could be (permission is not obligation).")


def premium(trip, seated, offers):
    """A premium economy or business request. Lines 156-163: economy is the default; an exemption may be authorised
    only on the flights of lines 159-161, or for duly certified medical reasons (line 164), by the Director General
    for staff and the Board Chair for Board members (line 165). Line 176: courses always in economy. Line 240:
    economy for a segment that starts or ends vacation leave."""
    wanted = trip.requested_cabin
    granted = exemptions(trip)
    if trip.leave_attached != LeaveTiming.NONE:
        return vacation(trip, seated, offers)
    if trip.purpose_kind == Purpose.COURSE:
        if granted:
            raise ValueError("an exemption granted for a course is not modelled")
        return answer(Decision.BOOK, lowest_economy(seated),
                      [ReasonCode.COURSE_TRAVEL_ECONOMY, ReasonCode.UPGRADE_NOT_ELIGIBLE], on_file(trip), AIR_CLAUSES,
                      "Line 176: travel for courses and studies should always be on an economy class ticket, whatever "
                      "the flight's length; the pending exemption does not change that. The cheapest economy fare.")
    asked = cheapest_direct(in_cabin(seated, wanted), wanted.value.lower())
    if trip.medical_certificate_on_file:
        return medical(trip, seated, asked, granted)
    verdicts = {eligible(offer) for offer in [*asked, *in_cabin(seated, wanted)]}
    if len(verdicts) != 1:
        raise ValueError("offers of the asked cabin on both sides of the exemption criteria are not modelled")
    verdict, phrase = verdicts.pop()
    if verdict is None:
        if granted:
            raise ValueError("an unclear case with the exemption already granted is not modelled")
        return answer(Decision.FLAG_FOR_APPROVAL, [*asked, *lowest_economy(seated)], UNCLEAR_REASONS, UNCLEAR_ROLES,
                      EXEMPTION_CLAUSES,
                      "Lines 159-161: an exemption above economy is considered only for flights where one leg lasts "
                      "more than 6 hours or the total journey more than 9 hours, and where travel involves overnight "
                      f"flights. Here the words '{phrase}' decide it and read two ways, so the handbook leaves open "
                      "whether the Director General may grant the pending exemption at all. Hold it.", phrase=phrase)
    if not verdict:
        if granted:
            raise ValueError("an exemption granted on a flight outside the criteria is not modelled")
        return answer(Decision.BOOK, lowest_economy(seated),
                      [ReasonCode.UPGRADE_NOT_ELIGIBLE, ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET], on_file(trip),
                      AIR_CLAUSES,
                      "Lines 156-161: no leg is more than 6 hours and the journey is not more than 9 hours with an "
                      "overnight flight on every reading, so no exemption can be considered, even one applied for. "
                      "Economy, the default, at the lowest fare (line 155).")
    if not granted:
        giver = exemption_giver(trip)
        return answer(Decision.FLAG_FOR_APPROVAL, asked, [ReasonCode.APPROVAL_REQUIRED], [giver], EXEMPTION_CLAUSES,
                      "Lines 159-161: the flight meets the criteria, so an exemption may be authorised, but only by the "
                      f"{giver.value.replace('_', ' ').lower()} (lines 135-136, 165), and none is on file: hold the "
                      "cheapest fare of the cabin asked for.")
    allowed = granted[0].cabin
    reasons = [ReasonCode.CABIN_EXEMPTION_AUTHORIZED, ReasonCode.LONG_FLIGHT_APPROVED,
               ReasonCode.INTERNATIONAL_LONG_FLIGHT]
    if allowed == Cabin.PREMIUM_ECONOMY:
        reasons.append(ReasonCode.PREMIUM_ECONOMY_ALLOWED)
    if CABIN_RANK[wanted] <= CABIN_RANK[allowed]:
        if wanted != allowed:
            raise ValueError("a request below the exempted cabin is not modelled")
        return answer(Decision.BOOK, asked, reasons, on_file(trip), EXEMPTION_CLAUSES,
                      "Lines 159-161: the flight meets the criteria (a leg over 6 hours, or a journey over 9 hours, with "
                      "an overnight flight), and the exemption is authorised on file by the role line 165 names: the "
                      "cheapest fare of the cabin it allows.")
    granted_offers = cheapest_direct(in_cabin(seated, allowed), allowed.value.lower())
    return answer(Decision.BOOK, granted_offers,
                  [ReasonCode.CABIN_EXEMPTION_AUTHORIZED, ReasonCode.PREMIUM_ECONOMY_ALLOWED,
                   ReasonCode.UPGRADE_NOT_ELIGIBLE],
                  on_file(trip), EXEMPTION_CLAUSES,
                  "Lines 159-161 and 165: the flight meets the criteria, but the exemption on file authorises premium "
                  "economy only, so business is not authorised; book the cheapest premium economy fare.")


def medical(trip, seated, asked, granted):
    """Line 164: exemptions may also be made for duly certified medical reasons; line 165: authorised by the
    Director General."""
    if not granted or granted[0].cabin != trip.requested_cabin:
        raise ValueError("a medical case without an exemption for the cabin asked for is not modelled")
    if any(eligible(offer)[0] is not False for offer in asked):
        raise ValueError("a medical case on a flight that meets the duration criteria is not modelled")
    return answer(Decision.BOOK, asked, [ReasonCode.MEDICAL_NEED, ReasonCode.CABIN_EXEMPTION_AUTHORIZED],
                  on_file(trip), EXEMPTION_CLAUSES,
                  "Line 164: exemptions may also be made for duly certified medical reasons, whatever the flight's "
                  "length; the certificate and the Director General's exemption (line 165) are on file. The cheapest "
                  "fare of the cabin authorised.")


def vacation(trip, seated, offers):
    """Lines 240-242: with vacation just before or after an event, that segment is flown in economy and its price
    must not exceed the ticket without the holiday."""
    if trip.purpose_kind == Purpose.COURSE or trip.medical_certificate_on_file:
        raise ValueError("leave combined with a course or a medical need is not modelled")
    lowest = lowest_economy(seated)
    usual = [offer for offer in offers if offer.segments[0].depart_local[:10] == trip.usual_travel_date
             and offer.seats_available and offer.cabin == Cabin.ECONOMY]
    if not usual or lowest[0].fare_cents > min(offer.fare_cents for offer in usual):
        raise ValueError("a leave segment dearer than the usual economy fare, or no usual fare, is not modelled")
    # The cabin asked for is declined because of the traveller's own leave (lines 240-242, under "Personal travel
    # ... / Vacation"), so PERSONAL_TRAVEL_NOT_COVERED also names the ground.
    return answer(Decision.BOOK, lowest, [ReasonCode.VACATION_SEGMENT_ECONOMY, ReasonCode.UPGRADE_NOT_ELIGIBLE,
                                          ReasonCode.PERSONAL_TRAVEL_NOT_COVERED],
                  on_file(trip), [Clause.PERSONAL_TRAVEL_VACATION, Clause.ACCOMMODATION_MEALS],
                  "Lines 240-242: the traveller takes vacation just before the event, so this segment must be travelled "
                  "in economy, whatever exemption was given for the trip, and its price must not exceed the ticket "
                  "without the holiday (it is below even the usual date's economy fare). The cheapest economy fare.")
