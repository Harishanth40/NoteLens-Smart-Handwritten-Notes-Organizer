import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_note_pdf(note):
    """
    Generates PDF document buffer for a Note object.
    Returns BytesIO buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles
    brand_style = ParagraphStyle(
        'BrandTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#3B82F6'), # Primary Indigo/Blue
        alignment=TA_LEFT,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'BrandSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#6B7280'),
        spaceAfter=15
    )

    title_style = ParagraphStyle(
        'NoteTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=12
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#4B5563')
    )

    meta_val_style = ParagraphStyle(
        'MetaValue',
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#111827')
    )

    body_style = ParagraphStyle(
        'ExtractedBody',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#1F2937')
    )

    elements = []

    # Header / Branding
    elements.append(Paragraph("NoteLens", brand_style))
    elements.append(Paragraph("Smart Handwritten Notes Organizer", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#E5E7EB'), spaceAfter=15))

    # Note Title
    elements.append(Paragraph(note.title, title_style))
    elements.append(Spacer(1, 8))

    # Metadata Grid Table
    created_str = note.created_at.strftime('%B %d, %Y - %I:%M %p') if hasattr(note.created_at, 'strftime') else str(note.created_at)
    
    meta_data = [
        [
            Paragraph("Subject:", meta_label_style), Paragraph(note.subject, meta_val_style),
            Paragraph("Topic:", meta_label_style), Paragraph(note.topic, meta_val_style)
        ],
        [
            Paragraph("Confidence:", meta_label_style), Paragraph(f"{note.confidence:.1f}%", meta_val_style),
            Paragraph("Date Added:", meta_label_style), Paragraph(created_str, meta_val_style)
        ]
    ]

    meta_table = Table(meta_data, colWidths=[80, 180, 80, 180])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#F3F4F6')),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 20))

    # Extracted Text Header
    elements.append(Paragraph("Extracted Handwritten Text", ParagraphStyle(
        'SectionHeading',
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#111827'),
        spaceAfter=8
    )))

    # Format Extracted Text into Paragraphs
    raw_lines = note.extracted_text.splitlines() if note.extracted_text else ["(No extracted text found)"]
    formatted_text = "<br/>".join([line.replace('<', '&lt;').replace('>', '&gt;') for line in raw_lines])

    text_table = Table([[Paragraph(formatted_text, body_style)]], colWidths=[520])
    text_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAFA')),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#D1D5DB')),
        ('ROUNDEDCORNERS', [4, 4, 4, 4])
    ]))
    elements.append(text_table)

    # Footer spacer
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E5E7EB'), spaceAfter=8))
    elements.append(Paragraph("Generated automatically by NoteLens • Smart Notes Organizer", ParagraphStyle(
        'Footer',
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#9CA3AF'),
        alignment=TA_CENTER
    )))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
