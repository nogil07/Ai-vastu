class FloorAllocator:
    def __init__(self):
        pass

    def allocate(self, user_input):
        """
        Distributes rooms into 'ground_floor' and 'first_floor' (and 'second_floor' etc.)
        based on user_input.building.floors and room types.
        """
        floors_config = user_input.building.floors.lower()
        
        # Determine number of floors
        num_floors = 1
        if "g+1" in floors_config or "2" in floors_config:
            num_floors = 2
        elif "g+2" in floors_config or "3" in floors_config:
            num_floors = 3
        
        # Base Allocation
        rooms_by_floor = {
            0: [], # Ground
            1: [], # First
            2: []  # Second
        }
        
        # Room Lists
        # We need to reconstruct the full list of rooms from boolean/count flags
        all_rooms = []
        if user_input.rooms.parking: all_rooms.append("parking")
        if user_input.rooms.living_room: all_rooms.append("living_room")
        if user_input.rooms.dining_area: all_rooms.append("dining_area")
        if user_input.rooms.kitchen: all_rooms.append("kitchen")
        if user_input.rooms.pooja_room: all_rooms.append("pooja_room")
        
        # Bedrooms
        # Master Bedroom priorities
        all_rooms.append("master_bedroom") # Assuming at least 1? The schema has bedrooms count.
        # Actually schema has 'bedrooms: int'
        # Let's clean this up. We should use the same Logic as main.py used to generate 'room_zones' keys
        
        # Let's assume we return a dict of room_names -> floor_index
        # Usage in main.py: 
        #   allocations = allocator.allocate(user_input) 
        #   for room, floor in allocations.items(): ...
        
        pass 
        # Re-thinking strategy: The allocator should take the 'room_zones' keys (or equivalent list) 
        # and assign them floors. But 'room_zones' is created after looking at rules.
        # Better: Allocator returns specific room lists for each floor.
        
        ground_rooms = []
        first_rooms = []
        second_rooms = []
        
        # 1. Essential Ground
        if user_input.rooms.parking: ground_rooms.append("parking")
        if user_input.rooms.living_room: ground_rooms.append("living_room")
        if user_input.rooms.kitchen: ground_rooms.append("kitchen")
        if user_input.rooms.dining_area: ground_rooms.append("dining_area")
        if user_input.rooms.pooja_room: ground_rooms.append("pooja_room")
        
        # 2. Bedrooms & Bathrooms allocation
        total_beds = user_input.rooms.bedrooms
        total_baths = user_input.rooms.bathrooms
        
        if num_floors == 1:
            ground_rooms.append("master_bedroom")
            if total_beds > 1:
                for i in range(1, total_beds):
                    ground_rooms.append(f"bedroom_{i+1}")
            
            # Bathrooms
            ground_rooms.append("bathroom") # Master bath
            if total_baths > 1:
                for i in range(1, total_baths):
                    ground_rooms.append(f"bathroom_{i+1}")
                    
        elif num_floors >= 2:
            # G+1 Strategy:
            # Ground: Guest Bed (if many), Common areas
            # First: Master Bed, Kids Bed
            
            # Staircase is needed on ALL floors
            ground_rooms.append("staircase")
            first_rooms.append("staircase")
            
            if total_beds == 1:
                # 1 Bed -> First floor (Private) or Ground? 
                # Usually Master is Upper in Duplex. Let's put Master on First.
                first_rooms.append("master_bedroom")
            else:
                # 2+ Beds
                # Put one on Ground (Guest/Parents) if count > 2?
                # Or if just 2, maybe both up?
                # Let's say: Master -> First. Bed 2 -> First. Bed 3 -> Ground.
                first_rooms.append("master_bedroom")
                
                remaining = total_beds - 1
                current_bed_idx = 2
                
                # Fill First Floor first
                if remaining > 0:
                    first_rooms.append(f"bedroom_{current_bed_idx}")
                    remaining -= 1
                    current_bed_idx += 1
                
                # Spill to Ground if more
                while remaining > 0:
                    ground_rooms.append(f"bedroom_{current_bed_idx}")
                    remaining -= 1
                    current_bed_idx += 1
            
            # Bathrooms Logic (Attached/Common)
            # Simple heuristic: Distribtue baths alongside bedrooms
            # But we don't have explicit tagging yet. 
            # Let's count bedrooms on each floor and allocate baths proportionally.
            
            g_beds = len([r for r in ground_rooms if "bedroom" in r])
            f_beds = len([r for r in first_rooms if "bedroom" in r])
            
            # Allocate baths
            # Master Bath (Main) -> With Master Bed (First Floor)
            if total_baths > 0:
                # Find where Master Bed is
                # It is in first_rooms
                first_rooms.append("bathroom") # Master bath
                remaining_baths = total_baths - 1
                
                # Assign remaining baths
                # If Ground has beds, give it a bath
                if remaining_baths > 0 and g_beds > 0:
                     ground_rooms.append("bathroom_2")
                     remaining_baths -= 1
                
                # If First has more beds and we have baths left
                if remaining_baths > 0 and f_beds > 1: # Already gave 1 to Master
                     first_rooms.append("bathroom_3")
                     remaining_baths -= 1
                     
                # Spill rest
                while remaining_baths > 0:
                     first_rooms.append(f"bathroom_{4 + (total_baths - remaining_baths)}") # Random ID
                     remaining_baths -= 1
            
            
        # Compile
        floors = {
            0: ground_rooms,
            1: first_rooms
        }
        if num_floors > 2:
            floors[2] = ["bedroom_extra", "bathroom_extra", "staircase"] # Placeholder logic
            
        return floors
