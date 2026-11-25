"""Writes the IDI scenario JSON files (an authoring aid, not a test; the JSON files are the truth).

    uv run python tests/build_scenarios.py

Expected answers are hand-written here; tests/test_scenarios.py checks them against rules.solve. Fares are in
øre (hundredths of Norwegian kroner, handbook.json currency NOK).
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

POLICY = (ROOT / "src/plugin/data/policy.txt").read_text(encoding="utf-8").split("\n")
OUT = ROOT / "src/plugin/data/scenarios"


def norm(text):
    return " ".join(text.split())


def keep(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    quote = text if quote is None else quote
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "sha256": hashlib.sha256(text.encode()).hexdigest(), "quote": quote, "why": why}


def aside(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "quote": quote, "why": why}


# ----- clauses the answers rest on -----
AUTHORITY = keep(131, 132, "All travel and travel arrangements shall be pre-authorised by the staff member's manager "
                 "(ADG)", "every trip is pre-authorised by the manager (ADG) on a travel authority form")
DG_ADDED = keep(135, 136, "if there is an exceptional need for traveling on premium economy/business, the DG needs to "
                "be added for approval of all such travel.", "premium economy or business needs the DG's approval")
DIRECT = keep(155, 155, None, "the most direct and economical route")
CRITERIA = keep(156, 161, None, "economy by default; an exemption only where a leg is over 6 hours or the journey over "
                "9 hours, and where travel involves overnight flights")
MEDICAL = keep(164, 164, None, "an exemption may also be made for duly certified medical reasons")
GIVER = keep(165, 166, "Exemptions will be authorized by IDI Director General for all IDI staff and by the Chair of "
             "the IDI Board for IDI Board members and IDI Director General.",
             "who authorises an exemption: the DG for staff, the Board Chair for Board members")
COURSE = keep(176, 176, None, "courses and studies always in economy")
NIGHT = keep(115, 115, None, "night is the period between 22:00 and 06:00")
SCOPE = keep(57, 58, "It applies only to IDI staff and Board members.", "the policy covers staff and Board members only")
WEEKEND = keep(234, 239, None, "a weekend at another location of personal choice: its transportation is not reimbursed")
VACATION = keep(240, 242, None, "vacation just before or after an event: economy for that segment, capped at the "
                "ticket without the holiday")
KIN = keep(251, 253, None, "next of kin's transportation when a staff member is ill or injured on official duty")
ECONOMICAL = keep(122, 123, "The journey shall be made in the speediest, safest and most reasonable/economical manner "
                  "for the IDI", "the journey is made in the most reasonable/economical manner")

# ----- nearby clauses that must not change the answer -----
LOUNGE = aside(169, 169, "IDI staff are entitled to a lounge if the stopover is longer than three hours.",
               "a lounge entitlement on a long stopover; it does not choose the route")
LEGROOM = aside(175, 175, "Purchasing extra leg room may also be considered for long travels",
                "extra legroom is an add-on, not a cabin")
TRAIN = aside(195, 195, "Train or bus travel can be undertaken by IDI staff using the cheapest available business or "
              "premium class tickets", "business or premium class on trains and buses, not on flights")
COMPENSATION = aside(296, 297, "not in connection with courses, seminars or conferences unless the employee has "
                     "specific assignments", "a pay rule for coordinators; it does not set the cabin")
MEALS = aside(210, 211, "For return trips from six to twelve hours from the place of residence/workplace",
              "hours that set a meals allowance, not a cabin")
BAGGAGE = aside(173, 174, "cost of carrying a single piece checked in baggage can be included in the travel claim",
                "a baggage rule, not a fare rule")
CLAIM = aside(275, 275, "Travel claims shall be submitted as soon as possible and at the latest 10 working days.",
              "a claim deadline, not a booking rule")
DAY = aside(114, 114, "Day: In this policy, day means 24 hours calculated from the time the trip begins.",
            "a day of 24 hours for allowances, not a flight length")

# ----- people -----
DG = "Marit Aasen"
CHAIR = "Elena Ruiz-Calderon"


def adg(name):
    return sign("ASSISTANT_DIRECTOR_GENERAL", name, "TRAVEL_AUTHORITY")


def exemption(cabin="BUSINESS"):
    return sign("DIRECTOR_GENERAL", DG, "CABIN_EXEMPTION", cabin)


def sign(role, name, subject, cabin="NONE"):
    return {"role": role, "name": name, "subject": subject, "cabin": cabin}


def trip(**fields):
    base = {
        "traveller_name": "", "traveller_title": "", "passenger": "STAFF_MEMBER", "goes_to": "", "based_in": "",
        "origin": "", "destination": "", "travel_date": "", "booking_date": "", "purpose": "",
        "purpose_kind": "MEETING", "engagement_starts": "", "requested_cabin": "ECONOMY", "requested_connection": "",
        "leave_attached": "NONE", "usual_travel_date": "", "medical_certificate_on_file": False,
        "staff_ill_on_duty": False, "exemption_pending": False, "sign_offs": [],
    }
    unknown = set(fields) - set(base)
    assert not unknown, unknown
    base.update(fields)
    return base


def offer(slot, flight, cabin, nok, seats=True):
    data = {"slot": slot, "flight": flight, "cabin": cabin, "fare_cents": nok * 100}
    if not seats:
        data["seats"] = False
    return data


def expected(decision, slots, cabins, reasons, approvers, clauses, phrase=""):
    return {"decision": decision, "offer_slots": sorted(slots), "cabins": sorted(cabins),
            "reason_codes": sorted(reasons), "approvers": sorted(approvers), "clauses": sorted(clauses),
            "unclear_phrase": phrase}


def search(origin, destination, date, flights, offers, name="main"):
    # No background offers (handbook.json background_offers is 0): every pinned search lists only its own offers,
    # so no background nonstop or connection can set "direct" against "economical" (line 155).
    return {"name": name, "origin": origin, "destination": destination, "date": date, "return_date": "",
            "background": 0, "flights": flights, "offers": offers}


S = []


def scenario(id, category, overlays, request, trip_, searches, exp, must_keep, notes, twin_of="", twin_fact="",
             flag_twins=(), ambiguity="none", distractors=()):
    S.append({
        "id": id, "category": category, "overlays": list(overlays), "twin_of": twin_of, "twin_fact": twin_fact,
        "flag_twins": list(flag_twins), "ambiguity_note": ambiguity, "request": request, "trip": trip_,
        "world": {"searches": list(searches)}, "expected": exp, "must_keep": list(must_keep),
        "distractors": list(distractors), "design_notes": notes,
    })


AIR = ["COMMERCIAL_AIR", "COMMERCIAL_TRANSPORTATION"]
EXEMPT = [*AIR, "PRE_AUTHORISATION", "TRANSPORT_AUTHORISATION"]
ECONOMY = [*AIR, "GENERAL_CONDITIONS", "GUIDING_PRINCIPLES"]
LONG_OK = ["CABIN_EXEMPTION_AUTHORIZED", "INTERNATIONAL_LONG_FLIGHT", "LONG_FLIGHT_APPROVED"]
NOT_MET = ["LONG_FLIGHT_CONDITION_NOT_MET", "UPGRADE_NOT_ELIGIBLE"]
UNCLEAR_ROLES = ["ASSISTANT_DIRECTOR_GENERAL", "DEPUTY_DIRECTOR_GENERAL", "DIRECTOR_GENERAL", "NOT_NAMED"]
UNCLEAR_REASONS = ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"]
STAFF_BOOK = ["ASSISTANT_DIRECTOR_GENERAL", "NONE"]
STAFF_EXEMPT_BOOK = ["ASSISTANT_DIRECTOR_GENERAL", "DIRECTOR_GENERAL", "NONE"]
FALLBACK = "If the policy rules business out for this flight, book what it allows; I have to be at the {}."
# The boundary twins carry the same signed exemption on both sides, so each pair differs in one fact (the flight).
# The DG signed it subject to the flight qualifying, so the ineligible side has no "the DG signed, so business"
# reading against "such exemptions will only be considered for flights where ..." (lines 159-161).
SIGNED = "The DG has signed my exemption for business, provided the flight qualifies under the policy. "

# ===== easy (5) =====

scenario(
    "aspen-fjord", "easy", ["upgrade_not_taken"],
    "I fly Johannesburg to Frankfurt on the evening of January 12th for the working group meeting. The DG signed an "
    "exemption so I could go business, but our project budget is tight this year, so please put me in economy.",
    trip(traveller_name="Thandiwe Mokoena", traveller_title="Senior Manager, Professional SAIs",
         based_in="Johannesburg, South Africa", origin="JNB", destination="FRA", travel_date="2027-01-12",
         booking_date="2026-12-14", purpose="INTOSAI working group meeting in Frankfurt",
         engagement_starts="2027-01-13 13:00", sign_offs=[adg("Lars Eide"), exemption()]),
    [search("JNB", "FRA", "2027-01-12", {
        "lufthansa": {"carrier": "LH", "depart": "19:40", "minutes": [650]},
        "saa": {"carrier": "SA", "depart": "20:15", "minutes": [650]},
    }, [
        offer("lufthansa-economy", "lufthansa", "ECONOMY", 7450, seats=False),
        offer("lufthansa-business", "lufthansa", "BUSINESS", 39500),
        offer("saa-economy", "saa", "ECONOMY", 7980),
        offer("saa-business", "saa", "BUSINESS", 42000),
    ])],
    expected("BOOK", ["saa-economy"], ["ECONOMY"], ["COST_SAVINGS", "LOWEST_FARE"], STAFF_EXEMPT_BOOK, ECONOMY),
    [DIRECT, CRITERIA],
    "A 650-minute overnight flight would allow the business exemption the DG signed, but the traveller asks for "
    "economy: economy is the default (line 156) and permission is not obligation. The cheaper Lufthansa economy fare "
    "is sold out, so the cheapest seat that can be bought is South African Airways economy. The exemption on file goes "
    "unused (DG accepted beside NONE and the ADG, SYNC_NOTES 4(b)).")

scenario(
    "birch-lagoon", "easy", ["dearer_option"],
    "Please book me business class Nairobi to Amsterdam on February 7th, on one of the late-evening departures, for "
    "the donor coordination meeting. The DG has approved my exemption for business.",
    trip(traveller_name="Wanjiru Kamau", traveller_title="Manager, Bilateral Support", based_in="Nairobi, Kenya",
         origin="NBO", destination="AMS", travel_date="2027-02-07", booking_date="2027-01-11",
         purpose="Donor coordination meeting in Amsterdam", engagement_starts="2027-02-09 10:00",
         requested_cabin="BUSINESS", sign_offs=[adg("Kari Nygaard"), exemption()]),
    [search("NBO", "AMS", "2027-02-07", {
        "klm": {"carrier": "KL", "depart": "23:30", "minutes": [505]},
        "kenya": {"carrier": "KQ", "depart": "23:55", "minutes": [510]},
    }, [
        offer("klm-economy", "klm", "ECONOMY", 6850),
        offer("klm-business", "klm", "BUSINESS", 34900),
        offer("kenya-economy", "kenya", "ECONOMY", 6400),
        offer("kenya-business", "kenya", "BUSINESS", 31800),
    ])],
    expected("BOOK", ["kenya-business"], ["BUSINESS"], LONG_OK, STAFF_EXEMPT_BOOK, EXEMPT),
    [CRITERIA, DG_ADDED, GIVER, NIGHT],
    "Both nonstops fly more than 6 hours (505 and 510 minutes) through the night (23:30 and 23:55 from Nairobi), so an "
    "exemption may be considered on every reading of lines 159-161, and the DG's exemption for business is on file "
    "(lines 135-136, 165). The cheapest business fare: Kenya Airways.")

scenario(
    "cobalt-tern", "easy", [],
    "Cairo to Amsterdam on March 16th for the peer review planning meeting. I'd like premium economy if the policy "
    "allows it for this flight; otherwise economy is fine. I have to be at the meeting the next morning.",
    trip(traveller_name="Omar Farouk", traveller_title="Senior Manager, Well-Governed SAIs", based_in="Cairo, Egypt",
         origin="CAI", destination="AMS", travel_date="2027-03-16", booking_date="2027-02-22",
         purpose="Peer review planning meeting in Amsterdam", engagement_starts="2027-03-17 09:00",
         requested_cabin="PREMIUM_ECONOMY", sign_offs=[adg("Lars Eide")]),
    [search("CAI", "AMS", "2027-03-16", {
        "klm": {"carrier": "KL", "depart": "09:10", "minutes": [265]},
        "egyptair": {"carrier": "MS", "depart": "11:00", "minutes": [265]},
    }, [
        offer("klm-economy", "klm", "ECONOMY", 3900),
        offer("klm-premium", "klm", "PREMIUM_ECONOMY", 6200),
        offer("egyptair-economy", "egyptair", "ECONOMY", 3650),
        offer("egyptair-premium", "egyptair", "PREMIUM_ECONOMY", 5900),
    ])],
    expected("BOOK", ["egyptair-economy"], ["ECONOMY"], NOT_MET, STAFF_BOOK, AIR),
    [CRITERIA, DIRECT],
    "A 265-minute daytime flight: no leg over 6 hours, no journey over 9 hours, no night flight, so premium economy "
    "cannot be considered on any reading (lines 156-161). Economy at the lowest fare, EgyptAir.",
    distractors=[LEGROOM])

scenario(
    "dune-sorrel", "easy", ["upgrade_not_taken"],
    "Book me economy from Delhi to Frankfurt, leaving just after midnight on January 20th, for the audit "
    "methodology workshop that starts on the 21st.",
    trip(traveller_name="Priya Natarajan", traveller_title="Manager, Relevant SAIs", based_in="New Delhi, India",
         origin="DEL", destination="FRA", travel_date="2027-01-20", booking_date="2026-12-28",
         purpose="Audit methodology workshop in Frankfurt", purpose_kind="WORKSHOP",
         engagement_starts="2027-01-21 09:00", sign_offs=[adg("Kari Nygaard")]),
    [search("DEL", "FRA", "2027-01-20", {
        "lufthansa": {"carrier": "LH", "depart": "00:30", "minutes": [465]},
        "airindia": {"carrier": "AI", "depart": "01:15", "minutes": [470]},
    }, [
        offer("lufthansa-economy", "lufthansa", "ECONOMY", 5600),
        offer("lufthansa-business", "lufthansa", "BUSINESS", 29800),
        offer("airindia-economy", "airindia", "ECONOMY", 5250),
        offer("airindia-business", "airindia", "BUSINESS", 27400),
    ])],
    expected("BOOK", ["airindia-economy"], ["ECONOMY"], ["LOWEST_FARE"], STAFF_BOOK, ECONOMY),
    [DIRECT, CRITERIA],
    "The overnight flights are long enough for an exemption to be considered, but the traveller asks for economy and "
    "none is sought: economy, the default, at the lowest fare (Air India).")

scenario(
    "ember-kestrel", "easy", ["dearer_option"],
    "Premium economy please from Delhi to Amsterdam on February 3rd, on one of the early-morning departures, for the "
    "SAI leadership programme meeting. The DG approved premium economy for me.",
    trip(traveller_name="Arjun Mehra", traveller_title="Senior Manager, Strategic Support", based_in="New Delhi, India",
         origin="DEL", destination="AMS", travel_date="2027-02-03", booking_date="2027-01-08",
         purpose="SAI leadership programme meeting in Amsterdam", engagement_starts="2027-02-04 13:00",
         requested_cabin="PREMIUM_ECONOMY", sign_offs=[adg("Lars Eide"), exemption("PREMIUM_ECONOMY")]),
    [search("DEL", "AMS", "2027-02-03", {
        "klm": {"carrier": "KL", "depart": "01:00", "minutes": [485]},
        "airindia": {"carrier": "AI", "depart": "01:40", "minutes": [485]},
    }, [
        offer("klm-economy", "klm", "ECONOMY", 5900),
        offer("klm-premium", "klm", "PREMIUM_ECONOMY", 9800),
        offer("klm-business", "klm", "BUSINESS", 30500),
        offer("airindia-economy", "airindia", "ECONOMY", 5400),
        offer("airindia-premium", "airindia", "PREMIUM_ECONOMY", 9200),
        offer("airindia-business", "airindia", "BUSINESS", 28900),
    ])],
    expected("BOOK", ["airindia-premium"], ["PREMIUM_ECONOMY"], [*LONG_OK, "PREMIUM_ECONOMY_ALLOWED"],
             STAFF_EXEMPT_BOOK, EXEMPT),
    [CRITERIA, DG_ADDED, GIVER],
    "485-minute nonstops leaving at 01:00 and 01:40: a leg over 6 hours, overnight, so the DG's exemption for premium "
    "economy applies (lines 156-161, 165). The cheapest premium economy fare: Air India.")

# ===== boundary twins (6) =====

MUMBAI_FLIGHTS = {
    "kenya": {"carrier": "KQ", "depart": "22:30", "minutes": [361]},
    "airindia": {"carrier": "AI", "depart": "23:15", "minutes": [355]},
}
MUMBAI_OFFERS = [
    offer("kenya-economy", "kenya", "ECONOMY", 4300),
    offer("kenya-business", "kenya", "BUSINESS", 21500),
    offer("airindia-economy", "airindia", "ECONOMY", 4650),
]


def mumbai(minutes):
    flights = json.loads(json.dumps(MUMBAI_FLIGHTS))
    flights["kenya"]["minutes"] = [minutes]
    return [search("NBO", "BOM", "2027-03-07", flights, MUMBAI_OFFERS)]


def mumbai_trip(name, title, **fields):
    return trip(traveller_name=name, traveller_title=title, based_in="Nairobi, Kenya", origin="NBO",
                destination="BOM", travel_date="2027-03-07", booking_date="2027-02-10",
                purpose="Cooperative audit workshop hosted by the SAI of India in Mumbai", purpose_kind="WORKSHOP",
                engagement_starts="2027-03-09 09:00", requested_cabin="BUSINESS", **fields)


scenario(
    "fennel-quay", "boundary_twin", ["dearer_option"],
    "Business class please on the Kenya Airways 22:30 flight from Nairobi to Mumbai on March 7th. " + SIGNED
    + FALLBACK.format("workshop"),
    mumbai_trip("Joseph Mwangi", "Manager, Bilateral Support", sign_offs=[adg("Kari Nygaard"), exemption()]),
    mumbai(361),
    expected("BOOK", ["kenya-business"], ["BUSINESS"], LONG_OK, STAFF_EXEMPT_BOOK, EXEMPT),
    [CRITERIA, DG_ADDED, GIVER, NIGHT],
    "The Kenya Airways nonstop is scheduled at 361 minutes, more than 6 hours (strict), leaving 22:30 and flying through "
    "the night on both clocks: the exemption criteria hold on every reading, and the DG's exemption is on file. Book "
    "Kenya Airways business (Air India sells no business on its 355-minute flight).",
    twin_of="garnet-brook", twin_fact="Kenya Airways nonstop 361 or 360 minutes (the same signed exemption in both)")

scenario(
    "garnet-brook", "boundary_twin", [],
    "Business class please on the Kenya Airways 22:30 flight from Nairobi to Mumbai on March 7th. " + SIGNED
    + FALLBACK.format("workshop"),
    mumbai_trip("Grace Achieng", "Manager, Bilateral Support", sign_offs=[adg("Kari Nygaard"), exemption()]),
    mumbai(360),
    expected("BOOK", ["kenya-economy"], ["ECONOMY"], NOT_MET, STAFF_EXEMPT_BOOK, AIR),
    [CRITERIA, DIRECT],
    "At exactly 360 minutes no leg lasts more than 6 hours, and 360 minutes is no journey of more than 9 hours, so an "
    "exemption cannot be considered on any reading of lines 159-161, and the DG's exemption, signed subject to the "
    "flight qualifying, does not apply (it stays on file unused: DG accepted beside the ADG and NONE). Economy at the "
    "lowest fare, Kenya Airways.",
    twin_of="fennel-quay", twin_fact="Kenya Airways nonstop 360 or 361 minutes (the same signed exemption in both)")

DOHA_NIGHT = {"carrier": "QR", "via": ["DOH"], "depart": "20:30", "minutes": [210, 360], "layovers": [75]}
DOHA_DAY = {"carrier": "QR", "via": ["DOH"], "depart": "09:00", "minutes": [210, 360], "layovers": [75]}
DOHA_OFFERS = [offer("qatar-economy", "qatar", "ECONOMY", 6100), offer("qatar-business", "qatar", "BUSINESS", 33800)]


def copenhagen_trip(name, **fields):
    return trip(traveller_name=name, traveller_title="Senior Manager, SAI Governance", based_in="New Delhi, India",
                origin="DEL", destination="CPH", travel_date="2027-04-11", booking_date="2027-03-15",
                purpose="Nordic SAI partnership conference in Copenhagen", purpose_kind="CONFERENCE",
                engagement_starts="2027-04-13 09:00", requested_cabin="BUSINESS", **fields)


scenario(
    "heather-cove", "boundary_twin", ["multi_leg", "dearer_option"],
    "Delhi to Copenhagen on April 11th for the partnership conference, on the Qatar Airways evening departure via "
    "Doha. Business please. " + SIGNED + FALLBACK.format("conference"),
    copenhagen_trip("Rohan Kapoor", sign_offs=[adg("Lars Eide"), exemption()]),
    [search("DEL", "CPH", "2027-04-11", {"qatar": DOHA_NIGHT}, DOHA_OFFERS)],
    expected("BOOK", ["qatar-business"], ["BUSINESS"], LONG_OK, STAFF_EXEMPT_BOOK, EXEMPT),
    [CRITERIA, DG_ADDED, GIVER, NIGHT],
    "No leg is over 6 hours (210 and 360 minutes), but the flights alone add to 570 minutes, so the total journey is "
    "over 9 hours on any reading, and the Doha-Copenhagen flight leaves 22:45 and flies through the night on both "
    "clocks. Both groupings of lines 159-161 hold, and the DG's exemption is on file: Qatar business.",
    twin_of="iris-shoal", twin_fact="Qatar Airways leaves Delhi 20:30 (Doha-Copenhagen overnight) or 09:00 (all "
    "daytime); the same signed exemption in both")

scenario(
    "iris-shoal", "boundary_twin", ["multi_leg"],
    "Delhi to Copenhagen on April 11th for the partnership conference, on the Qatar Airways morning departure via "
    "Doha. Business please. " + SIGNED + FALLBACK.format("conference"),
    copenhagen_trip("Meera Iyer", sign_offs=[adg("Lars Eide"), exemption()]),
    [search("DEL", "CPH", "2027-04-11", {"qatar": DOHA_DAY}, DOHA_OFFERS)],
    expected("BOOK", ["qatar-economy"], ["ECONOMY"], NOT_MET, STAFF_EXEMPT_BOOK, AIR),
    [CRITERIA, NIGHT, DIRECT],
    "The same 570 flying minutes, but leaving Delhi 09:00 and landing in Copenhagen 15:15, both flights outside "
    "22:00-06:00 on every clock. No leg is over 6 hours, so neither grouping of lines 159-161 is met without an "
    "overnight flight: no exemption can be considered, and the one signed subject to the flight qualifying does not "
    "apply. Economy, Qatar.",
    twin_of="heather-cove", twin_fact="Qatar Airways leaves Delhi 09:00 (all daytime) or 20:30 (overnight); the same "
    "signed exemption in both")

scenario(
    "juniper-moss", "boundary_twin", ["multi_leg", "dearer_option"],
    "Nairobi to Copenhagen on May 9th for the INTOSAI capacity building committee, on the EgyptAir evening "
    "connection through Cairo. Business please. " + SIGNED + FALLBACK.format("committee meeting"),
    trip(traveller_name="Peter Otieno", traveller_title="Manager, Capacity Development", based_in="Nairobi, Kenya",
         origin="NBO", destination="CPH", travel_date="2027-05-09", booking_date="2027-04-12",
         purpose="INTOSAI capacity building committee in Copenhagen", engagement_starts="2027-05-10 13:00",
         requested_cabin="BUSINESS", sign_offs=[adg("Kari Nygaard"), exemption()]),
    [search("NBO", "CPH", "2027-05-09", {
        "egyptair": {"carrier": "MS", "via": ["CAI"], "depart": "20:00", "minutes": [285, 265], "layovers": [60]},
    }, [offer("egyptair-economy", "egyptair", "ECONOMY", 5200), offer("egyptair-business", "egyptair", "BUSINESS", 26500)])],
    expected("BOOK", ["egyptair-business"], ["BUSINESS"], LONG_OK, STAFF_EXEMPT_BOOK, EXEMPT),
    [CRITERIA, DG_ADDED, GIVER, NIGHT],
    "Legs of 285 and 265 minutes (none over 6 hours) add to 550 flying minutes, over 9 hours whether or not the hour in "
    "Cairo counts; the Cairo-Copenhagen flight is wholly inside the night. Eligible on every reading, the DG's "
    "exemption on file: EgyptAir business.",
    twin_of="kelp-ridge", twin_fact="the journey: 550 flying minutes (610 door to door) to Copenhagen, or 540 minutes "
    "door to door to Istanbul; the same signed exemption in both")

scenario(
    "kelp-ridge", "boundary_twin", ["multi_leg"],
    "Nairobi to Istanbul on May 9th for the INTOSAI capacity building committee, on the EgyptAir evening "
    "connection through Cairo. Business please. " + SIGNED + FALLBACK.format("committee meeting"),
    trip(traveller_name="Faith Njeri", traveller_title="Manager, Capacity Development", based_in="Nairobi, Kenya",
         origin="NBO", destination="IST", travel_date="2027-05-09", booking_date="2027-04-12",
         purpose="INTOSAI capacity building committee in Istanbul", engagement_starts="2027-05-10 13:00",
         requested_cabin="BUSINESS", sign_offs=[adg("Kari Nygaard"), exemption()]),
    [search("NBO", "IST", "2027-05-09", {
        "egyptair": {"carrier": "MS", "via": ["CAI"], "depart": "20:00", "minutes": [285, 120], "layovers": [135]},
    }, [offer("egyptair-economy", "egyptair", "ECONOMY", 4800), offer("egyptair-business", "egyptair", "BUSINESS", 22000)])],
    expected("BOOK", ["egyptair-economy"], ["ECONOMY"], NOT_MET, STAFF_EXEMPT_BOOK, AIR),
    [CRITERIA, DIRECT],
    "Legs of 285 and 120 minutes with 135 minutes in Cairo: exactly 540 minutes from first departure to last arrival, "
    "and 405 in the air. 'More than 9 hours' is strict, so the journey is not over 9 hours on either reading, and no "
    "leg is over 6 hours: no exemption can be considered, though the flight is overnight, so the one signed subject to "
    "the flight qualifying does not apply. Economy, EgyptAir.",
    twin_of="juniper-moss", twin_fact="the journey: 540 minutes door to door to Istanbul, or 550 flying minutes to "
    "Copenhagen; the same signed exemption in both")

# ===== multi-rule (4) =====

scenario(
    "larch-mere", "multi_rule", ["personal_travel", "date_arithmetic", "month_end", "outside_air_section"],
    "The DG approved business class for my Johannesburg to Amsterdam flight to the March 5th meeting. I've since "
    "decided to take a week of annual leave in Amsterdam before it, so please book me out on February 26th instead "
    "of March 4th, business as approved. " + FALLBACK.format("meeting"),
    trip(traveller_name="Lerato Dlamini", traveller_title="Manager, Women Leadership Academy",
         based_in="Johannesburg, South Africa", origin="JNB", destination="AMS", travel_date="2027-02-26",
         booking_date="2027-02-01", purpose="Programme steering meeting in Amsterdam, with a week of annual leave "
         "in Amsterdam before it", engagement_starts="2027-03-05 09:00", requested_cabin="BUSINESS",
         leave_attached="BEFORE_EVENT", usual_travel_date="2027-03-04",
         sign_offs=[adg("Lars Eide"), exemption()]),
    [search("JNB", "AMS", "2027-02-26", {
        "klm": {"carrier": "KL", "depart": "21:00", "minutes": [675]},
        "saa": {"carrier": "SA", "depart": "20:00", "minutes": [680]},
    }, [
        offer("klm-economy", "klm", "ECONOMY", 8200),
        offer("klm-business", "klm", "BUSINESS", 41500),
        offer("saa-economy", "saa", "ECONOMY", 8600),
        offer("saa-business", "saa", "BUSINESS", 44000),
    ]), search("JNB", "AMS", "2027-03-04", {
        "klm": {"carrier": "KL", "depart": "21:00", "minutes": [675]},
        "saa": {"carrier": "SA", "depart": "20:00", "minutes": [680]},
    }, [
        offer("usual-klm-economy", "klm", "ECONOMY", 8900),
        offer("usual-klm-business", "klm", "BUSINESS", 43000),
        offer("usual-saa-economy", "saa", "ECONOMY", 9100),
        offer("usual-saa-business", "saa", "BUSINESS", 45500),
    ], name="usual")],
    expected("BOOK", ["klm-economy"], ["ECONOMY"], ["PERSONAL_TRAVEL_NOT_COVERED", "UPGRADE_NOT_ELIGIBLE", "VACATION_SEGMENT_ECONOMY"],
             STAFF_EXEMPT_BOOK, ["ACCOMMODATION_MEALS", "PERSONAL_TRAVEL_VACATION"]),
    [VACATION, CRITERIA, GIVER],
    "The flight itself meets the criteria (675 minutes overnight) and the DG's business exemption is on file, but the "
    "traveller now takes vacation just before the event: lines 240-242 say the employee must travel economy for that "
    "segment, at a price not over the ticket without the holiday. The cheapest economy fare on the 26th (KLM, NOK "
    "8,200) is below even the March 4th economy fare (NOK 8,900), let alone the business fare, so it is within the cap "
    "on any reading. The leave runs across the end of February. The record names the usual date, so its search is "
    "pinned.")

scenario(
    "maple-tarn", "multi_rule", [],
    "I'm flying Johannesburg to London on January 16th for the two-week public sector audit methodology course that "
    "starts on the 18th. It's a long flight, so business please; I've sent my exemption form to the DG. "
    + FALLBACK.format("course"),
    trip(traveller_name="Sipho Ndlovu", traveller_title="Senior Manager, Professional SAIs",
         based_in="Johannesburg, South Africa", origin="JNB", destination="LHR", travel_date="2027-01-16",
         booking_date="2026-12-17", purpose="Two-week course in public sector audit methodology in London",
         purpose_kind="COURSE", engagement_starts="2027-01-18 09:00", requested_cabin="BUSINESS",
         exemption_pending=True, sign_offs=[adg("Kari Nygaard")]),
    [search("JNB", "LHR", "2027-01-16", {
        "british": {"carrier": "BA", "depart": "20:30", "minutes": [680]},
        "saa": {"carrier": "SA", "depart": "19:45", "minutes": [685]},
    }, [
        offer("british-economy", "british", "ECONOMY", 8100),
        offer("british-business", "british", "BUSINESS", 40200),
        offer("saa-economy", "saa", "ECONOMY", 7700),
        offer("saa-business", "saa", "BUSINESS", 38900),
    ])],
    expected("BOOK", ["saa-economy"], ["ECONOMY"], ["COURSE_TRAVEL_ECONOMY", "UPGRADE_NOT_ELIGIBLE"], STAFF_BOOK, AIR),
    [COURSE, CRITERIA],
    "The overnight 680-minute flight would meet the exemption criteria of lines 159-161, but line 176 says travel for "
    "courses and studies should always be on an economy ticket, so there is nothing to hold for: book the cheapest "
    "economy fare (South African Airways).",
    distractors=[COMPENSATION])

scenario(
    "nutmeg-vale", "multi_rule", ["dearer_option"],
    "Since my spine surgery my doctor has certified that I can't sit upright in a standard seat for long. The DG has "
    "approved business class for me on that basis. Please book business Nairobi to Johannesburg on the morning of "
    "March 15th for the regional audit workshop.",
    trip(traveller_name="Esther Wambui", traveller_title="Manager, Audit Quality", based_in="Nairobi, Kenya",
         origin="NBO", destination="JNB", travel_date="2027-03-15", booking_date="2027-02-19",
         purpose="Regional audit workshop in Johannesburg", purpose_kind="WORKSHOP",
         engagement_starts="2027-03-16 09:00", requested_cabin="BUSINESS", medical_certificate_on_file=True,
         sign_offs=[adg("Lars Eide"), exemption()]),
    [search("NBO", "JNB", "2027-03-15", {
        "kenya": {"carrier": "KQ", "depart": "08:00", "minutes": [240]},
        "saa": {"carrier": "SA", "depart": "10:30", "minutes": [245]},
    }, [
        offer("kenya-economy", "kenya", "ECONOMY", 3400),
        offer("kenya-business", "kenya", "BUSINESS", 14800),
        offer("saa-economy", "saa", "ECONOMY", 3600),
        offer("saa-business", "saa", "BUSINESS", 15900),
    ])],
    expected("BOOK", ["kenya-business"], ["BUSINESS"], ["CABIN_EXEMPTION_AUTHORIZED", "MEDICAL_NEED"],
             STAFF_EXEMPT_BOOK, EXEMPT),
    [MEDICAL, GIVER, CRITERIA],
    "A 240-minute daytime flight fails the duration and overnight criteria, but line 164 lets exemptions also be made "
    "for duly certified medical reasons; the certificate and the DG's exemption are on file. The cheapest business "
    "fare, Kenya Airways.")

scenario(
    "oriole-peak", "multi_rule", ["dearer_option"],
    "Business class please from Bogota to Madrid on March 22nd, on one of the evening flights, for the joint "
    "OLACEFS-EUROSAI meeting. The DG signed my exemption. " + FALLBACK.format("meeting"),
    trip(traveller_name="Camila Restrepo", traveller_title="Senior Manager, Regional Cooperation",
         based_in="Bogota, Colombia", origin="BOG", destination="MAD", travel_date="2027-03-22",
         booking_date="2027-02-24", purpose="Joint OLACEFS-EUROSAI meeting in Madrid",
         engagement_starts="2027-03-24 09:00", requested_cabin="BUSINESS",
         sign_offs=[adg("Kari Nygaard"), exemption("PREMIUM_ECONOMY")]),
    [search("BOG", "MAD", "2027-03-22", {
        "avianca": {"carrier": "AV", "depart": "18:30", "minutes": [605]},
        "iberia": {"carrier": "IB", "depart": "20:00", "minutes": [610]},
    }, [
        offer("avianca-economy", "avianca", "ECONOMY", 7400),
        offer("avianca-premium", "avianca", "PREMIUM_ECONOMY", 12600),
        offer("avianca-business", "avianca", "BUSINESS", 36000),
        offer("iberia-economy", "iberia", "ECONOMY", 7900),
        offer("iberia-premium", "iberia", "PREMIUM_ECONOMY", 13400),
        offer("iberia-business", "iberia", "BUSINESS", 38800),
    ])],
    expected("BOOK", ["avianca-premium"], ["PREMIUM_ECONOMY"],
             ["CABIN_EXEMPTION_AUTHORIZED", "PREMIUM_ECONOMY_ALLOWED", "UPGRADE_NOT_ELIGIBLE"], STAFF_EXEMPT_BOOK,
             EXEMPT),
    [CRITERIA, DG_ADDED, GIVER],
    "The overnight 605-minute flight meets the criteria, but the exemption the DG signed (lines 135-136, 165) is for "
    "premium economy, not business: business is not authorised, and premium economy is. The cheapest premium economy "
    "fare, Avianca.")

# ===== hidden clause (2) =====

scenario(
    "plover-glen", "hidden_clause", ["dearer_option"],
    "I'm flying Mexico City to Madrid on April 20th for the IDI Board meeting. Business class please on one of the "
    "evening flights; Elena Ruiz-Calderon signed my exemption.",
    trip(traveller_name="Alejandro Vega", traveller_title="Member of the IDI Board; Auditor General",
         passenger="BOARD_MEMBER", based_in="Mexico City, Mexico", origin="MEX", destination="MAD",
         travel_date="2027-04-20", booking_date="2027-03-24", purpose="IDI Board meeting in Madrid",
         purpose_kind="BOARD_MEETING", engagement_starts="2027-04-22 09:00", requested_cabin="BUSINESS",
         sign_offs=[sign("BOARD_CHAIR", CHAIR, "TRAVEL_AUTHORITY"),
                    sign("BOARD_CHAIR", CHAIR, "CABIN_EXEMPTION", "BUSINESS")]),
    [search("MEX", "MAD", "2027-04-20", {
        "aeromexico": {"carrier": "AM", "depart": "17:30", "minutes": [680]},
        "iberia": {"carrier": "IB", "depart": "18:45", "minutes": [685]},
    }, [
        offer("aeromexico-economy", "aeromexico", "ECONOMY", 8800),
        offer("aeromexico-business", "aeromexico", "BUSINESS", 44500),
        offer("iberia-economy", "iberia", "ECONOMY", 9300),
        offer("iberia-business", "iberia", "BUSINESS", 47000),
    ])],
    expected("BOOK", ["aeromexico-business"], ["BUSINESS"], LONG_OK, ["BOARD_CHAIR", "NONE"], EXEMPT),
    [GIVER, CRITERIA, NIGHT],
    "A Board member on a 680-minute overnight flight. Line 165: exemptions for IDI Board members are authorised by the "
    "Chair of the IDI Board, not the DG, and the Chair's exemption is on file. The DG-approval wording of lines "
    "135-136 is for staff. Book the cheapest business fare, Aeromexico.")

KIN_FLIGHTS = {
    "kenya": {"carrier": "KQ", "depart": "08:00", "minutes": [240]},
    "saa": {"carrier": "SA", "depart": "10:30", "minutes": [245]},
}
KIN_OFFERS = [
    offer("kenya-economy", "kenya", "ECONOMY", 3400),
    offer("kenya-business", "kenya", "BUSINESS", 14800),
    offer("saa-economy", "saa", "ECONOMY", 3600),
]


def kin_trip(**fields):
    return trip(traveller_name="Daniel Otieno", traveller_title="Husband of Achieng Otieno, Manager, Audit Quality",
                passenger="FAMILY_MEMBER", goes_to="Achieng Otieno", based_in="Nairobi, Kenya", origin="NBO",
                destination="JNB", travel_date="2027-03-09", booking_date="2027-03-08", purpose_kind="FAMILY",
                **fields)


scenario(
    "quartz-heath", "hidden_clause", ["outside_air_section"],
    "My wife, Achieng Otieno, was hurt in a road accident in Johannesburg while she was there for an IDI workshop, and "
    "she's in hospital and needs me with her. Her ADG has authorised my trip. Please book me economy Nairobi to "
    "Johannesburg tomorrow, March 9th.",
    kin_trip(purpose="To be with his wife in hospital after she was injured on IDI travel in Johannesburg",
             staff_ill_on_duty=True, sign_offs=[adg("Kari Nygaard")]),
    [search("NBO", "JNB", "2027-03-09", KIN_FLIGHTS, KIN_OFFERS)],
    expected("BOOK", ["kenya-economy"], ["ECONOMY"], ["LOWEST_FARE", "NEXT_OF_KIN_TRAVEL"], STAFF_BOOK,
             ["ILLNESS_ACCIDENT", "SPECIAL_SITUATIONS"]),
    [KIN, AUTHORITY, CRITERIA],
    "The policy covers staff and Board members (lines 57-58), but lines 251-253 cover actual and reasonable "
    "transportation for next of kin when a staff member is injured on official duty and needs them. The trip is "
    "authorised by her ADG. Economy at the lowest fare, Kenya Airways.",
    twin_of="umber-loch", twin_fact="the staff member is in hospital after an accident on IDI travel (and her ADG "
    "authorised the trip), or simply at the workshop")

# ===== distractors (2) =====

scenario(
    "rowan-strand", "distractor", [],
    "I'm in Copenhagen and need to get to Frankfurt on May 3rd for the donor meeting at 15:00. A colleague told me "
    "IDI staff may book business class on short trips within Europe, so business please. " + FALLBACK.format("meeting"),
    trip(traveller_name="Ingrid Solheim", traveller_title="Senior Manager, Global Foundations Unit",
         based_in="Oslo, Norway", origin="CPH", destination="FRA", travel_date="2027-05-03",
         booking_date="2027-04-14", purpose="Donor meeting in Frankfurt", engagement_starts="2027-05-03 15:00",
         requested_cabin="BUSINESS", sign_offs=[adg("Lars Eide")]),
    [search("CPH", "FRA", "2027-05-03", {
        "early": {"carrier": "LH", "depart": "07:30", "minutes": [80]},
        "midday": {"carrier": "LH", "depart": "11:15", "minutes": [80]},
    }, [
        offer("early-economy", "early", "ECONOMY", 1850),
        offer("early-business", "early", "BUSINESS", 5400),
        offer("midday-economy", "midday", "ECONOMY", 1690),
        offer("midday-business", "midday", "BUSINESS", 5100),
    ])],
    expected("BOOK", ["midday-economy"], ["ECONOMY"], NOT_MET, STAFF_BOOK, AIR),
    [CRITERIA, DIRECT],
    "An 80-minute daytime flight meets none of the exemption criteria (lines 156-161): economy. The business or premium "
    "class of line 195 is for train or bus travel, not flights. The 11:15 flight lands 12:35, before the 15:00 meeting. "
    "The cheapest economy fare.",
    distractors=[TRAIN])

scenario(
    "saffron-isle", "distractor", ["multi_leg"],
    "Cairo to Copenhagen on June 7th for the SAI performance measurement meeting the next morning. Please book the "
    "Turkish Airlines connection through Istanbul: it has a long stop, and staff get lounge access on stops like that. "
    "If the policy wants a different flight, book that; I have to be at the meeting.",
    trip(traveller_name="Nadia Hassan", traveller_title="Manager, Performance Measurement", based_in="Cairo, Egypt",
         origin="CAI", destination="CPH", travel_date="2027-06-07", booking_date="2027-05-17",
         purpose="SAI performance measurement meeting in Copenhagen", engagement_starts="2027-06-08 09:00",
         requested_connection="IST", sign_offs=[adg("Kari Nygaard")]),
    [search("CAI", "CPH", "2027-06-07", {
        "turkish": {"carrier": "TK", "via": ["IST"], "depart": "08:00", "minutes": [125, 170], "layovers": [230]},
        "lufthansa": {"carrier": "LH", "via": ["FRA"], "depart": "08:30", "minutes": [240, 80], "layovers": [70]},
    }, [
        offer("turkish-economy", "turkish", "ECONOMY", 4450),
        offer("lufthansa-economy", "lufthansa", "ECONOMY", 4100),
    ])],
    expected("BOOK", ["lufthansa-economy"], ["ECONOMY"],
             ["ALTERNATE_ROUTE_TOO_EXPENSIVE", "CONNECTION_TOO_LONG", "COST_SAVINGS", "DIRECT_ECONOMICAL_ROUTE",
              "LOWEST_FARE"], STAFF_BOOK,
             ECONOMY),
    [DIRECT, ECONOMICAL],
    "Line 155: the most direct and economical route. Both itineraries connect once; the Frankfurt one is cheaper (NOK "
    "4,100 against 4,450) and quicker (390 against 525 minutes), so it is both the more direct and the more economical. "
    "The lounge of line 169 is an entitlement on a stopover over three hours, not a reason to choose a routing. Both "
    "land the afternoon before the meeting.",
    distractors=[LOUNGE])

# ===== refusals (2) =====

scenario(
    "tamarind-wold", "refusal", ["personal_travel", "date_arithmetic", "outside_air_section"],
    "The Amsterdam workshop runs from Thursday April 15th to Tuesday April 20th with nothing on over the weekend. I'd "
    "like to spend Saturday and Sunday in Barcelona, so please book me Amsterdam to Barcelona on Saturday the 17th; "
    "I'll fly back for Monday.",
    trip(traveller_name="Kofi Mensah", traveller_title="Manager, Bilateral Support", based_in="Nairobi, Kenya",
         origin="AMS", destination="BCN", travel_date="2027-04-17", booking_date="2027-04-08",
         purpose="A weekend in Barcelona during the break of the Amsterdam workshop (April 15-20)",
         purpose_kind="PERSONAL", sign_offs=[adg("Lars Eide")]),
    [search("AMS", "BCN", "2027-04-17", {
        "morning": {"carrier": "KL", "depart": "08:20", "minutes": [125]},
        "midday": {"carrier": "KL", "depart": "12:40", "minutes": [125]},
    }, [
        offer("morning-economy", "morning", "ECONOMY", 1450),
        offer("midday-economy", "midday", "ECONOMY", 1620),
    ])],
    expected("REFUSE", [], ["NONE"], ["OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED"], STAFF_BOOK,
             ["ACCOMMODATION_MEALS", "PERSONAL_TRAVEL_VACATION"]),
    [WEEKEND],
    "Lines 234-239: the staff member is not required to stay in Amsterdam over the weekend and chooses another "
    "location of personal choice; transportation related to that stay shall not be reimbursed. The IDI buys no ticket. "
    "The ADG's travel authority for the workshop is on file but unused (NONE or the ADG).",
    distractors=[DAY])

scenario(
    "umber-loch", "refusal", ["outside_air_section"],
    "My wife, Achieng Otieno, is in Johannesburg for an IDI workshop this week, and I'd like to join her there. Please "
    "book me economy Nairobi to Johannesburg tomorrow, March 9th.",
    kin_trip(purpose="To join his wife at her IDI workshop in Johannesburg"),
    [search("NBO", "JNB", "2027-03-09", KIN_FLIGHTS, KIN_OFFERS)],
    expected("REFUSE", [], ["NONE"], ["COMPANION_NOT_COVERED", "OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED"],
             ["NONE"], ["AREA_OF_APPLICATION", "ILLNESS_ACCIDENT", "SPECIAL_SITUATIONS"]),
    [SCOPE, KIN],
    "Lines 57-58: the policy applies only to IDI staff and Board members. A family member's transportation is covered "
    "only when a staff member is ill or injured on duty and needs next of kin (lines 251-253); she is not. The IDI "
    "buys no ticket.",
    twin_of="quartz-heath", twin_fact="the staff member is simply at the workshop, or in hospital after an accident "
    "on IDI travel (with her ADG's authorisation)")

# ===== flags (3) =====

scenario(
    "violet-crag", "flag", [],
    "Johannesburg to Dubai on June 14th for the INTOSAI regional coordination meeting, on the Emirates morning flight. "
    "It's a long flight, so business please; I've sent my exemption form to the DG. " + FALLBACK.format("meeting"),
    trip(traveller_name="Naledi Khumalo", traveller_title="Senior Manager, Regional Cooperation",
         based_in="Johannesburg, South Africa", origin="JNB", destination="DXB", travel_date="2027-06-14",
         booking_date="2027-05-18", purpose="INTOSAI regional coordination meeting in Dubai",
         engagement_starts="2027-06-15 09:00", requested_cabin="BUSINESS", exemption_pending=True,
         sign_offs=[adg("Lars Eide")]),
    [search("JNB", "DXB", "2027-06-14", {
        "emirates": {"carrier": "EK", "depart": "08:00", "minutes": [490]},
        "saa": {"carrier": "SA", "depart": "09:30", "minutes": [495]},
    }, [
        offer("emirates-economy", "emirates", "ECONOMY", 6300),
        offer("emirates-business", "emirates", "BUSINESS", 30200),
        offer("saa-economy", "saa", "ECONOMY", 6700),
        offer("saa-business", "saa", "BUSINESS", 32500),
    ])],
    expected("FLAG_FOR_APPROVAL", ["emirates-business", "emirates-economy"], ["BUSINESS", "ECONOMY"],
             UNCLEAR_REASONS, UNCLEAR_ROLES, EXEMPT, phrase="and where travel involves overnight flights"),
    [CRITERIA, DG_ADDED, GIVER, NIGHT],
    "A 490-minute daytime nonstop (08:00-18:10 Dubai time, no minute of it between 22:00 and 06:00). Lines 159-161: "
    "'One leg ... more than 6 hours ... or the total journey lasts for more than 9 hours, and where travel involves "
    "overnight flights'. Read as (long leg or long journey) and overnight, no exemption can be considered: book "
    "economy. Read as long leg, or (long journey and overnight), the long leg qualifies and the pending exemption is "
    "the DG's to decide: hold business. Hold either offer.",
    flag_twins=["birch-lagoon", "iris-shoal"],
    ambiguity={"phrase": "and where travel involves overnight flights",
               "readings": [("the overnight condition governs both the leg and the journey test: a daytime flight "
                            "never qualifies, so book economy"),
                            ("the overnight condition goes with the journey test only: a leg over 6 hours qualifies "
                            "by day, so hold business for the DG's exemption")]})

scenario(
    "willow-burn", "flag", ["multi_leg"],
    "Delhi to Copenhagen on June 20th for the partnership conference, on the Turkish Airlines 01:30 connection through "
    "Istanbul. Business please; I've sent my exemption form to the DG. " + FALLBACK.format("conference"),
    trip(traveller_name="Kavita Sharma", traveller_title="Senior Manager, SAI Governance", based_in="New Delhi, India",
         origin="DEL", destination="CPH", travel_date="2027-06-20", booking_date="2027-05-24",
         purpose="Nordic SAI partnership conference in Copenhagen", purpose_kind="CONFERENCE",
         engagement_starts="2027-06-21 13:00", requested_cabin="BUSINESS", exemption_pending=True,
         sign_offs=[adg("Kari Nygaard")]),
    [search("DEL", "CPH", "2027-06-20", {
        "turkish": {"carrier": "TK", "via": ["IST"], "depart": "01:30", "minutes": [355, 170], "layovers": [80]},
    }, [offer("turkish-economy", "turkish", "ECONOMY", 5800), offer("turkish-business", "turkish", "BUSINESS", 27600)])],
    expected("FLAG_FOR_APPROVAL", ["turkish-business", "turkish-economy"], ["BUSINESS", "ECONOMY"], UNCLEAR_REASONS,
             UNCLEAR_ROLES, EXEMPT, phrase="the total journey lasts for more than 9 hours"),
    [CRITERIA, DG_ADDED, GIVER, NIGHT],
    "Legs of 355 and 170 minutes (none over 6 hours), 80 minutes in Istanbul: 525 minutes in the air, 605 from Delhi "
    "to Copenhagen. The Delhi-Istanbul flight leaves 01:30 and flies through the night on both clocks. Whether 'the "
    "total journey lasts for more than 9 hours' counts the time on the ground decides it: with it, the criteria hold "
    "and the pending exemption is the DG's to decide (hold business); without it, they fail (economy). Hold either.",
    flag_twins=["juniper-moss", "kelp-ridge"],
    ambiguity={"phrase": "the total journey lasts for more than 9 hours",
               "readings": [("the journey runs from first departure to last arrival (605 minutes): over 9 hours and "
                            "overnight, so hold business for the DG's exemption"),
                            ("the journey is the time in the air (525 minutes): not over 9 hours and no leg over 6, so "
                            "book economy")]})

scenario(
    "yarrow-spit", "flag", ["approval_required", "dearer_option"],
    "Business class please on the Kenya Airways 22:30 flight from Nairobi to Mumbai on March 7th; I've sent my "
    "exemption form to the DG. " + FALLBACK.format("workshop"),
    mumbai_trip("Samuel Kiprono", "Manager, Bilateral Support", sign_offs=[adg("Kari Nygaard")],
                exemption_pending=True),
    mumbai(361),
    expected("FLAG_FOR_APPROVAL", ["kenya-business"], ["BUSINESS"], ["APPROVAL_REQUIRED"], ["DIRECTOR_GENERAL"],
             EXEMPT),
    [CRITERIA, DG_ADDED, GIVER, NIGHT],
    "The Kenya Airways nonstop is 361 minutes, over 6 hours, and overnight on both clocks: an exemption may be "
    "considered (lines 159-161), but only the DG may authorise it for staff (lines 135-136, 165), and the application "
    "is still pending. Hold the business fare for the DG; approval required, not 'no compliant offer'. Same flights as "
    "fennel-quay (signed: business), with the application still pending, and one minute longer than garnet-brook "
    "(360 minutes: economy whatever is signed).",
    flag_twins=["fennel-quay", "garnet-brook"],
    ambiguity="none: an approval is required and missing; the text is clear")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for data in S:
        (OUT / f"{data['id']}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(S)} scenarios to {OUT}")


if __name__ == "__main__":
    main()
