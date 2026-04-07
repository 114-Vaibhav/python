from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
import os

def generate_pdf(month, year, total_revenue, total_units, avg_revenue, region_revenue, region_units, daily_chart_path, region_chart_path, pie_chart_path, units_chart_path):

    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f'{month}_{year}_monthly_sales_report.pdf')

    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']

    # Title
    elements.append(Paragraph(f"Monthly Sales Report ({month}-{year})", title_style))
    elements.append(Spacer(1, 12))

    # Summary
    elements.append(Paragraph(f"<b>Total Revenue:</b> {total_revenue}", normal_style))
    elements.append(Paragraph(f"<b>Total Units Sold:</b> {total_units}", normal_style))
    elements.append(Paragraph(f"<b>Average Revenue per Sale:</b> {avg_revenue}", normal_style))
    elements.append(Spacer(1, 12))

    # Region-wise Revenue Table
    elements.append(Paragraph("🌍 Region-wise Revenue", subtitle_style))
    table_data = [["Region", "Revenue"]]
    for region, revenue in region_revenue.items():
        table_data.append([region, f"{revenue:.2f}"])

    table = Table(table_data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Region-wise Units Table
    elements.append(Paragraph("📦 Region-wise Units Sold", subtitle_style))
    table_data_units = [["Region", "Units"]]
    for region, units in region_units.items():
        table_data_units.append([region, units])

    table_units = Table(table_data_units, hAlign='LEFT')
    table_units.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    elements.append(table_units)
    elements.append(Spacer(1, 12))

    # Charts
    for chart_path, chart_title in [
        (daily_chart_path, "Daily Revenue Trend"),
        (region_chart_path, "Revenue by Region"),
        (pie_chart_path, "Revenue Distribution (Pie Chart)"),
        (units_chart_path, "Units Sold by Region")
    ]:
        if os.path.exists(chart_path):
            elements.append(Paragraph(chart_title, subtitle_style))
            elements.append(Image(chart_path, width=400, height=250))
            elements.append(Spacer(1, 12))

    # Build PDF
    doc.build(elements)

    print(f"✅ PDF generated: {pdf_path}")