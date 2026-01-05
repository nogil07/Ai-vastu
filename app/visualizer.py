from PIL import Image, ImageDraw, ImageFont

class Visualizer:
    def __init__(self, size=2048):
        self.size = size
        self.margin = 160 # Increase margin proportionally
        self.drawing_area = size - (2 * self.margin)
        self.grid_size = self.drawing_area // 3
        
        self.bg_color = (10, 20, 60)
        self.line_color = (255, 255, 255)
        self.wall_color = (255, 255, 255)
        self.text_color = (255, 255, 255)
        self.accent_color = (255, 215, 0)

        self.zone_map = {
            "NW": (0, 0), "N": (0, 1), "NE": (0, 2),
            "W": (1, 0), "Center": (1, 1), "E": (1, 2),
            "SW": (2, 0), "S": (2, 1), "SE": (2, 2)
        }
        
        # Room Size Weights (Relative Importance)
        self.SIZE_WEIGHTS = {
            "master_bedroom": 1.6,
            "living_room": 1.5,
            "kitchen": 1.0, 
            "dining_area": 1.0,
            "bedroom": 1.2,
            "bedroom_1": 1.2, "bedroom_2": 1.2, "bedroom_3": 1.2,
            "parking": 1.4,
            "staircase": 0.8,
            "pooja_room": 0.5,
            "bathroom": 0.5,
            "store_room": 0.5,
            "balcony": 0.6
        }

    def _draw_compass(self, draw, facing):
        cx, cy = self.size - 60, 60
        # ... (compass code same as before, omitted for brevity if unchanged, but ensuring it maps correctly)
        radius = 40
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=self.accent_color, width=2)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
            
        draw.text((cx - 5, cy - radius - 25), "N", fill=self.accent_color, font=font)
        draw.polygon([(cx, cy - radius + 10), (cx - 10, cy), (cx + 10, cy)], fill=self.accent_color)
        if facing:
            draw.text((cx - 20, cy + radius + 30), f"Facing: {facing.title()}", fill=self.line_color, font=font)

    def _draw_door_arc(self, draw, x, y, alignment, size=50, is_main=False):
        # ... (same as before)
        color = self.accent_color if is_main else self.line_color
        width = 4 if is_main else 1
        bbox = [x - size, y - size, x + size, y + size]
        
        if alignment == 'bottom': 
            draw.line([(x-size/2, y), (x-size/2, y+size)], fill=color, width=width+1)
            draw.arc([x-size - size/2, y-size, x+size - size/2, y+size], 0, 90, fill=color, width=width)
        elif alignment == 'top':
            draw.line([(x-size/2, y), (x-size/2, y-size)], fill=color, width=width+1)
            draw.arc([x-size - size/2, y-size, x+size - size/2, y+size], 270, 360, fill=color, width=width)
        elif alignment == 'left': 
            draw.line([(x, y-size/2), (x-size, y-size/2)], fill=color, width=width+1)
            draw.arc([x-size, y-size - size/2, x+size, y+size - size/2], 180, 270, fill=color, width=width)
        elif alignment == 'right': 
            draw.line([(x, y-size/2), (x+size, y-size/2)], fill=color, width=width+1)
            draw.arc([x-size, y-size - size/2, x+size, y+size - size/2], 0, 90, fill=color, width=width)

    def _get_weight(self, room_name):
        # Strip numbering (e.g. bedroom_1 -> bedroom)
        base = room_name.split("_")[0] if "_" in room_name and not room_name.startswith("master") and not room_name.startswith("living") and not room_name.startswith("dining") and not room_name.startswith("pooja") else room_name
        # Careful with logic, simplify:
        for key in self.SIZE_WEIGHTS:
            if key in room_name:
                return self.SIZE_WEIGHTS[key]
        return 1.0 # Default

    def _subdivide_cell(self, rooms, x, y, size):
        rects = []
        count = len(rooms)
        
        weights = [self._get_weight(r) for r in rooms]
        total_weight = sum(weights)
        
        if count == 1:
            # Check weight - if it's a small room (e.g. Bathroom, Pooja), don't fill the whole grid.
            w = weights[0]
            if w < 0.8: # Small room threshold
                # Split into Room + Void/Passage
                # Give it 40-50% of the space
                room_w = int(size * 0.45)
                # Split vertically or horizontally? 
                # Let's say vertically for now.
                rects.append((rooms[0], x, y, room_w, size))
                # We won't add a rect for the rest, so it stays background color (Passage)
            else:
                rects.append((rooms[0], x, y, size, size))
            
        elif count == 2:
            # Split proportionally based on weight
            w1, w2 = weights
            ratio = w1 / (w1 + w2)
            
            # Cap ratio to avoid tiny rooms (max 75%)
            ratio = max(0.25, min(0.75, ratio))
            
            # Split Vertically if Width > Height logic? Here it's a square cell.
            # Let's split Vertically (Side by Side) usually looks better, 
            # UNLESS weights are very skewed, maybe Horizontally better?
            # Let's stick to Vertical split for 2 rooms.
            
            w_split = int(size * ratio)
            
            rects.append((rooms[0], x, y, w_split, size))
            rects.append((rooms[1], x + w_split, y, size - w_split, size))
            
        elif count == 3:
            # Find the Hero (Largest room)
            max_w = max(weights)
            hero_idx = weights.index(max_w)
            
            # Give Hero the Left Half (50%)
            hero_w = size // 2
            
            rects.append((rooms[hero_idx], x, y, hero_w, size))
            
            # Split the other two in the Right Half
            others = [(i, w) for i, w in enumerate(weights) if i != hero_idx]
            o1_idx, o1_w = others[0]
            o2_idx, o2_w = others[1]
            
            ratio_o = o1_w / (o1_w + o2_w)
            ratio_o = max(0.25, min(0.75, ratio_o))
            
            h_split = int(size * ratio_o)
            
            # Split Right Half Horizontally (Top/Bottom)
            rects.append((rooms[o1_idx], x + hero_w, y, size - hero_w, h_split))
            rects.append((rooms[o2_idx], x + hero_w, y + h_split, size - hero_w, size - h_split))
            
        elif count >= 4:
            # 2x2 Grid (Simplified equal for now, 4 rooms in one zone is rare/crowded)
            w = size // 2
            h = size // 2
            rects.append((rooms[0], x, y, w, h))
            rects.append((rooms[1], x + w, y, w, h))
            rects.append((rooms[2], x, y + h, w, h))
            rects.append((rooms[3], x + w, y + h, w, h))
            
        return rects

    def create_layout_image(self, layout, plot_details=None):
        img = Image.new("RGB", (self.size, self.size), self.bg_color)
        draw = ImageDraw.Draw(img)

        # Draw Outer Boundary
        draw.rectangle(
            [self.margin, self.margin, self.size - self.margin, self.size - self.margin], 
            outline=self.line_color, 
            width=3
        )

        facing = plot_details.facing.lower() if plot_details else "north"
        self._draw_compass(draw, facing)
        
        # Draw Plot Dimensions
        if plot_details:
            dim_text = f"Plot: {plot_details.length} {plot_details.unit} x {plot_details.width} {plot_details.unit}"
            try:
                f_dim = ImageFont.truetype("arial.ttf", 24)
            except:
                f_dim = ImageFont.load_default()
            
            # Draw at bottom center or corner
            # Using bottom left margin
            draw.text((self.margin, self.size - self.margin + 20), dim_text, fill=self.text_color, font=f_dim)

        # 1. Group Rooms by Zone to handle subdivision
        zone_allocations = {k: [] for k in self.zone_map}
        for room, zone in layout.items():
            if zone in zone_allocations:
                zone_allocations[zone].append(room)

        # Calculate Scale
        total_width_ft = plot_details.width if plot_details else 30
        total_length_ft = plot_details.length if plot_details else 40
        unit = plot_details.unit if plot_details else "ft" # Assuming pixels map to plot dim

        # Pixels per scale unit
        # Map drawing_area to total_width
        # Note: Usually Width is X, Length is Y.
        
        labels = []
        wall_thick = 6

        for zone, rooms in zone_allocations.items():
            if not rooms:
                continue
                
            row, col = self.zone_map[zone]
            
            # Base Grid Cell Coordinates
            cell_x = self.margin + (col * self.grid_size)
            cell_y = self.margin + (row * self.grid_size)
            
            # Subdivide this cell for the rooms
            sub_rects = self._subdivide_cell(rooms, cell_x, cell_y, self.grid_size)
            
            for room_name, rx, ry, rw, rh in sub_rects:
                # Draw Room
                draw.rectangle([rx, ry, rx+rw, ry+rh], outline=self.wall_color, width=wall_thick)
                
                # Door Logic (Practical)
                # Ensure connection to Center or Common area
                cx = rx + rw/2
                cy = ry + rh/2
                
                # Determine Door Wall by finding "Center-est" wall
                # Map center is (size/2, size/2)
                map_cx = self.size / 2
                map_cy = self.size / 2
                
                # Vectors to center
                dx = map_cx - cx
                dy = map_cy - cy
                
                door_size = 40
                
                # Pick the wall facing the center of the house
                door_wall = None
                
                # Simple logic: If abs(dx) > abs(dy), vertical walls are closer to center? 
                # Actually, we want the wall *facing* the center.
                # If room is Left of center (dx > 0), Door is on Right wall.
                # If room is Above center (dy > 0), Door is on Bottom wall.
                
                # Also consider Main Entrance if this is a Living Room or Parking
                is_main_entry = False
                if "parking" in room_name.lower() or "living" in room_name.lower():
                     # Main door usually faces the Plot Facing direction
                     if facing == "north" and row == 0: is_main_entry = True # Top wall
                     elif facing == "south" and row == 2: is_main_entry = True
                     elif facing == "east" and col == 2: is_main_entry = True
                     elif facing == "west" and col == 0: is_main_entry = True

                if is_main_entry:
                    # Draw Main Door on external wall
                    # Force it to be clearly visible
                    if facing == "north": self._draw_door_arc(draw, cx, ry+5, 'top', 60, True) # +5 adjustment
                    elif facing == "south": self._draw_door_arc(draw, cx, ry+rh-5, 'bottom', 60, True)
                    elif facing == "east": self._draw_door_arc(draw, rx+rw-5, cy, 'right', 60, True)
                    elif facing == "west": self._draw_door_arc(draw, rx+5, cy, 'left', 60, True)
                else:
                    # Internal Door (Standard logic)
                    if room_name.lower() != "center": # Center has no doors
                        if abs(dx) > abs(dy):
                            # Dominantly horizontal offset
                            if dx > 0: # Center is to Right -> Door on Right Wall
                                # Check if it's the external boundary? (avoid unless balcony)
                                self._draw_door_arc(draw, rx+rw, cy, 'right', door_size)
                            else: # Center is to Left -> Door on Left Wall
                                self._draw_door_arc(draw, rx, cy, 'left', door_size)
                        else:
                            # Dominantly vertical offset
                            if dy > 0: # Center is Below -> Door on Bottom Wall
                                self._draw_door_arc(draw, cx, ry+rh, 'bottom', door_size)
                            else: # Center is Above -> Door on Top Wall
                                self._draw_door_arc(draw, cx, ry, 'top', door_size)

                # Calculate Dimensions
                # width fraction = rw / drawing_area
                room_w_real = (rw / self.drawing_area) * total_width_ft
                room_l_real = (rh / self.drawing_area) * total_length_ft

                labels.append({
                    "text": room_name.replace("_", " ").upper(),
                    "x": cx,
                    "y": cy,
                    "subtext": f"{room_w_real:.1f}{unit} x {room_l_real:.1f}{unit}"
                })

        return img, labels

    def create_composite_image(self, variants_list, plot_details=None, single_option_mode=False):
        """
        variants_list: List of Options. 
        Each Option is a Dictionary of Floors: {0: layout_g, 1: layout_f}
        """
        # 1. Generate individual images for each floor of each option
        # Structure: We want 3 Columns (Options). Each Column has N Rows (Floors).
        
        option_images = [] # List of (Option_Image)
        
        for i, floors_dict in enumerate(variants_list):
            # floors_dict is {0: layout, 1: layout}
            floor_imgs = []
            sorted_floors = sorted(floors_dict.keys())
            
            for f_idx in sorted_floors:
                layout = floors_dict[f_idx]
                img, _ = self.create_layout_image(layout, plot_details)
                img = self.overlay_labels(img, _)
                
                # Add Floor Label
                d = ImageDraw.Draw(img)
                floor_name = "GROUND FLOOR" if f_idx == 0 else f"FIRST FLOOR" if f_idx == 1 else f"FLOOR {f_idx}"
                d.text((self.size - 250, 20), floor_name, fill=self.text_color, font=ImageFont.load_default())
                
                floor_imgs.append(img)
            
            # Switch Vertical Stitching for the Option (Ground Top, First Bottom)
            # Or Horizontal? usually Ground | First is better for comparison if screen is wide.
            # But we have 3 Options. Warning: 3 Options x 2 Floors side-by-side = 6 images wide. Too wide.
            # Let's Stack Floors Vertically for each Option.
            # Option 1:
            #  [ Ground ]
            #  [ First  ]
            
            opt_w = floor_imgs[0].width
            opt_h = sum(img.height for img in floor_imgs) + (len(floor_imgs)-1)*20
            
            opt_img = Image.new("RGB", (opt_w, opt_h), (0,0,0))
            y_off = 0
            for f_img in floor_imgs:
                opt_img.paste(f_img, (0, y_off))
                y_off += f_img.height + 20
            
            # Add Option Label to the top of this tall strip
            d = ImageDraw.Draw(opt_img)
            try:
                f = ImageFont.truetype("arial.ttf", 60)
            except:
                f = ImageFont.load_default()
            d.text((40, 40), f"OPTION {i+1}", fill=self.accent_color, font=f)
            
            option_images.append(opt_img)
             
        # 2. Stitch Options Side-by-Side
        total_width = sum(i.width for i in option_images) + (len(option_images)-1)*50
        max_height = max(i.height for i in option_images)
        
        composite = Image.new("RGB", (total_width, max_height), (20, 20, 20))
        
        current_x = 0
        for img in option_images:
            composite.paste(img, (current_x, 0))
            current_x += img.width + 50
            
        return composite

    def overlay_labels(self, image, labels):
        draw = ImageDraw.Draw(image)
        try:
            font_title = ImageFont.truetype("arial.ttf", 18)
            font_sub = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()

        for label in labels:
            text = label["text"]
            x, y = label["x"], label["y"]
            
            bbox = draw.textbbox((0, 0), text, font=font_title)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text((x - w/2, y - h - 2), text, fill=self.text_color, font=font_title)
            
            sub = label.get("subtext", "")
            if sub:
                bbox_s = draw.textbbox((0, 0), sub, font=font_sub)
                ws = bbox_s[2] - bbox_s[0]
                draw.text((x - ws/2, y + 5), sub, fill=(200, 200, 200), font=font_sub)
            
        return image
