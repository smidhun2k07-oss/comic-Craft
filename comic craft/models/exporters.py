import os
from datetime import datetime
from pathlib import Path

from fpdf import FPDF

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORTS_DIR = BASE_DIR / "app" / "static" / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


class ComicPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "ComicCraft - AI Comic", 0, 1, "C")


def save_pdf(layout, character_name="Hero"):
    if not layout:
        raise ValueError("No comic panels were generated to export.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comic_{sanitize(character_name)}_{timestamp}.pdf"
    filepath = EXPORTS_DIR / filename

    pdf = ComicPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Panel {panel['panel_number']}: {panel['title']}", ln=True, align="C")
        pdf.ln(5)

        try:
            image_path = panel.get("image_path", "")
            if image_path:
                real_img_path = (BASE_DIR / "app" / "static" / image_path.lstrip("/").replace("static/", ""))
                if real_img_path.exists():
                    pdf.image(str(real_img_path), x=15, w=180)
            pdf.ln(5)
        except Exception as e:
            print(f"PDF image error: {e}")

        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 8, f"Scene: {panel.get('scene_description', '')}")
        pdf.ln(3)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, f"Caption: {panel.get('caption', '')}")
        pdf.ln(2)
        pdf.multi_cell(0, 8, f"Narration: {panel.get('narration', '')}")

    pdf.output(filepath)
    return f"/static/exports/{filename}", filepath


def sanitize(text):
    return "".join(c if c.isalnum() else "_" for c in text)[:20]
