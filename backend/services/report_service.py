import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime


def generate_validation_report(document, result, output_path):
    """Generate a PDF validation report for a document result."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = styles['Title']
    elements.append(Paragraph("Document Validation Report", title_style))
    elements.append(Spacer(1, 20))

    # Document Information
    elements.append(Paragraph("<b>Document Information</b>", styles['Heading2']))
    doc_info = [
        ["Filename", document.filename],
        ["File Type", document.file_type.upper()],
        ["Upload Date", document.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if document.uploaded_at else "N/A"],
        ["User ID", str(document.user_id)]
    ]
    t1 = Table(doc_info, colWidths=[150, 300])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 20))

    # Validation Result
    elements.append(Paragraph("<b>Validation Result</b>", styles['Heading2']))
    
    verdict_color = colors.red
    if result.verdict == 'AUTHENTIC':
        verdict_color = colors.green
    elif result.verdict == 'SUSPICIOUS':
        verdict_color = colors.orange

    res_info = [
        ["Verdict", Paragraph(f"<font color={verdict_color.hexval()}><b>{result.verdict}</b></font>", styles['Normal'])],
        ["Overall Authenticity Score", f"{result.score * 100:.2f}%"],
        ["AI Visual Confidence (CNN)", f"{result.cnn_score * 100:.2f}%"],
        ["OCR Text Confidence", f"{result.ocr_confidence * 100:.2f}%"],
        ["Database Match Score", f"{result.db_match_score * 100:.2f}%"],
        ["Validation Timestamp", result.validated_at.strftime("%Y-%m-%d %H:%M:%S") if result.validated_at else "N/A"]
    ]
    t2 = Table(res_info, colWidths=[150, 300])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 20))

    # Extracted Data
    if result.extracted_data:
        elements.append(Paragraph("<b>Extracted Data Verification</b>", styles['Heading2']))
        data_rows = [["Field", "Value", "Match status"]]
        for field, value in result.extracted_data.items():
            match = result.match_details.get(field, False)
            match_text = "PASSED" if match else "FAILED"
            match_color = colors.green if match else colors.red
            data_rows.append([
                field.capitalize(), 
                str(value), 
                Paragraph(f"<font color={match_color.hexval()}>{match_text}</font>", styles['Normal'])
            ])
        
        t3 = Table(data_rows, colWidths=[100, 250, 100])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t3)

    # Footer
    elements.append(Spacer(1, 40))
    footer_text = f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Document-Validator AI System."
    elements.append(Paragraph(footer_text, ParagraphStyle(name='Footer', fontSize=8, textColor=colors.grey)))

    doc.build(elements)
    return output_path
