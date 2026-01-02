from fpdf import FPDF
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import os
import uuid
from datetime import datetime


# ============================================================================
# COLOR PALETTE - Professional Blue Theme
# ============================================================================
COLORS = {
    'primary': (37, 99, 235),      # Blue
    'secondary': (99, 102, 241),   # Indigo
    'accent': (16, 185, 129),      # Green
    'dark': (30, 41, 59),          # Slate dark
    'light': (241, 245, 249),      # Slate light
    'white': (255, 255, 255),
    'warning': (245, 158, 11),     # Amber
}


# ============================================================================
# PDF REPORT GENERATOR
# ============================================================================
class PDFReport(FPDF):
    """Professional PDF Report with styled headers, footers, and sections."""
    
    def __init__(self, title="Data Analysis Report"):
        super().__init__()
        self.title = title
        self.set_auto_page_break(auto=True, margin=20)
    
    def header(self):
        if self.page_no() == 1:
            return  # No header on title page
        self.set_fill_color(*COLORS['primary'])
        self.rect(0, 0, 210, 15, 'F')
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*COLORS['white'])
        self.set_y(5)
        self.cell(0, 5, self.title, 0, 1, 'C')
        self.set_text_color(*COLORS['dark'])
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.now().strftime("%Y-%m-%d")}', 0, 0, 'C')

    def add_title_page(self):
        """Create a professional title page."""
        self.add_page()
        # Background
        self.set_fill_color(*COLORS['primary'])
        self.rect(0, 0, 210, 297, 'F')
        
        # Title
        self.set_font('Arial', 'B', 36)
        self.set_text_color(*COLORS['white'])
        self.set_y(100)
        self.cell(0, 20, 'Data Analysis Report', 0, 1, 'C')
        
        # Subtitle
        self.set_font('Arial', '', 16)
        self.set_text_color(200, 220, 255)
        self.cell(0, 10, 'Comprehensive Data Insights & Recommendations', 0, 1, 'C')
        
        # Date
        self.set_y(250)
        self.set_font('Arial', 'I', 12)
        self.cell(0, 10, f'Generated: {datetime.now().strftime("%B %d, %Y")}', 0, 1, 'C')
        
    def add_section_header(self, title, number=None):
        """Add a styled section header."""
        self.ln(5)
        self.set_fill_color(*COLORS['primary'])
        header_text = f"{number}. {title}" if number else title
        self.set_font('Arial', 'B', 16)
        self.set_text_color(*COLORS['primary'])
        self.cell(0, 10, header_text, 0, 1, 'L')
        self.set_draw_color(*COLORS['primary'])
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
        self.set_text_color(*COLORS['dark'])
        self.set_font('Arial', '', 11)

    def add_subsection(self, title):
        """Add a subsection header."""
        self.ln(3)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(*COLORS['secondary'])
        self.cell(0, 8, title, 0, 1, 'L')
        self.set_text_color(*COLORS['dark'])
        self.set_font('Arial', '', 11)
        self.ln(2)

    def add_paragraph(self, text):
        """Add a paragraph of text."""
        safe_text = clean_text(text).encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, safe_text)
        self.ln(3)

    def add_bullet_point(self, text):
        """Add a bullet point."""
        safe_text = clean_text(text).encode('latin-1', 'replace').decode('latin-1')
        self.set_x(15)
        self.set_font('Arial', '', 11)
        self.cell(5, 6, chr(149), 0, 0)  # Bullet character
        self.multi_cell(0, 6, safe_text)

    def add_key_value(self, key, value):
        """Add a key-value pair."""
        self.set_font('Arial', 'B', 11)
        self.set_text_color(*COLORS['secondary'])
        self.cell(60, 7, f"{key}:", 0, 0)
        self.set_font('Arial', '', 11)
        self.set_text_color(*COLORS['dark'])
        safe_value = str(value).encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 7, safe_value, 0, 1)

    def add_image_with_caption(self, img_path, caption="", width=170):
        """Add an image with a caption."""
        if os.path.exists(img_path):
            try:
                # Check if we need a new page
                if self.get_y() > 200:
                    self.add_page()
                self.image(img_path, x=20, w=width)
                if caption:
                    self.ln(3)
                    self.set_font('Arial', 'I', 9)
                    self.set_text_color(100, 100, 100)
                    self.cell(0, 5, caption, 0, 1, 'C')
                    self.set_text_color(*COLORS['dark'])
                self.ln(5)
            except Exception as e:
                self.add_paragraph(f"[Image could not be loaded: {e}]")


