class VastuScorer:

    ROOM_WEIGHTS = {
        "pooja_room": 20,
        "kitchen": 20,
        "master_bedroom": 15,
        "living_room": 10,
        "bathroom": 10,
        "staircase": 10,
        "bedroom": 10
    }

    REASONING_MAP = {
        "kitchen": {
            "preferred": "The South-East (SE) is the ideal Agni (Fire) corner.",
            "allowed": "North-West (NW) is a supportive alternative for the Kitchen.",
            "avoid": "Avoid North-East (NE) for Kitchen as water and fire clash here.",
            "flexible": "Placement is neutral but not optimal.",
            "benefit": "SE placement harnesses the fire element (Agni), promoting good health, digestive strength, and family prosperity."
        },
        "master_bedroom": {
            "preferred": "South-West (SW) brings stability, strength, and leadership qualities.",
            "allowed": "West or South zones are acceptable for the Master Bedroom.",
            "avoid": "North-East (NE) should be avoided for the Master Bedroom due to health concerns.",
            "flexible": "Placement here is passable but SW is strongly recommended.",
            "benefit": "SW placement ensures stability, confident leadership, and sound sleep for the head of the family."
        },
        "pooja_room": {
            "preferred": "North-East (NE) is the Ishan corner, perfect for meditation and connection to divine energy.",
            "allowed": "East or North walls are good alternatives.",
            "avoid": "Avoid South (S) or South-West (SW) for the Pooja room.",
            "flexible": "Placement is neutral.",
            "benefit": "NE placement connects with cosmic energies, enhancing spiritual growth, peace, and mental clarity."
        },
        "bathroom": {
            "preferred": "North-West (NW) is ideal for waste disposal and cleanliness.",
            "allowed": "South-East (SE) is also acceptable.",
            "avoid": "Never place a bathroom in the North-East (NE) or center (Brahmasthan).",
            "flexible": "Placement is neutral.",
            "benefit": "NW placement aids in effective waste elimination and prevents the stagnation of negative energies."
        },
        "living_room": {
            "preferred": "North-East (NE) or North (N) allows positive morning energy to enter the house.",
            "allowed": "East and North-West are also good locations.",
            "avoid": "No major restrictions, but avoid South-West (SW) for main entry if possible.",
            "flexible": "Placement is generally flexible.",
            "benefit": "NE/N placement invites fresh prana (life force) and positive social interactions for the family."
        },
        "staircase": {
            "preferred": "South (S), South-West (SW), or West (W) are best for heavy structures like stairs.",
            "avoid": "Avoid North-East (NE) as it should be kept light and open.",
            "flexible": "Placement is neutral.",
            "benefit": "Placement in heavy zones (S/SW) provides structural stability and blocks negative energies from these directions."
        },
        "dining_area": {
            "preferred": "West (W) is the best zone for dining and nourishment.",
            "allowed": "East (E) or North (N) are decent alternatives.",
            "avoid": "South-West (SW) is not recommended.",
            "flexible": "Placement is neutral.",
            "benefit": "West placement fosters profitability and ensures food is enjoyed in a relaxed atmosphere."
        },
        "bedroom": {
            "preferred": "West (W) or North-West (NW) is good for children or guests.",
            "allowed": "South (S) is also stable.",
            "avoid": "Avoid North-East (NE) for bedrooms if possible.",
            "flexible": "Placement is neutral.",
            "benefit": "West placement is excellent for gains and studying; NW supports movement and guests."
        },
        "parking": {
            "preferred": "North-West (NW) or South-East (SE) provides movement and mobility.",
            "avoid": "Avoid South-West (SW) or North-East (NE) for parking.",
            "flexible": "Placement is neutral.",
            "benefit": "NW placement ensures vehicles are constantly in use and reduces maintenance issues."
        }
    }

    def calculate_score(self, layout, rules):
        total_score = 0
        max_score = 0 # Calculate dynamically based on actual rooms present
        breakdown = {}

        for room, zone in layout.items():
            # Handle identifiers like bedroom_2
            base_name = room.split("_")[0] 
            if "master" in room: base_name = "master_bedroom"
            if "living" in room: base_name = "living_room"
            if "dining" in room: base_name = "dining_area"
            if "pooja" in room: base_name = "pooja_room"
            if "kitchen" in room: base_name = "kitchen"
            
            # 1. Determine Weight
            weight = self.ROOM_WEIGHTS.get(base_name, self.ROOM_WEIGHTS.get(room, 5)) 
            max_score += weight # Add to total potential score

            # 2. Determine Rule Compliance
            rule = rules.get(base_name, rules.get(room, {}))
            
            # 3. Score & Logic
            score_val = 0
            reason_template = self.REASONING_MAP.get(base_name, {})
            
            if zone in rule.get("preferred", []):
                score_val = weight
                reason = reason_template.get("preferred", f"{zone} is the best zone for {base_name}.")
            elif zone in rule.get("allowed", []):
                score_val = weight * 0.7
                reason = reason_template.get("allowed", f"{zone} is an allowed zone for {base_name}.")
            elif zone in rule.get("avoid", []):
                score_val = 0
                reason = reason_template.get("avoid", f"{zone} should be avoided for {base_name}.")
            else:
                score_val = weight * 0.4
                reason = reason_template.get("flexible", f"{zone} is a neutral placement for {base_name}.")

            benefit = reason_template.get("benefit", "Balances the layout's energy flow.")

            total_score += score_val
            breakdown[room] = {
                "zone": zone,
                "score": round(score_val, 2),
                "max": weight,
                "reason": reason,
                "benefit": benefit
            }

        if max_score == 0:
            percentage = 0
        else:
            percentage = round((total_score / max_score) * 100, 2)

        return percentage, breakdown
