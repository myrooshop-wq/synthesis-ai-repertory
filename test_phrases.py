import re

PHRASE_EXPANSIONS = {
    "loose motion": ["RECTUM - DIARRHEA", "STOOL - THIN", "STOOL - WATERY"],
    "loose motions": ["RECTUM - DIARRHEA", "STOOL - THIN", "STOOL - WATERY"],
    "watery stool": ["RECTUM - DIARRHEA", "STOOL - WATERY"],
    "stomach ache": ["ABDOMEN - PAIN", "STOMACH - PAIN"],
    "belly ache": ["ABDOMEN - PAIN"],
    "runny nose": ["NOSE - CORYZA", "NOSE - DISCHARGE"],
    "body ache": ["GENERALS - PAIN", "EXTREMITIES - PAIN"],
    "limb pain": ["EXTREMITIES - PAIN"],
    "loss of appetite": ["STOMACH - APPETITE - wanting"],
    "no appetite": ["STOMACH - APPETITE - wanting"],
    "burning stomach": ["STOMACH - PAIN - burning"],
    "burning in stomach": ["STOMACH - PAIN - burning"],
    "dry mouth": ["MOUTH - DRYNESS"],
    "restless night": ["MIND - RESTLESSNESS - night", "SLEEP - RESTLESS - night"],
    "restlessness at night": ["MIND - RESTLESSNESS - night"],
    "night sweat": ["PERSPIRATION - NIGHT"],
    "sweating at night": ["PERSPIRATION - NIGHT"],
    "high fever": ["FEVER - INTENSE heat", "FEVER - CONTINUED fever"],
    "chill with fever": ["FEVER - CHILL; with", "CHILL - FEVER; with"],
    "migraine": ["HEAD - PAIN", "HEAD - PAIN - Sides - one side"],
    "headache": ["HEAD - PAIN"],
    "vomiting": ["STOMACH - VOMITING"],
    "nausea": ["STOMACH - NAUSEA"],
    "acidity": ["STOMACH - ERUCTATIONS; TYPE OF - sour", "STOMACH - ACIDITY"],
    "gas in stomach": ["ABDOMEN - DISTENSION", "ABDOMEN - FLATULENCE"],
    "bloating": ["ABDOMEN - DISTENSION"]
}

print("Phrases defined:", len(PHRASE_EXPANSIONS))
