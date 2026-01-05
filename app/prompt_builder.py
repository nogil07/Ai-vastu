class PromptBuilder:

    def build(self, data, layout, notes):
        prompt = f"""
Generate a Vastu-compliant 2D floor plan.

Plot Details:
- {data.plot.shape} plot of {data.plot.length} x {data.plot.width} {data.plot.unit}
- Plot facing {data.plot.facing}, north arrow clearly marked

Building Configuration:
- {data.building.building_type}
- {data.building.floors} floors
- Architectural style: {data.design.style}
- Layout type: {data.design.layout_type}

Room Placement:
"""

        for room, zone in layout.items():
            prompt += f"- {room.replace('_',' ').title()} in {zone} zone\n"

        prompt += """
Vastu Constraints:
- Keep Brahmasthan open
- Avoid toilets in NE and SW
- Follow strict directional alignment

Drawing Instructions:
- Clean 2D architectural line drawing
- Room labels and dimensions
- Black lines on white background
"""

        return prompt.strip(), notes