def clean_text(text):
    """Remove markdown artifacts from text."""
    if not text:
        return ""
    text = str(text)
    text = text.replace('**', '').replace('*', '')
    text = text.replace('### ', '').replace('## ', '').replace('# ', '')
    text = text.replace('```python', '').replace('```', '')
    text = text.replace('\n\n\n', '\n\n')
    return text.strip()


def create_pdf_report(report_data, image_paths=None, output_filename=None):
    """
    Creates a comprehensive professional PDF report.
    
    Args:
        report_data: Either a string (simple text) or dict with structured sections:
            {
                'executive_summary': str,
                'data_overview': str,
                'key_statistics': str,
                'data_quality': str,
                'distribution_analysis': str,
                'trend_analysis': str,
                'correlation_insights': str,
                'key_findings': list[str],
                'recommendations': list[str],
                'image_descriptions': dict[str, str]  # {filename: description}
            }
        image_paths: List of image file paths
        output_filename: Output filename
        
    Returns:
        str: Path to the generated PDF.
    """
    if not output_filename:
        output_filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
    
    image_paths = image_paths or []
    
    pdf = PDFReport()
    
    # Handle simple string input (backward compatibility)
    if isinstance(report_data, str):
        report_data = {
            'executive_summary': report_data,
            'key_findings': [],
            'recommendations': []
        }
    
    # 1. Title Page
    pdf.add_title_page()
    
    # 2. Executive Summary
    pdf.add_page()
    pdf.add_section_header("Executive Summary", 1)
    pdf.add_paragraph(report_data.get('executive_summary', 'Analysis completed successfully.'))
    
    # 3. Data Overview
    pdf.add_section_header("Data Overview", 2)
    pdf.add_paragraph(report_data.get('data_overview', 'The dataset was analyzed for patterns and insights.'))
    
    # 4. Key Statistics
    pdf.add_section_header("Key Statistics", 3)
    pdf.add_paragraph(report_data.get('key_statistics', 'Statistical analysis was performed on the dataset.'))
    
    # 5. Data Quality Analysis
    pdf.add_page()
    pdf.add_section_header("Data Quality Analysis", 4)
    pdf.add_paragraph(report_data.get('data_quality', 'Data quality was assessed for completeness and accuracy.'))
    
    # 6. Distribution Analysis with images
    pdf.add_section_header("Distribution Analysis", 5)
    pdf.add_paragraph(report_data.get('distribution_analysis', 'The distribution of key variables was analyzed.'))
    
    # Add first half of images
    image_descriptions = report_data.get('image_descriptions', {})
    half = len(image_paths) // 2 + 1
    for img_path in image_paths[:half]:
        filename = os.path.basename(img_path)
        caption = image_descriptions.get(filename, f"Figure: {filename}")
        pdf.add_image_with_caption(img_path, caption)
    
    # 7. Trend Analysis
    pdf.add_page()
    pdf.add_section_header("Trend Analysis", 6)
    pdf.add_paragraph(report_data.get('trend_analysis', 'Trends and patterns were identified in the data.'))
    
    # 8. Correlation Insights with remaining images
    pdf.add_section_header("Correlation Insights", 7)
    pdf.add_paragraph(report_data.get('correlation_insights', 'Relationships between variables were examined.'))
    
    for img_path in image_paths[half:]:
        filename = os.path.basename(img_path)
        caption = image_descriptions.get(filename, f"Figure: {filename}")
        pdf.add_image_with_caption(img_path, caption)
    
    # 9. Key Findings
    pdf.add_page()
    pdf.add_section_header("Key Findings", 8)
    findings = report_data.get('key_findings', [])
    if isinstance(findings, list) and findings:
        for finding in findings:
            pdf.add_bullet_point(finding)
    else:
        pdf.add_paragraph("Key findings from the analysis have been documented above.")
    
    # 10. Recommendations
    pdf.add_section_header("Recommendations & Next Steps", 9)
    recommendations = report_data.get('recommendations', [])
    if isinstance(recommendations, list) and recommendations:
        for rec in recommendations:
            pdf.add_bullet_point(rec)
    else:
        pdf.add_paragraph("Based on the analysis, further investigation of identified patterns is recommended.")
    
    # Create output directory for PDFs
    output_dir = os.path.join(os.getcwd(), "outputs", "pdfs")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save
    output_path = os.path.join(output_dir, output_filename)
    pdf.output(output_path)
    return output_path


# ============================================================================
# POWERPOINT REPORT GENERATOR
# ============================================================================

