from fastapi import FastAPI
from app.schemas import UserInput, PromptOutput
from app.rule_engine import VastuRuleEngine
from app.optimizer import LayoutOptimizer
from app.prompt_builder import PromptBuilder
from app.vastu_scoring import VastuScorer
from app.visualizer import Visualizer
# from app.image_generator import ImageGenerator  <-- Removed
from app.floor_allocator import FloorAllocator
from app.report_generator import PDFReportGenerator
from app.text_generator import TextGenerator
import base64
from io import BytesIO
from PIL import ImageDraw, ImageFont

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import UserInput, PromptOutput
from app.rule_engine import VastuRuleEngine
from app.optimizer import LayoutOptimizer

app = FastAPI(title="AI Vastu Prompt Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specifiy frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rule_engine = VastuRuleEngine()
optimizer = LayoutOptimizer()
builder = PromptBuilder()
scorer = VastuScorer()
visualizer = Visualizer()
allocator = FloorAllocator()
report_gen = PDFReportGenerator()
text_gen = TextGenerator()

@app.post("/generate-prompt", response_model=PromptOutput)
def generate_prompt(user_input: UserInput):

    room_zones = {}

    if user_input.rooms.kitchen:
        room_zones["kitchen"] = rule_engine.get_zone_for_room("kitchen", user_input.vastu_level)

    if user_input.rooms.pooja_room:
        room_zones["pooja_room"] = rule_engine.get_zone_for_room("pooja_room", user_input.vastu_level)

    room_zones["master_bedroom"] = rule_engine.get_zone_for_room("master_bedroom", user_input.vastu_level)
    room_zones["bathroom"] = rule_engine.get_zone_for_room("bathroom", user_input.vastu_level)

    if user_input.rooms.living_room:
        room_zones["living_room"] = rule_engine.get_zone_for_room("living_room", user_input.vastu_level)
    
    if user_input.rooms.dining_area:
        room_zones["dining_area"] = rule_engine.get_zone_for_room("dining_area", user_input.vastu_level)

    if user_input.rooms.parking:
        room_zones["parking"] = rule_engine.get_zone_for_room("parking", user_input.vastu_level)

    # Handle extra bedrooms
    if user_input.rooms.bedrooms > 1:
        for i in range(1, user_input.rooms.bedrooms):
            room_zones[f"bedroom_{i+1}"] = rule_engine.get_zone_for_room("bedroom", user_input.vastu_level)

    layout, notes = optimizer.optimize(room_zones)
    prompt, notes = builder.build(user_input, layout, notes)

    score, breakdown = scorer.calculate_score(
        layout, rule_engine.get_all_rules()
    )

    return {
        "optimized_prompt": prompt,
        "vastu_score": score,
        "vastu_breakdown": breakdown,
        "vastu_notes": notes
    }

# Initialize Image Generator (Disabled for Procedural Mode)
# try:
#     generator = ImageGenerator()
#     print("Image Generator loaded successfully.")
# except Exception as e:
#     print(f"Failed to load Image Generator: {e}")
#     generator = None

def get_base_rule_name(r):
    base_name = r.split("_")[0] if "bedroom" in r or "bathroom" in r else r
    if "master" in r: base_name = "master_bedroom"
    rule_name = base_name
    if "staircase" in r: rule_name = "staircase"
    return base_name, rule_name

@app.post("/generate-design")
def generate_design(user_input: UserInput):
    # 1. Allocate Rooms to Floors
    floors_alloc = allocator.allocate(user_input)
    
    # 2. Generate Options (Variants)
    # We want 3 distinct options with potentially different scores/layouts.
    # Method: Run optimizer 3 times with different constraints.

    # Store options structure: [ {floor: layout}, {floor: layout}, {floor: layout} ]
    final_options = [{}, {}, {}] 

    for f_idx, room_names in floors_alloc.items():
        # Option 1: Strict / User Level
        rz_opt1 = {}
        for r in room_names:
            base, rule_name = get_base_rule_name(r)
            rz_opt1[r] = rule_engine.get_zone_for_room(rule_name, user_input.vastu_level)
        
        vars_1 = optimizer.generate_variants(rz_opt1, count=1)
        final_options[0][f_idx] = vars_1[0][0]
        
        # Option 2: Balanced (Try alternatives if available)
        rz_opt2 = {}
        for r in room_names:
            base, rule_name = get_base_rule_name(r)
            # Use Medium to get more options
            zones = rule_engine.get_zone_for_room(rule_name, "medium")
            # For variety, if we have >1 zone, rotate the list
            if len(zones) > 1:
                 zones = zones[1:] + zones[:1] # Shift preference
            rz_opt2[r] = zones
            
        vars_2 = optimizer.generate_variants(rz_opt2, count=1)
        final_options[1][f_idx] = vars_2[0][0]

        # Option 3: Experimental / Relaxed
        rz_opt3 = {}
        import random
        for r in room_names:
            base, rule_name = get_base_rule_name(r)
            zones = rule_engine.get_zone_for_room(rule_name, "medium")
            if len(zones) > 1:
                random.shuffle(zones)
            rz_opt3[r] = zones
            
        vars_3 = optimizer.generate_variants(rz_opt3, count=1)
        final_options[2][f_idx] = vars_3[0][0]

    # 4. Process Outputs (Image + Report)
    images_base64 = []
    reports_base64 = []
    
    for i, opt_layouts in enumerate(final_options):
        # A. Image
        img = visualizer.create_composite_image([opt_layouts], plot_details=user_input.plot, single_option_mode=True)
        
        buffered_img = BytesIO()
        img.save(buffered_img, format="PNG")
        img_str = base64.b64encode(buffered_img.getvalue()).decode("utf-8")
        images_base64.append(img_str)
        
        # B. Report
        # Aggregate full layout for scoring
        full_layout = {}
        for f, layout in opt_layouts.items():
            full_layout.update(layout)
            
        # Score
        score, breakdown = scorer.calculate_score(full_layout, rule_engine.get_all_rules())
        
        # Determine notes
        notes = [f"Option {i+1} optimized for compliance."]
        
        # AI Text Generation
        context = {
            "style": user_input.design.style,
            "plot_size": f"{user_input.plot.length * user_input.plot.width}",
            "facing": user_input.plot.facing,
            "floors": user_input.building.floors,
            "bedrooms": user_input.rooms.bedrooms
        }
        ai_summary = text_gen.generate_report_text(context)
        
        # Generate PDF
        pdf_buffer = report_gen.generate_report(i+1, buffered_img, score, breakdown, notes, user_input.plot, ai_summary=ai_summary)
        pdf_str = base64.b64encode(pdf_buffer.getvalue()).decode("utf-8")
        reports_base64.append(pdf_str)

    return {
        "images": images_base64,
        "reports": reports_base64,
        "image_base64": images_base64[0],
        "prompt": "Generated 3 Options with Professional AI Reports."
    }
