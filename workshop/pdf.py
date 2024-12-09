from fpdf import FPDF


def write_2_pdf(self):
    # Create a PDF object
    pdf = FPDF()
    pdf.add_page()

    # Calculate the center x-coordinate for the table
    print(f"page width: {pdf.w}")
    print(f"page left margin: {pdf.l_margin}")
    print(f"page right margin: {pdf.r_margin}")
    pew = pdf.w - (pdf.l_margin + pdf.r_margin)
    print(f"page effective width: {pew}")

    # Add title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(pew, 10, "My Plotly Plot", ln=1, align='C')

    # Add text
    pdf.set_font("Arial", "B", 12)
    pdf.cell(pew, 10, "This is some descriptive text about the plot.", ln=1)

    # Add a table header
    pdf.set_font('Arial', '', 10)
    pdf.cell(pew / 3, 10, 'Column 1', 1, 0, 'C')
    pdf.cell(pew / 3, 10, 'Column 2', 1, 0, 'C')
    pdf.cell(pew / 3, 10, 'Column 3', 1, 1, 'C')

    # Add table rows
    pdf.set_font('Arial', '', 10)
    pdf.cell(pew / 3, 10, 'Row 1, Col 1', 1, 0, 'C')
    pdf.cell(pew / 3, 10, 'Row 1, Col 2', 1, 0, 'C')
    pdf.cell(pew / 3, 10, 'Row 1, Col 3', 1, 1, 'C')

    pdf.cell(pew / 4, 10, 'Row 2, Col 1', 1, 0, 'C')
    pdf.cell(pew / 4, 10, 'Row 2, Col 2', 1, 0, 'C')
    pdf.cell(pew / 4, 10, 'Row 2, Col 3', 1, 0, 'C')
    pdf.cell(pew / 4, 10, 'Row 2, Col 4', 1, 1, 'C')

    pdf.cell(pew / 4, 10, '', 0, 1, 'C')

    # Add image in the center X axis of the page but just below the table
    pdf.image("my_plot.png", x=50, w=100)

    pdf.output("my_pdf.pdf")