from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
import io, os, datetime, urllib.request

W, H = A4  # 595 x 842 pt

# Bonfire Club brand colors
BLACK      = colors.HexColor('#000000')
WHITE      = colors.HexColor('#FFFFFF')
OFF_WHITE  = colors.HexColor('#F5F5F0')
ACCENT     = colors.HexColor('#39FF14')   # neon green
DARK_GREEN = colors.HexColor('#00140e')
GRAY       = colors.HexColor('#888888')
LIGHT_GRAY = colors.HexColor('#CCCCCC')
DARK_GRAY  = colors.HexColor('#1a1a1a')
TABLE_BORDER = colors.HexColor('#333333')

def draw_page_bg(c, color=BLACK):
    c.setFillColor(color)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def draw_logo(c, x, y, size=18):
    """Draw BONFIRECLUB logo with accent color on last part"""
    c.setFont('Helvetica-Bold', size)
    c.setFillColor(WHITE)
    c.drawString(x, y, 'BONFIRE')
    bonfire_w = c.stringWidth('BONFIRE', 'Helvetica-Bold', size)
    c.setFillColor(ACCENT)
    c.drawString(x + bonfire_w, y, 'CLUB')

def draw_footer(c, page_num=None):
    c.setFillColor(colors.HexColor('#111111'))
    c.rect(0, 0, W, 28*mm, fill=1, stroke=0)
    c.setFont('Helvetica', 7.5)
    c.setFillColor(GRAY)
    c.drawString(20*mm, 14*mm, 'www.bonfireclub.be  |  info@bonfireclub.be  |  +32 XXX XX XX XX')
    c.setFillColor(ACCENT)
    # YP-style logo bottom right
    c.setFont('Helvetica-Bold', 10)
    c.drawRightString(W - 20*mm, 14*mm, 'BFC')

def load_image(path_or_url):
    """Load image from file path"""
    if path_or_url and os.path.exists(path_or_url):
        return ImageReader(path_or_url)
    return None

def fit_image(img_reader, max_w, max_h):
    """Return (w, h) fitting within max dimensions, preserving aspect ratio"""
    if img_reader is None:
        return max_w, max_h
    iw, ih = img_reader.getSize()
    ratio = min(max_w / iw, max_h / ih)
    return iw * ratio, ih * ratio


# ─────────────────────────────────────────────
# PAGE 1 — Cover
# ─────────────────────────────────────────────
def page_cover(c, data):
    draw_page_bg(c, BLACK)

    # Hero image (mockup 2 = roomscene, full bleed top)
    hero = load_image(data.get('mockup2'))
    if hero:
        hw, hh = fit_image(hero, W, H * 0.62)
        hx = (W - hw) / 2
        c.drawImage(hero, hx, H - hh - 10*mm, hw, hh, mask='auto')
        # Dark overlay gradient effect
        c.setFillColor(colors.Color(0, 0, 0, alpha=0.45))
        c.rect(0, H - hh - 10*mm, W, hh, fill=1, stroke=0)
    else:
        # Fallback gradient block
        c.setFillColor(DARK_GRAY)
        c.rect(0, H * 0.38, W, H * 0.62, fill=1, stroke=0)

    # Logo top center
    logo_text = 'BONFIRE'
    logo_size = 22
    lw = c.stringWidth(logo_text, 'Helvetica-Bold', logo_size)
    club_w = c.stringWidth('CLUB', 'Helvetica-Bold', logo_size)
    total_w = lw + club_w
    lx = (W - total_w) / 2
    draw_logo(c, lx, H - 22*mm, logo_size)

    # "DESIGN PROPOSAL" title
    c.setFont('Helvetica-Bold', 38)
    c.setFillColor(ACCENT)
    title = 'DESIGN PROPOSAL'
    tw = c.stringWidth(title, 'Helvetica-Bold', 38)
    c.drawString((W - tw) / 2, 115*mm, title)

    # Info table
    table_x = 80*mm
    table_w = W - 2 * table_x
    table_y = 88*mm
    row_h = 9*mm
    fields = [
        ('Client:', data.get('client_name', '')),
        ('Quote #:', data.get('quote_number', '')),
        ('Date:', data.get('date', '')),
    ]
    for i, (label, value) in enumerate(fields):
        ry = table_y - i * row_h
        # Border
        c.setStrokeColor(ACCENT)
        c.setLineWidth(0.5)
        c.rect(table_x, ry - row_h + 2*mm, table_w, row_h, fill=0, stroke=1)
        c.setFont('Helvetica', 9)
        c.setFillColor(ACCENT)
        c.drawString(table_x + 4*mm, ry - row_h + 4.5*mm, label)
        c.setFillColor(WHITE)
        c.drawString(table_x + 35*mm, ry - row_h + 4.5*mm, value)

    # CONFIDENTIAL
    c.setFont('Helvetica-Bold', 13)
    c.setFillColor(WHITE)
    conf = 'CONFIDENTIAL'
    cw = c.stringWidth(conf, 'Helvetica-Bold', 13)
    c.drawString((W - cw) / 2, 28*mm, conf)

    draw_footer(c)
    c.showPage()


