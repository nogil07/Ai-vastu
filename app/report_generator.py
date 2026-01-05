from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from io import BytesIO
from reportlab.lib.units import inch

class PDFReportGenerator:
    def __init__(self):
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self.create_custom_styles()

    def create_custom_styles(self):
        self.styles.add(ParagraphStyle(name='VastuTitle', parent=self.styles['Heading1'], fontSize=24, spaceAfter=20, textColor=colors.darkblue))
        self.styles.add(ParagraphStyle(name='VastuScore', parent=self.styles['Heading2'], fontSize=18, spaceAfter=20, textColor=colors.darkgreen))
        self.styles.add(ParagraphStyle(name='Reasoning', parent=self.styles['BodyText'], fontSize=10, leading=12))

    def generate_report(self, variant_num, image_buffer, score, breakdown, notes, plot_details, ai_summary=""):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        
        elements = []
        
        # 1. Header (Logo/Title)
        elements.append(Paragraph(f"ARCHITECTURAL DESIGN REPORT", self.styles['VastuTitle']))
        elements.append(Paragraph(f"OPTION {variant_num} - {plot_details.facing.upper()} FACING RESIDENCE", self.styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        # 2. Project Details Table
        data = [
            ["Plot Dimensions", f"{plot_details.length} x {plot_details.width} {plot_details.unit}"],
            ["Orientation", plot_details.facing.title()],
            ["Vastu Score", f"{score:.1f}/100"],
            ["Compliance Level", "Excellent" if score > 80 else "Good" if score > 60 else "Average"]
        ]
        t_meta = Table(data, colWidths=[2*inch, 3*inch], hAlign='LEFT')
        t_meta.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t_meta)
        elements.append(Spacer(1, 20))

        # 3. AI Executive Summary
        if ai_summary:
            elements.append(Paragraph("Executive Summary", self.styles['Heading2']))
            elements.append(Paragraph(ai_summary, self.styles['Reasoning']))
            elements.append(Spacer(1, 15))

        # 4. Methodology & Scoring Logic (NEW)
        elements.append(Paragraph("Scoring Methodology", self.styles['Heading2']))
        method_text = (
            "The Vastu Compliance Score is a weighted aggregate reflecting how well the spatial organization aligns with ancient Vedic architectural principles. "
            "Key functional areas (Kitchen, Master Bedroom, Pooja Room) carry higher weightage (15-20%) compared to others. "
            "A score of 100% indicates optimal placement for all rooms according to the chosen Vastu strictness level."
        )
        elements.append(Paragraph(method_text, self.styles['Reasoning']))
        elements.append(Spacer(1, 15))

        # 5. Floor Plan Visual
        elements.append(Paragraph("Proposed Floor Layout", self.styles['Heading2']))
        
        image_buffer.seek(0)
        from PIL import Image as PILImage
        try:
             with PILImage.open(image_buffer) as pil_img:
                 orig_w, orig_h = pil_img.size
                 aspect = orig_h / orig_w
        except:
             orig_w, orig_h = 600, 400
             aspect = 0.75
        image_buffer.seek(0)
        
        available_width = self.width - 60 # Reduced margins (30 each side effectively) for just image? No, global margin is 40.
        # Let's align with global margin: 595 - 80 = 515 pts.
        
        # Increase available height to allow larger images
        available_height = 600 
        
        display_width = available_width
        display_height = display_width * aspect
        
        if display_height > available_height:
             display_height = available_height
             display_width = display_height / aspect

        rl_img = RLImage(image_buffer, width=display_width, height=display_height)
        rl_img.hAlign = 'CENTER'
        elements.append(rl_img)
        elements.append(Spacer(1, 25))
        
        # 6. Detailed Vastu Analysis
        elements.append(Paragraph("Detailed Vastu Analysis & Benefits", self.styles['Heading2']))
        
        # Create a more detailed table
        # Columns: Room | Zone | Status | Benefit/Reasoning
        # Headers should be Paragraphs too for consistency or strings
        headers = ["Room", "Zone", "Status", "Vastu Benefit & Reasoning"]
        
        table_data = [headers]
        
        # Define styles for columns
        style_cell_normal = self.styles['BodyText']
        style_cell_normal.fontSize = 9
        style_cell_normal.leading = 11
        style_cell_bold = ParagraphStyle('BoldCell', parent=style_cell_normal, fontName='Helvetica-Bold')

        for room, info in breakdown.items():
            r_name = room.replace("_", " ").title()
            z_zone = info.get("zone", "N/A")
            s_val = info.get("score", 0)
            status = "Optimal" if self.request_status_check(s_val, info.get("max",5)) else "Needs Attn"
            
            # Combine reasoning and benefit
            reason = info.get("reason", "")
            benefit = info.get("benefit", "")
            full_text = f"<b>Reasoning:</b> {reason}<br/><b>Benefit:</b> {benefit}"
            
            # Use Paragraphs to ensure wrapping
            p_room = Paragraph(r_name, style_cell_bold)
            p_zone = Paragraph(z_zone, style_cell_normal)
            p_status = Paragraph(status, style_cell_normal)
            p_desc = Paragraph(full_text, style_cell_normal)
            
            table_data.append([p_room, p_zone, p_status, p_desc])
            
        # Adjusted widths to fit A4 (approx 7 inches max safely)
        # Total available width approx 7.1 inches.
        # 1.1 + 0.6 + 0.9 + 4.5 = 7.1 inches
        col_widths = [1.1*inch, 0.6*inch, 0.9*inch, 4.5*inch]
        t_analysis = Table(table_data, colWidths=col_widths)
        t_analysis.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (2, -1), 'CENTER'),
            ('ALIGN', (3, 0), (3, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'), # Top align is better for wrapped text
            ('WORDWRAP', (0, 0), (-1, -1), True),
        ]))
        
        elements.append(t_analysis)
        elements.append(Spacer(1, 20))
        
        # 7. Conclusion / Notes
        if notes:
            elements.append(Paragraph("Design Notes", self.styles['Heading2']))
            for note in notes:
                 elements.append(Paragraph(f"• {note}", self.styles['Reasoning']))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def request_status_check(self, score, max_score):
        if max_score == 0: return False
        return (score / max_score) > 0.7