def add_title_slide(prs, title, subtitle):
    """Add a professional title slide."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    
    # Full background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(*COLORS['primary'])
    bg.line.fill.background()
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12.3), Inches(1.5))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = RGBColor(*COLORS['white'])
    p.alignment = PP_ALIGN.CENTER
    
    # Subtitle
    sub_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(12.3), Inches(0.8))
    tf = sub_box.text_frame
    p = tf.paragraphs[0]
    p.text = subtitle
    p.font.size = Pt(22)
    p.font.color.rgb = RGBColor(200, 220, 255)
    p.alignment = PP_ALIGN.CENTER
    
    # Date
    date_box = slide.shapes.add_textbox(Inches(0.5), Inches(6.5), Inches(12.3), Inches(0.5))
    tf = date_box.text_frame
    p = tf.paragraphs[0]
    p.text = datetime.now().strftime("%B %d, %Y")
    p.font.size = Pt(16)
    p.font.color.rgb = RGBColor(180, 200, 255)
    p.alignment = PP_ALIGN.CENTER


def add_content_slide(prs, title, content, bullet_points=None):
    """Add a content slide with header and text."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    
    # Header bar
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = RGBColor(*COLORS['primary'])
    header.line.fill.background()
    
    # Header text
    header_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(12), Inches(0.6))
    tf = header_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = RGBColor(*COLORS['white'])
    
    # Content
    if content:
        content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(12.3), Inches(5.5))
        tf = content_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        cleaned = clean_text(content)
        if len(cleaned) > 800:
            cleaned = cleaned[:800] + "..."
        p.text = cleaned
        p.font.size = Pt(16)
        p.font.color.rgb = RGBColor(*COLORS['dark'])
    
    # Bullet points
    if bullet_points:
        y_pos = Inches(1.5) if not content else Inches(4.5)
        for i, point in enumerate(bullet_points[:6]):  # Max 6 points
            bp_box = slide.shapes.add_textbox(Inches(0.7), y_pos + Inches(i * 0.6), Inches(11.5), Inches(0.5))
            tf = bp_box.text_frame
            p = tf.paragraphs[0]
            p.text = f"• {clean_text(point)}"
            p.font.size = Pt(14)
            p.font.color.rgb = RGBColor(*COLORS['dark'])
    
    return slide


