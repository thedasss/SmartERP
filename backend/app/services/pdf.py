from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from app.models.finance import Invoice

class PDFService:
    @staticmethod
    def generate_invoice_pdf(invoice: Invoice) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Header
        elements.append(Paragraph(f"<b>INVOICE</b> - {invoice.invoice_number}", styles['Heading1']))
        elements.append(Spacer(1, 12))
        
        elements.append(Paragraph(f"<b>Status:</b> {invoice.status.value}", styles['Normal']))
        elements.append(Paragraph(f"<b>Date:</b> {invoice.created_at.strftime('%Y-%m-%d') if invoice.created_at else 'N/A'}", styles['Normal']))
        elements.append(Paragraph(f"<b>Due Date:</b> {invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else 'N/A'}", styles['Normal']))
        elements.append(Spacer(1, 24))

        # Basic Table Data
        data = [
            ["Description", "Amount"],
            ["Invoice Total", f"${invoice.total_amount:,.2f}"],
            ["Amount Paid", f"${invoice.amount_paid:,.2f}"],
            ["Balance Due", f"${(invoice.total_amount - invoice.amount_paid):,.2f}"]
        ]

        table = Table(data, colWidths=[300, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 24))
        
        # Notes
        if invoice.notes:
            elements.append(Paragraph("<b>Notes:</b>", styles['Heading3']))
            elements.append(Paragraph(invoice.notes, styles['Normal']))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
