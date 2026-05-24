from reportlab.pdfgen import canvas

def create_pdf(text, filename="output.pdf"):

    c = canvas.Canvas(filename)

    c.drawString(100, 750, text)

    c.save()

    return filename