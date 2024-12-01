from fpdf import FPDF

def create_pdf(entries):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for entry in entries:
        pdf.cell(0, 10, f"Date: {entry['date']}", ln=True)
        pdf.multi_cell(0, 10, f"Entry: {entry['entry']}\n", border=0, align="L")
    return pdf.output(dest="S").encode("latin1")
