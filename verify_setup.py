import sys
import os

print("Verifying setup...")

try:
    import torch
    print(f"Torch version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"Failed to import torch: {e}")

try:
    from diffusers import StableDiffusionControlNetPipeline
    print("Diffusers imported successfully.")
except ImportError as e:
    print(f"Failed to import diffusers: {e}")

try:
    from app.visualizer import Visualizer
    v = Visualizer()
    from app.schemas import PlotDetails
    plot = PlotDetails(length=40, width=30, unit="ft", shape="rectangle", facing="North")
    
    # Test new Variant Generator
    from app.optimizer import LayoutOptimizer
    opt = LayoutOptimizer()
    variants = opt.generate_variants({"kitchen": ["SE", "NW"], "bedroom": ["SW", "W"]}, count=2)
    print(f"Generated {len(variants)} variants.")
    
    # Test Visualizer Stitching
    layouts = [v[0] for v in variants]
    
    # Test Floor Allocator
    from app.floor_allocator import FloorAllocator
    alloc = FloorAllocator()
    from app.schemas import UserInput, PlotDetails, BuildingConfig, RoomRequirements, DesignPreferences
    
    # Mock Input
    u_in = UserInput(
        plot=plot, 
        building=BuildingConfig(floors="G+1", building_type="house"),
        rooms=RoomRequirements(bedrooms=3, bathrooms=3, kitchen=True, living_room=True, dining_area=True, pooja_room=True, parking=True),
        vastu_level="strict",
        design=DesignPreferences(style="", layout_type="", natural_lighting="", visualization="")
    )
    
    floors = alloc.allocate(u_in)
    print("Floors Allocated:", floors.keys())
    print("Ground:", floors[0])
    print("First:", floors[1])
    
    print("Verification passed.")
except Exception as e:
    print(f"Visualizer failed: {e}")

print("Setup verification complete.")
