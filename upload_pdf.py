from pypdf import PdfReader


def extract_pdf_text(uploaded_file):

    pdf = PdfReader(uploaded_file)

    text = ""

    for page in pdf.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    return text


def extract_txt_text(uploaded_file):

    return uploaded_file.read().decode("utf-8")