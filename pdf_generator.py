from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def create_pdf(text, filename="report.pdf"):

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph("AI Research Report", styles["Title"])
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(text.replace("\n", "<br/>"), styles["BodyText"])
    )

    doc.build(story)

    return filename