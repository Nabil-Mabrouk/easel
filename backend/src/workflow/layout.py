from pathlib import Path
from typing import List
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
from reportlab.lib import colors
from textwrap import wrap

# -------------------- Page Size --------------------
PAGE_WIDTH = PAGE_HEIGHT = 8.5 * inch  # square page for kids book

# -------------------- Utilities --------------------

def draw_cover_title_top_box(c: "canvas.Canvas", title: str, page_width: float, page_height: float,
                             max_words_per_line: int = 3, font_name: str = "Helvetica-Bold",
                             font_size: int = 42, line_spacing: int = 10,
                             box_color=colors.white, alpha: float = 0.5, padding: float = 20):
    words = title.split()
    lines = []
    i = 0
    while i < len(words):
        lines.append(" ".join(words[i:i + max_words_per_line]))
        i += max_words_per_line

    c.setFont(font_name, font_size)
    total_text_height = len(lines) * font_size + (len(lines) - 1) * line_spacing
    max_line_width = max(c.stringWidth(line, font_name, font_size) for line in lines)
    box_width = max_line_width + 2 * padding
    box_height = total_text_height + 2 * padding

    y_center = page_height * 2 / 3 - box_height / 2
    x_center = page_width / 2
    box_x = x_center - box_width / 2
    box_y = y_center - box_height / 2

    c.saveState()
    c.setFillColor(box_color, alpha=alpha)
    c.rect(box_x, box_y, box_width, box_height, fill=1, stroke=0)
    c.restoreState()

    y_text_start = box_y + box_height - padding - font_size
    for line in lines:
        line_width = c.stringWidth(line, font_name, font_size)
        x_text = x_center - line_width / 2
        c.drawString(x_text, y_text_start, line)
        y_text_start -= font_size + line_spacing

def draw_page_number(c: "canvas.Canvas", page_num: int, page_width: float, page_height: float,
                     margin_bottom: float = 0.5*inch, font_name="Helvetica", font_size=14):
    c.setFont(font_name, font_size)
    text = str(page_num)
    text_width = c.stringWidth(text, font_name, font_size)
    x = (page_width - text_width) / 2
    y = margin_bottom
    c.drawString(x, y, text)

def draw_text_page(c: "canvas.Canvas", text: str, page_width: float, page_height: float,
                   font_name="Times-Roman", font_size=24, line_spacing=10, side_margin=inch):
    c.setFont(font_name, font_size)
    c.setFillColor(colors.black)

    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if c.stringWidth(test_line, font_name, font_size) <= (page_width - 2*side_margin):
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    total_text_height = len(lines) * font_size + (len(lines) - 1) * line_spacing
    y_start = (page_height + total_text_height)/2 - font_size

    for i, line in enumerate(lines):
        if i == len(lines) - 1:
            c.drawString(side_margin, y_start, line)
        else:
            words_in_line = line.split()
            if len(words_in_line) == 1:
                c.drawString(side_margin, y_start, line)
            else:
                line_width = c.stringWidth(line, font_name, font_size)
                space_needed = page_width - 2*side_margin - sum(c.stringWidth(w, font_name, font_size) for w in words_in_line)
                extra_space = space_needed / (len(words_in_line)-1)
                x = side_margin
                for w in words_in_line:
                    c.drawString(x, y_start, w)
                    x += c.stringWidth(w, font_name, font_size) + extra_space
        y_start -= font_size + line_spacing

# -------------------- Main PDF Builder --------------------

def build_kids_pdf(title: str, chapters: List[str], images: List[Path], output_pdf: Path):
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_pdf), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    page_counter = 1

    # Cover page
    cover_img = ImageReader(str(images[0]))
    c.drawImage(cover_img, 0, 0, width=PAGE_WIDTH, height=PAGE_HEIGHT, preserveAspectRatio=False, mask='auto')
    draw_cover_title_top_box(c, title, PAGE_WIDTH, PAGE_HEIGHT)
    c.showPage()  # cover: no page number

    # Story pages
    for i, (text, img_path) in enumerate(zip(chapters, images[1:])):
        img = ImageReader(str(img_path))
        c.drawImage(img, 0, 0, width=PAGE_WIDTH, height=PAGE_HEIGHT, preserveAspectRatio=False, mask='auto')
        draw_page_number(c, page_counter, PAGE_WIDTH, PAGE_HEIGHT)
        page_counter += 1
        c.showPage()

        draw_text_page(c, text, PAGE_WIDTH, PAGE_HEIGHT)
        draw_page_number(c, page_counter, PAGE_WIDTH, PAGE_HEIGHT)
        page_counter += 1
        c.showPage()

    # Back cover
    back_img = ImageReader(str(images[-1]))
    c.drawImage(back_img, 0, 0, width=PAGE_WIDTH, height=PAGE_HEIGHT, preserveAspectRatio=False, mask='auto')
    c.showPage()  # back cover: no page number

    c.save()
    return output_pdf

 