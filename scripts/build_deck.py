"""Build the competition deck from competition/deck_data.json and competition/screenshots/.

    .venv/Scripts/python -m pip install python-pptx     # dev tool only; not a runtime dependency
    .venv/Scripts/python scripts/build_deck.py

Writes competition/PITCH_DECK.md (always) and competition/IntegrationRescue_Competition_Deck.pptx (needs
python-pptx). Missing founder assets appear as amber dashed "[PLACEHOLDER: ...]" boxes so they cannot be missed.
Render to PNG for review: scripts/render_deck.ps1 (PowerPoint) - see competition/DECK_QA.md.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMP = ROOT / "competition"
SHOTS = COMP / "screenshots"
DATA = json.loads((COMP / "deck_data.json").read_text(encoding="utf-8"))
PH = DATA["placeholders"]

BG, PANEL, PANEL2, TEXT, MUTED = "0E1116", "161B22", "1F2630", "E6E9EE", "9AA4B2"
ACCENT, OK, WARN, BAD = "5B8DEF", "3FB37F", "E0A23B", "E5534B"
FONT = "Segoe UI"


# ----------------------------------------------------------------------------------------------- Markdown spec
def visible_text(s: dict) -> list[str]:
    out: list[str] = []
    for key in ("chips", "checks", "bullets", "steps", "nodes"):
        out += [str(x) for x in s.get(key, [])]
    for key in ("cards", "personas", "columns", "tiles", "boxes", "stages"):
        for item in s.get(key, []):
            out.append(" · ".join(str(x) for x in item if not isinstance(x, (bool, list))) +
                       (" → " + ", ".join(item[1]) if isinstance(item, list) and len(item) > 1
                        and isinstance(item[1], list) else ""))
    for key in ("buyer", "status", "footer", "small", "segment", "measured", "footnote", "repo"):
        if s.get(key):
            out.append(s[key])
    return out


def write_markdown() -> None:
    out = ["# Pitch deck specification (15 slides)", "",
           f"**Status: {DATA['status']}.** Generated from `competition/deck_data.json` by `scripts/build_deck.py` "
           f"({DATA['updated']}). Edit the JSON, not this file. Every figure must match "
           "[TECHNICAL_EVIDENCE.md](TECHNICAL_EVIDENCE.md). Visual QA: [DECK_QA.md](DECK_QA.md).", "",
           "Design: dark theme, one message per slide, real screenshots from a live Gemini run (fictional data, "
           "`competition/screenshots/`), large evidence numbers, the code-repair limitation shown at equal size, "
           "hypotheses labelled, amber placeholder boxes for missing founder assets. File: "
           "`IntegrationRescue_Competition_Deck.pptx`.", ""]
    for s in DATA["slides"]:
        out += [f"## {s['n']}. {s['title']}", "", f"**Key message:** {s['message']}", "",
                "**Visible text:**", *[f"- {t}" for t in visible_text(s)], ""]
        imgs = [s[k] for k in ("image", "image2") if s.get(k)]
        if imgs:
            out += ["**Screenshots:** " + ", ".join(f"`screenshots/{i}`" for i in imgs), ""]
        out += [f"**Speaker notes:** {s['notes']}", "", f"**Evidence source:** {s['source']}", "",
                "**Needs founder validation:** " + ("; ".join(s["validate"]) if s["validate"] else "none"), ""]
    (COMP / "PITCH_DECK.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


# ----------------------------------------------------------------------------------------------------- PowerPoint
def write_pptx() -> bool:
    try:
        from pptx import Presentation  # noqa: PLC0415 - optional dev dependency
        from pptx.dml.color import RGBColor  # noqa: PLC0415
        from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: PLC0415
        from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE  # noqa: PLC0415
        from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: PLC0415
        from pptx.util import Inches, Pt  # noqa: PLC0415
    except ImportError:
        print("python-pptx not installed: skipped the .pptx")
        return False
    from PIL import Image  # noqa: PLC0415 - python-pptx depends on Pillow

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]

    def rgb(h: str) -> RGBColor:
        return RGBColor.from_string(h)

    def box(slide, x, y, w, h, fill=PANEL, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, dash=False, radius=0.06):
        sh = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
        if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
            sh.adjustments[0] = radius
        if fill:
            sh.fill.solid()
            sh.fill.fore_color.rgb = rgb(fill)
        else:
            sh.fill.background()
        if line:
            sh.line.color.rgb = rgb(line)
            sh.line.width = Pt(1.75)
            if dash:
                sh.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        else:
            sh.line.fill.background()
        sh.shadow.inherit = False
        sh.text_frame.text = ""
        return sh

    def text(slide, x, y, w, h, value, size=18, color=TEXT, bold=False, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, font=FONT):
        tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        tf.margin_left = tf.margin_right = Inches(0.05)
        lines = value if isinstance(value, list) else [value]
        for i, line in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            run = p.add_run()
            run.text = line
            run.font.size, run.font.bold, run.font.name = Pt(size), bold, font
            run.font.color.rgb = rgb(color)
        return tb

    def label_in(sh, value, size=16, color=TEXT, bold=False, align=PP_ALIGN.CENTER):
        tf = sh.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        lines = value if isinstance(value, list) else [value]
        for i, line in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            run = p.add_run()
            run.text = line
            run.font.size, run.font.name = Pt(size if i == 0 else size - 3), FONT
            run.font.bold = bold if i == 0 else False
            run.font.color.rgb = rgb(color if i == 0 else MUTED)

    def placeholder(slide, x, y, w, h, value, size=14):
        sh = box(slide, x, y, w, h, fill=None, line=WARN, dash=True)
        label_in(sh, value, size=size, color=WARN, bold=True)
        return sh

    def image(slide, name, x, y, w=None, h=None, border=True):
        """Fit a screenshot into the (x, y, w, h) frame, keeping its aspect ratio."""
        path = SHOTS / name
        if not path.is_file():
            return placeholder(slide, x, y, w or 4, h or 3, f"[missing screenshot {name}]")
        iw, ih = Image.open(path).size
        if w and h:
            scale = min(w / iw, h / ih)
            dw, dh = iw * scale, ih * scale
            x, y = x + (w - dw) / 2, y + (h - dh) / 2
        elif w:
            dw, dh = w, w * ih / iw
        else:
            dw, dh = h * iw / ih, h
        if border:
            box(slide, x - 0.04, y - 0.04, dw + 0.08, dh + 0.08, fill="2A323D", radius=0.02)
        return slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(dw), Inches(dh))

    def arrow(slide, x1, y1, x2, y2, color=MUTED):
        c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
        c.line.color.rgb = rgb(color)
        c.line.width = Pt(2)
        line = c.line._get_or_add_ln()
        tail = line.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}tailEnd",
                                {"type": "triangle", "w": "med", "len": "med"})
        line.append(tail)

    def chip(slide, x, y, value, color=ACCENT, w=None, size=14):
        w = w or 0.45 + 0.125 * len(value)
        sh = box(slide, x, y, w, 0.42, fill=PANEL2, line=color, radius=0.5)
        label_in(sh, value, size=size, color=color, bold=True)
        return w

    def header(slide, s, msg_color=ACCENT):
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = rgb(BG)
        box(slide, 0, 0, 0.14, 7.5, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
        text(slide, 0.6, 0.35, 12.2, 0.8, s["title"], 34, bold=True)
        text(slide, 0.6, 1.08, 12.2, 0.6, s["message"], 18, color=msg_color)
        text(slide, 12.2, 7.02, 0.9, 0.35, f"{s['n']} / {len(DATA['slides'])}", 11, color=MUTED, align=PP_ALIGN.RIGHT)
        text(slide, 0.6, 7.02, 6, 0.35, "IntegrationRescue · prototype · simulated systems, fictional data", 11,
             color=MUTED)

    # -------------------------------------------------------------------------------------------- layouts
    def l_title(slide, s):
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = rgb(BG)
        box(slide, 0, 0, 0.14, 7.5, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
        text(slide, 0.7, 1.2, 6.4, 1.0, s["title"], 46, bold=True)
        text(slide, 0.7, 2.25, 6.0, 1.3, s["message"], 22, color=ACCENT)
        x = 0.7
        for i, c in enumerate(s["chips"]):
            if i == 2:
                x = 0.7
            x += chip(slide, x, 3.75 + (0.58 if i >= 2 else 0), c, color=OK if i == 3 else ACCENT) + 0.15
        f = DATA["founder"]
        text(slide, 0.7, 5.2, 6.2, 0.45, f["name"], 20, bold=True)
        text(slide, 0.7, 5.62, 6.2, 0.7, f["role"], 14, color=MUTED)
        placeholder(slide, 0.7, 6.3, 3.6, 0.45, PH["email"], size=12)
        text(slide, 4.45, 6.33, 3.0, 0.4, "Best Business AI Agent", 12, color=MUTED)
        # A drawn summary of the verifier's checks: readable at any size, unlike a shrunken screenshot.
        box(slide, 7.6, 1.45, 5.2, 4.6, fill=PANEL, line=OK)
        text(slide, 7.9, 1.65, 4.6, 0.45, "Independent verifier", 16, color=MUTED, bold=True)
        for i, check in enumerate(s["checks"]):
            y = 2.25 + i * 0.62
            text(slide, 7.9, y, 0.5, 0.5, "✓", 22, color=OK, bold=True)
            text(slide, 8.45, y + 0.04, 4.2, 0.5, check, 18)
        badge = box(slide, 8.6, 4.85, 3.2, 0.8, fill=PANEL2, line=OK, radius=0.5)
        label_in(badge, "VERIFIED", size=26, color=OK, bold=True)
        text(slide, 7.6, 6.15, 5.2, 0.4, "From a live Gemini run on fictional data", 12, color=MUTED,
             align=PP_ALIGN.CENTER)

    def l_incident(slide, s):
        header(slide, s)
        for i, (system, status, ok) in enumerate(s["cards"]):
            x = 0.6 + i * 3.1
            color = OK if ok else BAD
            card = box(slide, x, 2.2, 2.85, 2.9, fill=PANEL, line=color)
            card.text_frame.text = ""
            text(slide, x, 2.45, 2.85, 1.1, "✓" if ok else "✗", 60, color=color, bold=True, align=PP_ALIGN.CENTER)
            text(slide, x, 3.65, 2.85, 0.5, system, 20, bold=True, align=PP_ALIGN.CENTER)
            text(slide, x, 4.15, 2.85, 0.5, status, 17, color=color, align=PP_ALIGN.CENTER)
            if i < 3:
                arrow(slide, x + 2.88, 3.65, x + 3.08, 3.65)
        bar = box(slide, 0.6, 5.55, 12.1, 0.95, fill=PANEL2)
        label_in(bar, s["footer"], size=19)

    def l_who(slide, s):
        header(slide, s)
        for i, (who, pain) in enumerate(s["personas"]):
            x = 0.6 + i * 4.1
            box(slide, x, 2.0, 3.85, 2.75, fill=PANEL)
            box(slide, x + 1.4, 2.2, 1.05, 0.1, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
            text(slide, x + 0.2, 2.5, 3.45, 0.9, who, 20, bold=True, align=PP_ALIGN.CENTER)
            text(slide, x + 0.2, 3.45, 3.45, 1.1, pain, 16, color=MUTED, align=PP_ALIGN.CENTER)
        b = box(slide, 0.6, 5.0, 12.1, 0.7, fill=PANEL2, line=ACCENT)
        label_in(b, s["buyer"], size=17)
        st = box(slide, 0.6, 5.9, 12.1, 0.7, fill=None, line=WARN, dash=True)
        label_in(st, s["status"], size=16, color=WARN, bold=True)

    def l_gap(slide, s):
        header(slide, s)
        for i, (tool, stop) in enumerate(s["columns"]):
            x = 0.6 + i * 3.1
            box(slide, x, 2.0, 2.85, 2.6, fill=PANEL)
            text(slide, x + 0.15, 2.25, 2.55, 0.9, tool, 19, bold=True, align=PP_ALIGN.CENTER)
            text(slide, x + 0.15, 3.25, 2.55, 1.1, stop, 17, color=WARN, align=PP_ALIGN.CENTER)
        g = box(slide, 0.6, 4.95, 12.1, 0.95, fill=PANEL2, line=OK)
        label_in(g, s["footer"], size=21, color=OK, bold=True)
        text(slide, 0.6, 6.1, 12.1, 0.5, s["small"], 13, color=MUTED, align=PP_ALIGN.CENTER)

    def l_solution(slide, s):
        header(slide, s)
        y = 2.1
        for b in s["bullets"]:
            box(slide, 0.6, y, 0.12, 0.62, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
            text(slide, 0.9, y - 0.02, 3.5, 1.2, b, 17)
            y += 1.45
        image(slide, s["image"], 4.65, 1.85, w=8.3, h=5.0)

    def l_workflow(slide, s):
        header(slide, s)
        n = len(s["steps"])
        w = 1.78
        for i, step in enumerate(s["steps"]):
            x = 0.6 + i * (w + 0.29)
            special = step in ("Human approval", "Independent verify")
            sh = box(slide, x, 1.95, w, 0.95, fill=PANEL2 if special else PANEL, line=OK if special else ACCENT)
            label_in(sh, step, size=15, color=OK if special else TEXT, bold=True)
            if i < n - 1:
                arrow(slide, x + w + 0.02, 2.42, x + w + 0.27, 2.42)
        for col, (title, items, color) in enumerate((("The model decides", s["left"], ACCENT),
                                                     ("Code enforces", s["right"], OK))):
            x = 0.6 + col * 6.2
            box(slide, x, 3.25, 5.9, 3.45, fill=PANEL)
            text(slide, x + 0.3, 3.45, 5.3, 0.55, title, 22, color=color, bold=True)
            text(slide, x + 0.3, 4.1, 5.3, 2.5, [f"•  {i}" for i in items], 19)

    def l_demo(slide, s):
        header(slide, s)
        pic = image(slide, s["image"], 2.4, 1.8, w=8.5, h=3.75)
        dim = box(slide, pic.left / 914400, pic.top / 914400, pic.width / 914400, pic.height / 914400,
                  fill="000000", shape=MSO_SHAPE.RECTANGLE)
        from pptx.oxml.ns import qn  # noqa: PLC0415
        sf = dim.fill._xPr.find(qn("a:solidFill"))
        clr = sf[0]
        alpha = clr.makeelement(qn("a:alpha"), {"val": "55000"})
        clr.append(alpha)
        play = box(slide, 6.15, 3.15, 1.0, 1.0, fill=ACCENT, shape=MSO_SHAPE.OVAL)
        label_in(play, "▶", size=30)
        placeholder(slide, 2.4, 5.8, 5.6, 0.55, PH["video"], size=14)
        placeholder(slide, 8.2, 5.8, 2.7, 0.55, PH["date"], size=12)
        text(slide, 0.6, 6.5, 12.1, 0.4, "Embed the video here, or link it if the portal takes a separate upload.",
             12, color=MUTED, align=PP_ALIGN.CENTER)

    def l_architecture(slide, s):
        header(slide, s)
        nodes = {
            "ticket": (0.6, 2.6, 1.9, 0.9, "Ticket\n(untrusted)", MUTED),
            "agent": (3.0, 2.45, 2.4, 1.2, "Gemini agent\nchooses tools", ACCENT),
            "tools": (6.0, 2.45, 2.3, 1.2, "Typed, phase-gated\ntools (read-only)", ACCENT),
            "sims": (9.0, 2.05, 3.7, 2.0, "Simulated systems\nbilling · webhooks ·\nentitlements · logs", MUTED),
            "policy": (3.0, 4.35, 2.4, 1.0, "Patch policy\nallow-list, size", WARN),
            "sandbox": (6.0, 4.35, 2.3, 1.0, "Sandbox\ntests · regression · replay", WARN),
            "human": (9.0, 4.35, 1.7, 1.0, "Human\napproval", OK),
            "verifier": (11.0, 4.35, 1.7, 1.0, "Verifier\n(read-only)", OK),
        }
        for x, y, w, h, label, color in nodes.values():
            sh = box(slide, x, y, w, h, fill=PANEL, line=color)
            first, *rest = label.split("\n")
            label_in(sh, [first, *rest], size=15, color=color if color != MUTED else TEXT, bold=True)
        arrow(slide, 2.5, 3.05, 3.0, 3.05)
        arrow(slide, 5.4, 3.05, 6.0, 3.05)
        arrow(slide, 8.3, 3.05, 9.0, 3.05)
        arrow(slide, 4.2, 3.65, 4.2, 4.35)
        arrow(slide, 5.4, 4.85, 6.0, 4.85)
        arrow(slide, 8.3, 4.85, 9.0, 4.85)
        arrow(slide, 10.7, 4.85, 11.0, 4.85)
        arrow(slide, 11.85, 4.35, 11.85, 4.05)
        caption = ["Only the verifier can produce VERIFIED. It reads billing directly, never the agent's output.",
                   "Gemini today · Claude adapter (fake-client tested) · rule-based baseline for tests, never the AI"]
        text(slide, 0.6, 5.75, 12.1, 0.9, caption, 14, color=MUTED, align=PP_ALIGN.CENTER)

    def l_evidence(slide, s):
        header(slide, s)
        for i, (big, label, kind) in enumerate(s["tiles"]):
            col, row = i % 3, i // 3
            x, y = 0.6 + col * 4.1, 1.95 + row * 2.3
            color = OK if kind == "ok" else WARN
            box(slide, x, y, 3.85, 2.05, fill=PANEL, line=color)
            text(slide, x, y + 0.15, 3.85, 1.1, big, 54, color=color, bold=True, align=PP_ALIGN.CENTER)
            text(slide, x + 0.2, y + 1.28, 3.45, 0.7, label, 16, align=PP_ALIGN.CENTER)
        text(slide, 0.6, 6.55, 12.1, 0.45, s["footnote"], 12, color=MUTED, align=PP_ALIGN.CENTER)

    def l_safety(slide, s):
        header(slide, s)
        for i, b in enumerate(s["bullets"]):
            x, y = 0.6 + (i % 2) * 6.1, 1.85 + (i // 2) * 1.12
            box(slide, x, y, 5.95, 1.0, fill=PANEL)
            box(slide, x, y, 0.1, 1.0, fill=OK, shape=MSO_SHAPE.RECTANGLE)
            text(slide, x + 0.3, y + 0.05, 5.5, 0.9, b, 15, anchor=MSO_ANCHOR.MIDDLE)
        image(slide, s["image2"], 0.6, 4.2, w=12.1, h=2.45)
        text(slide, 0.6, 6.68, 12.1, 0.35, "Verifier result after human approval: live Gemini run, fictional data", 11,
             color=MUTED, align=PP_ALIGN.CENTER)

    def l_flywheel(slide, s):
        header(slide, s)
        cx, cy, r = 6.65, 4.15, 1.75
        pos = [(cx, cy - r), (cx + r * 1.9, cy), (cx, cy + r), (cx - r * 1.9, cy)]
        w, h = 3.1, 0.95
        for (x, y), label in zip(pos, s["nodes"], strict=True):
            sh = box(slide, x - w / 2, y - h / 2, w, h, fill=PANEL, line=ACCENT)
            label_in(sh, label, size=16, bold=True)
        for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
            (x1, y1), (x2, y2) = pos[a], pos[b]
            arrow(slide, x1 + (x2 - x1) * 0.38, y1 + (y2 - y1) * 0.38, x1 + (x2 - x1) * 0.62, y1 + (y2 - y1) * 0.62,
                  color=ACCENT)
        hub = box(slide, cx - 1.05, cy - 0.45, 2.1, 0.9, fill=PANEL2, line=OK, radius=0.5)
        label_in(hub, "Verified outcomes", size=15, color=OK, bold=True)
        text(slide, 0.6, 6.45, 12.1, 0.45, s["small"], 13, color=WARN, align=PP_ALIGN.CENTER)

    def l_business(slide, s):
        header(slide, s)
        for i, (name, desc) in enumerate(s["boxes"]):
            x = 0.6 + i * 4.1
            box(slide, x, 2.0, 3.85, 2.3, fill=PANEL, line=ACCENT)
            chip(slide, x + 0.2, 2.15, "HYPOTHESIS", color=WARN, size=11, w=1.45)
            text(slide, x + 0.2, 2.7, 3.45, 0.7, name, 21, bold=True, align=PP_ALIGN.CENTER)
            text(slide, x + 0.2, 3.35, 3.45, 0.8, desc, 15, color=MUTED, align=PP_ALIGN.CENTER)
        seg = box(slide, 0.6, 4.6, 12.1, 0.9, fill=None, line=WARN, dash=True)
        label_in(seg, s["segment"], size=16, color=TEXT)
        m = box(slide, 0.6, 5.7, 12.1, 0.8, fill=PANEL2)
        label_in(m, s["measured"], size=15, color=OK)

    def l_market(slide, s):
        header(slide, s)
        colors = [OK, OK, ACCENT, MUTED]
        for i, (place, role, what) in enumerate(s["stages"]):
            x = 0.6 + i * 3.1
            box(slide, x, 2.0, 2.8, 3.4, fill=PANEL, line=colors[i])
            text(slide, x, 2.2, 2.8, 0.8, place, 30, color=colors[i] if colors[i] != MUTED else TEXT, bold=True,
                 align=PP_ALIGN.CENTER)
            text(slide, x + 0.15, 3.1, 2.5, 0.8, role, 16, bold=True, align=PP_ALIGN.CENTER)
            text(slide, x + 0.15, 3.95, 2.5, 1.2, what, 14, color=MUTED, align=PP_ALIGN.CENTER)
            if i < 3:
                arrow(slide, x + 2.82, 3.7, x + 3.08, 3.7)
        text(slide, 0.6, 5.55, 12.1, 0.45, "Ahmad is based in Egypt. The UAE is a proposed early market through the "
                                           "championship network, subject to customer validation.", 14,
             align=PP_ALIGN.CENTER)
        st = box(slide, 0.6, 6.1, 12.1, 0.6, fill=None, line=WARN, dash=True)
        label_in(st, s["small"], size=14, color=WARN, bold=True)

    def l_roadmap(slide, s):
        header(slide, s)
        colors = [OK, ACCENT, MUTED]
        for i, (when, items) in enumerate(s["columns"]):
            x = 0.6 + i * 4.1
            box(slide, x, 2.1, 3.85, 3.9, fill=PANEL, line=colors[i])
            text(slide, x, 2.3, 3.85, 0.7, when, 30, color=colors[i] if colors[i] != MUTED else TEXT, bold=True,
                 align=PP_ALIGN.CENTER)
            text(slide, x + 0.3, 3.2, 3.3, 2.7, [f"•  {t}" for t in items], 19)
            if i < 2:
                arrow(slide, x + 3.87, 4.05, x + 4.08, 4.05)

    def l_close(slide, s):
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = rgb(BG)
        box(slide, 0, 0, 0.14, 7.5, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
        text(slide, 0.6, 0.45, 12.2, 0.9, s["title"], 40, bold=True)
        placeholder(slide, 0.6, 1.65, 2.3, 2.6, PH["photo"], size=12)
        f = DATA["founder"]
        text(slide, 3.15, 1.65, 5.6, 0.5, f["name"], 22, bold=True)
        text(slide, 3.15, 2.15, 5.6, 0.9, f["role"], 15, color=MUTED)
        text(slide, 3.15, 2.95, 5.6, 0.45, "Based in Egypt · creator of IntegrationRescue", 15, color=MUTED)
        ask = box(slide, 0.6, 4.55, 8.2, 1.35, fill=PANEL2, line=OK)
        label_in(ask, ["Seeking design partners", s["message"].replace("We're looking for design partners: ", "")],
                 size=19, color=OK, bold=True)
        placeholder(slide, 9.4, 1.65, 3.3, 3.0, PH["qr"], size=13)
        placeholder(slide, 9.4, 4.85, 3.3, 0.5, PH["url"], size=12)
        placeholder(slide, 9.4, 5.45, 3.3, 0.5, PH["email"], size=12)
        text(slide, 0.6, 6.15, 8.4, 0.45, s["repo"], 15, color=ACCENT)
        text(slide, 0.6, 6.6, 12.1, 0.45, "When software breaks between systems, IntegrationRescue fixes it, and "
                                          "proves it.", 15, color=MUTED)
        text(slide, 12.2, 7.02, 0.9, 0.35, f"{s['n']} / {len(DATA['slides'])}", 11, color=MUTED, align=PP_ALIGN.RIGHT)

    layouts = {"title": l_title, "incident": l_incident, "who": l_who, "gap": l_gap, "solution": l_solution,
               "workflow": l_workflow, "demo": l_demo, "architecture": l_architecture, "evidence": l_evidence,
               "safety": l_safety, "flywheel": l_flywheel, "business": l_business, "market": l_market,
               "roadmap": l_roadmap, "close": l_close}
    for s in DATA["slides"]:
        slide = prs.slides.add_slide(blank)
        layouts[s["layout"]](slide, s)
        slide.notes_slide.notes_text_frame.text = (
            f"{s['notes']}\n\nEvidence: {s['source']}\nValidate before use: " + ("; ".join(s["validate"]) or "none"))
    prs.core_properties.title = "IntegrationRescue"
    prs.core_properties.author = DATA["founder"]["name"]
    prs.save(COMP / "IntegrationRescue_Competition_Deck.pptx")
    return True


if __name__ == "__main__":
    write_markdown()
    built = write_pptx()
    print("wrote competition/PITCH_DECK.md" + (" and the .pptx" if built else ""))