# ─────────────────────────────────────────────
# PAGE 2 — Mockup + Product specs
# ─────────────────────────────────────────────
def page_mockup(c, data):
    draw_page_bg(c, WHITE)

    # Header bar
    c.setFillColor(BLACK)
    c.rect(0, H - 22*mm, W, 22*mm, fill=1, stroke=0)
    draw_logo(c, 20*mm, H - 14*mm, 14)

    # Section title
    c.setFillColor(BLACK)
    c.setFont('Helvetica-Bold', 20)
    c.drawString(20*mm, H - 42*mm, 'MOCKUP &')
    c.drawString(20*mm, H - 52*mm, 'PRODUCT INFOS')

    # Mockup images side by side
    img_y = H - 140*mm
    img_h = 80*mm
    img_w = (W - 50*mm) / 2

    m1 = load_image(data.get('mockup1'))
    m2 = load_image(data.get('mockup2'))

    # Image 1 - white bg mockup with dimensions
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(0.5)
    c.rect(20*mm, img_y, img_w, img_h, fill=0, stroke=1)
    if m1:
        mw, mh = fit_image(m1, img_w - 4*mm, img_h - 4*mm)
        mx = 20*mm + (img_w - mw) / 2
        my = img_y + (img_h - mh) / 2
        c.drawImage(m1, mx, my, mw, mh, mask='auto')
    c.setFont('Helvetica', 7)
    c.setFillColor(GRAY)
    c.drawString(20*mm, img_y + img_h + 2*mm, 'Indoor')

    # Image 2 - roomscene
    rx = 20*mm + img_w + 10*mm
    c.setStrokeColor(LIGHT_GRAY)
    c.rect(rx, img_y, img_w, img_h, fill=0, stroke=1)
    if m2:
        mw2, mh2 = fit_image(m2, img_w - 4*mm, img_h - 4*mm)
        mx2 = rx + (img_w - mw2) / 2
        my2 = img_y + (img_h - mh2) / 2
        c.drawImage(m2, mx2, my2, mw2, mh2, mask='auto')
    c.setFont('Helvetica', 7)
    c.setFillColor(GRAY)
    c.drawString(rx, img_y + img_h + 2*mm, 'Essential Neon')

    # SIGN INFO
    sy = img_y - 14*mm
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(BLACK)
    c.drawString(20*mm, sy, 'SIGN INFO:')

    specs_left = [
        ('Technology:', data.get('technology', 'LED Neon Flex')),
        ('Neon Size:', f"{data.get('width', '')}cm x {data.get('height', '')}cm"),
        ('Neon Color:', data.get('neon_color', '')),
    ]
    specs_right = [
        ('Jacket Type:', data.get('jacket_type', '')),
        ('Usage:', data.get('usage', 'Indoor')),
        ('Installation:', data.get('installation', '')),
    ]

    sy2 = sy - 6*mm
    for label, val in specs_left:
        c.setFont('Helvetica-Bold', 9)
        c.setFillColor(BLACK)
        c.drawString(20*mm, sy2, label)
        c.setFont('Helvetica', 9)
        c.drawString(55*mm, sy2, val)
        sy2 -= 6*mm

    sy2 = sy - 6*mm
    for label, val in specs_right:
        c.setFont('Helvetica-Bold', 9)
        c.setFillColor(BLACK)
        c.drawString(W/2, sy2, label)
        c.setFont('Helvetica', 9)
        c.drawString(W/2 + 30*mm, sy2, val)
        sy2 -= 6*mm

    # BACKING INFO
    by = sy2 - 4*mm
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(BLACK)
    c.drawString(20*mm, by, 'BACKING INFO:')

    backing_specs = [
        ('Backing:', data.get('backing', '')),
        ('Backing color:', data.get('backing_color', 'Transparant')),
        ('Description:', data.get('backing_description', '')),
    ]
    by2 = by - 6*mm
    for label, val in backing_specs:
        c.setFont('Helvetica-Bold', 9)
        c.setFillColor(BLACK)
        c.drawString(20*mm, by2, label)
        c.setFont('Helvetica', 9)
        c.drawString(55*mm, by2, val)
        by2 -= 6*mm

    # OTHER DETAILS (USPs)
    oy = by2 - 6*mm
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(BLACK)
    c.drawString(20*mm, oy, 'OTHER DETAILS:')

    usps = [
        ('Gemaakt in België:', 'Kwaliteit en vakmanschap in elk ontwerp.'),
        ('50.000 uur levensduur:', 'De meest duurzame LED neon op de markt.'),
        ('2 jaar garantie:', 'Voor jouw gemoedsrust.'),
        ('Installatie:', 'Eenvoudig te monteren, 100% veilig, wordt niet warm.'),
    ]
    oy2 = oy - 6*mm
    for bold, rest in usps:
        c.setFont('Helvetica-Bold', 8.5)
        c.setFillColor(BLACK)
        c.drawString(20*mm, oy2, bold)
        bw = c.stringWidth(bold, 'Helvetica-Bold', 8.5)
        c.setFont('Helvetica', 8.5)
        c.drawString(20*mm + bw + 2*mm, oy2, rest)
        oy2 -= 5.5*mm

    # Process flow
    steps = ['Quote\nApproval', 'Betaling', 'Productie', 'Gratis\nLevering']
    step_w = (W - 40*mm) / len(steps)
    flow_y = 45*mm
    for i, step in enumerate(steps):
        sx = 20*mm + i * step_w + step_w / 2
        # Circle
        c.setStrokeColor(ACCENT if i == 0 else LIGHT_GRAY)
        c.setFillColor(WHITE)
        c.setLineWidth(1.5 if i == 0 else 0.8)
        c.circle(sx, flow_y + 8*mm, 8*mm, fill=1, stroke=1)
        # Arrow
        if i < len(steps) - 1:
            c.setStrokeColor(LIGHT_GRAY)
            c.setLineWidth(0.8)
            c.line(sx + 8*mm, flow_y + 8*mm, sx + step_w - 8*mm, flow_y + 8*mm)
        # Label
        lines = step.split('\n')
        for j, line in enumerate(lines):
            c.setFont('Helvetica', 7)
            c.setFillColor(BLACK)
            lw = c.stringWidth(line, 'Helvetica', 7)
            c.drawString(sx - lw/2, flow_y - 2*mm - j*5*mm, line)

    # Timeline label
    c.setFont('Helvetica', 8)
    c.setFillColor(GRAY)
    timeline = data.get('delivery_time', '2-4 WEKEN')
    tw = c.stringWidth(timeline, 'Helvetica', 8)
    c.drawString((W - tw)/2, 32*mm, timeline)

    draw_footer(c)
    c.showPage()


