class LayoutOptimizer:
    ROOM_PRIORITY = [
        "pooja_room",
        "kitchen",
        "master_bedroom",
        "living_room",
        "bedroom",
        "bathroom",
        "staircase",
        "balcony"
    ]

    ZONE_COORDS = {
        "NW": (0, 0), "N": (0, 1), "NE": (0, 2),
        "W": (1, 0), "Center": (1, 1), "E": (1, 2),
        "SW": (2, 0), "S": (2, 1), "SE": (2, 2)
    }

    RELATIONSHIPS = {
        "dining_area": ["kitchen"],
        "bathroom": ["master_bedroom", "bedroom", "bedroom_1", "bedroom_2"],
        "pooja_room": ["living_room"],
        "living_room": ["center", "dining_area"]
    }

    def _get_dist(self, z1, z2):
        if z1 not in self.ZONE_COORDS or z2 not in self.ZONE_COORDS: return 99
        r1, c1 = self.ZONE_COORDS[z1]
        r2, c2 = self.ZONE_COORDS[z2]
        return abs(r1-r2) + abs(c1-c2)

    def optimize(self, room_zones):
        # Wrapper for backward compatibility if needed, returns best single layout
        variants = self.generate_variants(room_zones, count=1)
        return variants[0][0], variants[0][1]

    def generate_variants(self, room_zones, count=3):
        import random
        
        candidates = []
        seen_hashes = set()
        
        # Strategies: 
        # 1. Greedy (Best Fit)
        # 2. Kitchen Alternative (Force Kitchen to 2nd choice if avail)
        # 3. Master Bed Alternative 
        # 4. Randomized
        
        attempts = 0
        max_attempts = 50
        
        while len(candidates) < count and attempts < max_attempts:
            attempts += 1
            
            assigned = {}
            zone_capacity = {k: 0 for k in ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "Center"]}
            MAX_PER_ZONE = 3
            notes = []
            
            # Randomized Priority for variety in non-critical rooms
            # But keep Critical rooms (Kitchen, Master) high priority
            current_priority = self.ROOM_PRIORITY.copy()
            if attempts > 1:
                # Shuffle the middle/lower priority items to induce variation
                mid_idx = 3
                sub_list = current_priority[mid_idx:]
                random.shuffle(sub_list)
                current_priority = current_priority[:mid_idx] + sub_list
            
            sorted_rooms = sorted(
                room_zones.keys(),
                key=lambda r: current_priority.index(r) if r in current_priority else 99
            )
            
            valid_layout = True
            
            # Dynamic Relationships for this floor
            current_rels = self._setup_dynamic_relationships(room_zones)
            
            for room in sorted_rooms:
                possible_zones = list(room_zones[room])
                
                # Adjacency Logic (Dynamic)
                related_rooms = current_rels.get(room, [])
                anchor_zone = None
                for related in related_rooms:
                    if related in assigned:
                        anchor_zone = assigned[related]
                        break
                
                # Sort by adjacency if anchor exists
                if anchor_zone:
                    possible_zones.sort(key=lambda z: self._get_dist(z, anchor_zone))
                
                # Randomize if no anchor and not first attempt (to get variety)
                elif attempts > 1:
                    # Keep Preferred at top, but shuffle within Preferred?
                    # valid_zones is usually [Preferred..., Allowed...]
                    # Let's shuffle the whole list slightly but bias towards front?
                    # Simple shuffle for exploration
                    if random.random() < 0.3: # 30% chance to shuffle preferences
                         random.shuffle(possible_zones)

                placed = False
                for zone in possible_zones:
                    if zone_capacity.get(zone, 0) < MAX_PER_ZONE:
                        assigned[room] = zone
                        zone_capacity[zone] = zone_capacity.get(zone, 0) + 1
                        placed = True
                        break
                
                if not placed:
                    # Fallback
                    fallback_preference = ["NW", "SE", "W", "S", "E", "N", "Center"]
                    if anchor_zone:
                         fallback_preference.sort(key=lambda z: self._get_dist(z, anchor_zone))
                    
                    for zone in fallback_preference:
                         if zone_capacity.get(zone, 0) < MAX_PER_ZONE:
                            assigned[room] = zone
                            zone_capacity[zone] = zone_capacity.get(zone, 0) + 1
                            placed = True
                            notes.append(f"{room} placed in {zone} (Fallback)")
                            break
                            
                if not placed:
                    assigned[room] = "Flexible"
                    # Ideally mark as invalid if critical room missing
                    # But we'll just accept it with a note
            
            # Check uniqueness
            # Hash based on sorted tuples of (room, zone)
            layout_hash = tuple(sorted(assigned.items()))
            if layout_hash not in seen_hashes:
                seen_hashes.add(layout_hash)
                candidates.append((assigned, notes))
        
        # If we failed to get random variants, just return the greedy one duplicated
        if not candidates:
             candidates.append(self.optimize(room_zones))
             
        return candidates

    def _setup_dynamic_relationships(self, room_zones):
        """
        Dynamically adjusts relationships based on available rooms.
        e.g. If 1 Bath and 2 Beds -> Common Bath logic.
        """
        rels = self.RELATIONSHIPS.copy()
        
        rooms = list(room_zones.keys())
        bedrooms = [r for r in rooms if "bedroom" in r and "master" not in r]
        master = [r for r in rooms if "master_bedroom" in r]
        bathrooms = [r for r in rooms if "bathroom" in r]
        
        # 1. Master Suite Logic
        if master and bathrooms:
            # The "main" bathroom usually attaches to Master
            main_bath = bathrooms[0] # "bathroom"
            rels[main_bath] = ["master_bedroom"]
            
        # 2. Common vs Attached for others
        # Remaining beds & baths
        other_beds = bedrooms
        other_baths = bathrooms[1:] if len(bathrooms) > 1 else []
        
        if other_beds and not other_baths:
            # We have extra beds but no extra baths. 
            # The Main Bath might need to be shared? Or assume Error?
            # Or usually "bathroom" is just one.
            if len(bathrooms) == 1 and (len(master) + len(other_beds)) > 1:
                # 1 Bath, Multiple Beds -> Common Bath
                # Ideally near Dining/Center or equidistance
                rels[bathrooms[0]] = ["dining_area", "living_room", "master_bedroom"] 
                # Removing direct attach to Master to allow it to be common?
                # But Master needs it most. 
                # Let's say: prioritizes Master but accessible.
                pass
        
        elif other_beds and other_baths:
            # 1-to-1 Mapping if counts match
            for i, bed in enumerate(other_beds):
                if i < len(other_baths):
                    rels[other_baths[i]] = [bed]
        
        return rels
