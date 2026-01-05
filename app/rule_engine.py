import json
import os

class VastuRuleEngine:
    def __init__(self, rule_file="app/vastu_rules.json"):
        BASE_DIR = os.path.dirname(__file__)
        with open(os.path.join(BASE_DIR, "vastu_rules.json"), "r") as f:
            self.rules = json.load(f)["rules"]

    def get_zone_for_room(self, room_name, vastu_level):
        rule = self.rules.get(room_name, {})

        if vastu_level == "high":
            return rule.get("preferred", [])

        if vastu_level == "medium":
            return rule.get("preferred", []) + rule.get("allowed", [])

        # Low compliance
        return [z for z in ["N","NE","E","SE","S","SW","W","NW", "Center"]
                if z not in rule.get("avoid", [])]
    
    def get_all_rules(self):
        return self.rules