def add_image_slide(prs, title, img_path, description=""):
    """Add a slide with an image and description."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    
    # Header bar
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.0))
    header.fill.solid()
    header.fill.fore_color.rgb = RGBColor(*COLORS['primary'])
    header.line.fill.background()
    
    # Header text
    header_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.25), Inches(12), Inches(0.5))
    tf = header_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = RGBColor(*COLORS['white'])
    
    # Add image
    if os.path.exists(img_path):
        try:
            slide.shapes.add_picture(img_path, Inches(1), Inches(1.2), width=Inches(8))
        except Exception as e:
            print(f"Error adding image: {e}")
    
    # Description
    if description:
        desc_box = slide.shapes.add_textbox(Inches(9.2), Inches(1.5), Inches(3.8), Inches(5))
        tf = desc_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = clean_text(description)[:400]
        p.font.size = Pt(12)
        p.font.color.rgb = RGBColor(*COLORS['dark'])
    
    return slide


def add_closing_slide(prs):
    """Add a thank you / closing slide."""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    
    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(*COLORS['secondary'])
    bg.line.fill.background()
    
    # Text
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(3), Inches(12.3), Inches(1.5))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Thank You"
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = RGBColor(*COLORS['white'])
    p.alignment = PP_ALIGN.CENTER
    
    # Subtitle
    sub_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(12.3), Inches(0.8))
    tf = sub_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Questions & Discussion"
    p.font.size = Pt(24)
    p.font.color.rgb = RGBColor(220, 220, 255)
    p.alignment = PP_ALIGN.CENTER


def create_ppt_report(report_data, image_paths=None, output_filename=None, title=None):
    """
    Creates a PowerPoint presentation with DYNAMIC pages based on user content.
    Uses consistent text style and color scheme across all slides.
    
    Args:
        report_data: Either a string (text content) or dict with sections
        image_paths: Optional list of image file paths
        output_filename: Output filename
        title: Optional title for the presentation (from user prompt)
        
    Returns:
        str: Path to the generated PPTX.
    """
    if not output_filename:
        output_filename = f"presentation_{uuid.uuid4().hex[:8]}.pptx"
    
    image_paths = image_paths or []
    
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Parse content into sections if string
    if isinstance(report_data, str):
        # Split by double newlines to get sections
        sections = [s.strip() for s in report_data.split('\n\n') if s.strip()]
        if not sections:
            sections = [report_data]
        # Generate title from first line if not provided
        if not title and sections:
            first_section = sections[0]
            first_line = first_section.split('\n')[0][:60]
            title = first_line if first_line else "Presentation"
    else:
        # Convert dict to list of (title, content) tuples
        sections = []
        for key, value in report_data.items():
            if key not in ['image_descriptions', 'title'] and value:
                section_title = key.replace('_', ' ').title()
                if isinstance(value, list):
                    sections.append((section_title, value))
                else:
                    sections.append((section_title, str(value)))
        # Use provided title or generate from content
        if not title:
            title = report_data.get('title', 'Presentation')
    
    # Slide 1: Title slide with user-provided or generated title
    add_title_slide(prs, title, "Generated Report")
    
    # Create slides dynamically based on content
    def add_dynamic_slide(prs, slide_title, content):
        """Add a slide with content that fits within boundaries."""
        slide_layout = prs.slide_layouts[6]  # Blank
        slide = prs.slides.add_slide(slide_layout)
        
        # White background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = RGBColor(255, 255, 255)
        bg.line.fill.background()
        
        # Header bar - consistent primary blue
        header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.0))
        header.fill.solid()
        header.fill.fore_color.rgb = RGBColor(*COLORS['primary'])
        header.line.fill.background()
        
        # Title text
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.5))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = slide_title[:50]  # Limit title length
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        
        # Content area
        if isinstance(content, list):
            # Bullet points - max 6 per slide, proper spacing
            y_start = 1.3
            line_height = 0.8
            for i, point in enumerate(content[:6]):
                point_box = slide.shapes.add_textbox(
                    Inches(0.8), 
                    Inches(y_start + i * line_height), 
                    Inches(11.5), 
                    Inches(0.7)
                )
                tf = point_box.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                point_text = clean_text(str(point))[:120]  # Limit each point
                p.text = f"• {point_text}"
                p.font.size = Pt(16)
                p.font.color.rgb = RGBColor(30, 41, 59)
        else:
            # Paragraph content - limit to 400 chars per slide
            content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(12), Inches(5.5))
            tf = content_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            cleaned = clean_text(str(content))[:400]  # Strict limit
            p.text = cleaned
            p.font.size = Pt(16)
            p.font.color.rgb = RGBColor(30, 41, 59)
        
        return slide
    
    # Split content into slides - ensure minimum 10 slides
    slide_count = 1  # Already have title slide
    
    for section in sections:
        if isinstance(section, tuple):
            sec_title, content = section
        else:
            lines = str(section).split('\n')
            sec_title = lines[0][:40] if lines else "Content"
            content = '\n'.join(lines[1:]) if len(lines) > 1 else section
        
        if not content:
            continue
            
        # Split long content into multiple slides
        if isinstance(content, str) and len(content) > 400:
            # Split into chunks
            words = content.split()
            chunks = []
            current_chunk = []
            current_len = 0
            
            for word in words:
                if current_len + len(word) > 350:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [word]
                    current_len = len(word)
                else:
                    current_chunk.append(word)
                    current_len += len(word) + 1
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            for i, chunk in enumerate(chunks):
                chunk_title = f"{sec_title}" if i == 0 else f"{sec_title} (cont.)"
                add_dynamic_slide(prs, chunk_title, chunk)
                slide_count += 1
        elif isinstance(content, list):
            # Split list into groups of 6
            for i in range(0, len(content), 6):
                chunk = content[i:i+6]
                chunk_title = f"{sec_title}" if i == 0 else f"{sec_title} (cont.)"
                add_dynamic_slide(prs, chunk_title, chunk)
                slide_count += 1
        else:
            add_dynamic_slide(prs, sec_title, content)
            slide_count += 1
    
    # Add image slides
    for i, img_path in enumerate(image_paths[:4]):
        if os.path.exists(img_path):
            add_image_slide(prs, f"Visualization {i+1}", img_path)
            slide_count += 1
    
    # Ensure minimum 10 slides by adding summary/filler slides if needed
    default_sections = [
        ("Overview", "This presentation covers the key points provided."),
        ("Summary", "The main topics have been outlined in the previous slides."),
        ("Key Points", "Important information has been highlighted throughout."),
        ("Conclusion", "This concludes the main content of the presentation."),
        ("Next Steps", "Consider reviewing the material for further action items."),
        ("Notes", "Additional notes can be added as needed."),
    ]
    
    filler_idx = 0
    while slide_count < 9 and filler_idx < len(default_sections):  # 9 + closing = 10
        add_dynamic_slide(prs, default_sections[filler_idx][0], default_sections[filler_idx][1])
        slide_count += 1
        filler_idx += 1
    
    # Closing slide
    add_closing_slide(prs)
    
    # Create output directory
    output_dir = os.path.join(os.getcwd(), "outputs", "ppts")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save
    output_path = os.path.join(output_dir, output_filename)
    prs.save(output_path)
    return output_path