# ─────────────────────────────────────────────
# PAGE 3 — Quote / Offerte
# ─────────────────────────────────────────────
def page_quote(c, data):
    draw_page_bg(c, WHITE)

    # Header
    c.setFillColor(BLACK)
    c.rect(0, H - 22*mm, W, 22*mm, fill=1, stroke=0)
    draw_logo(c, 20*mm, H - 14*mm, 14)

    # Contact bar
    c.setFont('Helvetica', 8)
    c.setFillColor(GRAY)
    c.drawString(20*mm, H - 34*mm, 'www.bonfireclub.be  |  info@bonfireclub.be  |  +32 XXX XX XX XX')

    # PAY NOW button
    btn_w = 36*mm
    btn_h = 9*mm
    btn_x = W - 20*mm - btn_w
    btn_y = H - 38*mm
    c.setFillColor(ACCENT)
    c.roundRect(btn_x, btn_y, btn_w, btn_h, 2*mm, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(BLACK)
    label = 'BETAAL NU'
    lw = c.stringWidth(label, 'Helvetica-Bold', 9)
    c.drawString(btn_x + (btn_w - lw)/2, btn_y + 2.5*mm, label)

    # Section title
    c.setFont('Helvetica-Bold', 28)
    c.setFillColor(BLACK)
    c.drawString(20*mm, H - 56*mm, 'OFFERTE')

    # Client info table
    ci_x = 20*mm
    ci_y = H - 78*mm
    ci_w = (W - 40*mm) / 2 - 5*mm
    row_h = 8*mm
    left_fields = [
        ('Client:', data.get('client_name', '')),
        ('Naam:', data.get('client_name', '')),
        ('Email:', data.get('client_email', '')),
        ('Tel:', data.get('client_phone', '')),
    ]
    right_fields = [
        ('Offerte #:', data.get('quote_number', '')),
        ('Datum:', data.get('date', '')),
        ('Valuta:', 'EUR'),
        ('', ''),
    ]

    for i, ((ll, lv), (rl, rv)) in enumerate(zip(left_fields, right_fields)):
        ry = ci_y - i * row_h
        c.setStrokeColor(TABLE_BORDER)
        c.setLineWidth(0.5)
        c.rect(ci_x, ry - row_h + 2*mm, ci_w, row_h, fill=0, stroke=1)
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(BLACK)
        c.drawString(ci_x + 3*mm, ry - row_h + 4*mm, ll)
        c.setFont('Helvetica', 8)
        c.drawString(ci_x + 25*mm, ry - row_h + 4*mm, lv)

        rx2 = ci_x + ci_w + 10*mm
        c.setStrokeColor(TABLE_BORDER)
        c.rect(rx2, ry - row_h + 2*mm, ci_w, row_h, fill=0, stroke=1)
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(BLACK)
        c.drawString(rx2 + 3*mm, ry - row_h + 4*mm, rl)
        c.setFont('Helvetica', 8)
        c.drawString(rx2 + 28*mm, ry - row_h + 4*mm, rv)

    # Products table
    table_top = ci_y - 4 * row_h - 8*mm
    col_widths = [60*mm, 90*mm, 35*mm]
    header_h = 8*mm
    tx = 20*mm

    # Table header
    headers = [('PRODUCT', 'OMSCHRIJVING', 'PRIJS')]
    c.setFillColor(LIGHT_GRAY)
    c.rect(tx, table_top - header_h, sum(col_widths), header_h, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(BLACK)
    cx = tx
    for i, h in enumerate(headers[0]):
        c.drawString(cx + 3*mm, table_top - header_h + 2.5*mm, h)
        cx += col_widths[i]

    # Product row
    prod_h = 14*mm
    py = table_top - header_h - prod_h
    c.setFillColor(BLACK)
    c.rect(tx, py, col_widths[0], prod_h, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(WHITE)
    prod_name = data.get('product_name', '').upper()
    pw = c.stringWidth(prod_name, 'Helvetica-Bold', 9)
    c.drawString(tx + (col_widths[0] - pw)/2, py + prod_h/2 - 3*mm, prod_name)

    # Description cell
    c.setStrokeColor(TABLE_BORDER)
    c.setLineWidth(0.5)
    c.rect(tx + col_widths[0], py, col_widths[1], prod_h, fill=0, stroke=1)
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(BLACK)
    c.drawString(tx + col_widths[0] + 3*mm, py + prod_h/2, f"Aantal: 1")
    c.setFont('Helvetica', 8)
    c.drawString(tx + col_widths[0] + 3*mm, py + prod_h/2 - 5*mm,
                 f"Afmeting: {data.get('width', '')}cm x {data.get('height', '')}cm")

    # Price cell
    price_x = tx + col_widths[0] + col_widths[1]
    c.setFillColor(colors.HexColor('#1a1a1a'))
    c.rect(price_x, py, col_widths[2], prod_h, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(WHITE)
    price_str = f"€{data.get('price', '0')}"
    pw2 = c.stringWidth(price_str, 'Helvetica-Bold', 10)
    c.drawString(price_x + (col_widths[2] - pw2)/2, py + prod_h/2 - 3*mm, price_str)

    # Shipping row
    ship_y = py - 10*mm
    c.setFillColor(BLACK)
    c.rect(tx, ship_y, col_widths[0], 10*mm, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(WHITE)
    c.drawString(tx + (col_widths[0] - c.stringWidth('Verzending', 'Helvetica-Bold', 8))/2,
                 ship_y + 3*mm, 'Verzending')
    c.setStrokeColor(TABLE_BORDER)
    c.rect(tx + col_widths[0], ship_y, col_widths[1], 10*mm, fill=0, stroke=1)
    c.setFont('Helvetica', 8)
    c.setFillColor(BLACK)
    c.drawString(tx + col_widths[0] + 3*mm, ship_y + 3*mm, data.get('delivery_time', '2-4 WEKEN'))
    c.setFillColor(colors.HexColor('#1a1a1a'))
    c.rect(price_x, ship_y, col_widths[2], 10*mm, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(WHITE)
    free = 'Gratis'
    fw = c.stringWidth(free, 'Helvetica-Bold', 9)
    c.drawString(price_x + (col_widths[2] - fw)/2, ship_y + 3*mm, free)

    # Notes
    note_y = ship_y - 8*mm
    c.setFont('Helvetica', 7)
    c.setFillColor(GRAY)
    c.drawString(tx, note_y, '* Prijzen variëren op basis van afmeting en complexiteit.')
    c.drawString(tx, note_y - 4*mm, '** Excl. BTW')

    # Totals
    total_y = note_y - 16*mm
    total_x = tx + col_widths[0] + col_widths[1]

    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(BLACK)
    c.drawRightString(total_x - 3*mm, total_y, 'TOTAAL')
    c.setFillColor(colors.HexColor('#1a1a1a'))
    c.rect(total_x, total_y - 2*mm, col_widths[2], 10*mm, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(WHITE)
    tot_str = f"€{data.get('price', '0')}"
    tw = c.stringWidth(tot_str, 'Helvetica-Bold', 10)
    c.drawString(total_x + (col_widths[2]-tw)/2, total_y + 1*mm, tot_str)

    final_y = total_y - 12*mm
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(BLACK)
    c.drawRightString(total_x - 3*mm, final_y, 'EINDPRIJS**')
    c.setFillColor(ACCENT)
    c.rect(total_x, final_y - 2*mm, col_widths[2], 10*mm, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 11)
    c.setFillColor(BLACK)
    fs = f"€{data.get('price', '0')}"
    fw2 = c.stringWidth(fs, 'Helvetica-Bold', 11)
    c.drawString(total_x + (col_widths[2]-fw2)/2, final_y + 1*mm, fs)

    # ADD ONS
    ao_y = final_y - 18*mm
    c.setFillColor(colors.HexColor('#F8F8F8'))
    c.rect(tx, ao_y - 28*mm, sum(col_widths), 28*mm, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(BLACK)
    c.drawString(tx + 4*mm, ao_y - 5*mm, 'ADD ONS:')

    addons = [
        ('Expreslevering (5-7 dagen):', '€90'),
        ('Dimmer afstandsbediening:', '€30'),
        ('3M strips (wandmontage):', '€10'),
        ('Ophangset:', 'Gratis op aanvraag'),
        ('2 jaar garantie:', 'Inbegrepen'),
    ]
    ao_col_w = sum(col_widths) / 2
    for i, (label, price) in enumerate(addons):
        col = i % 2
        row = i // 2
        ax = tx + 4*mm + col * ao_col_w
        ay = ao_y - 11*mm - row * 6*mm
        c.setFont('Helvetica-Bold', 7.5)
        c.setFillColor(BLACK)
        c.drawString(ax, ay, label)
        lbw = c.stringWidth(label, 'Helvetica-Bold', 7.5)
        c.setFont('Helvetica', 7.5)
        c.drawString(ax + lbw + 2*mm, ay, price)

    draw_footer(c)
    c.showPage()


# ─────────────────────────────────────────────
# MAIN — Generate full PDF
# ─────────────────────────────────────────────
def generate_quote_pdf(data):
    """
    data dict keys:
      client_name, client_email, client_phone
      product_name, width, height
      technology, neon_color, jacket_type, usage, installation
      backing, backing_color, backing_description
      uv_print (bool), delivery_time
      price (string, e.g. "349")
      mockup1 (file path), mockup2 (file path)
      quote_number (auto), date (auto)
    """
    # Auto-fill
    if not data.get('quote_number'):
        import random
        data['quote_number'] = f"BF{datetime.date.today().strftime('%y%m%d')}{random.randint(10,99)}"
    if not data.get('date'):
        data['date'] = datetime.date.today().strftime('%d/%m/%Y')

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"Bonfire Club — Offerte {data.get('quote_number', '')}")

    page_cover(c, data)
    page_mockup(c, data)
    page_quote(c, data)

    c.save()
    buf.seek(0)
    return buf, data['quote_number']
