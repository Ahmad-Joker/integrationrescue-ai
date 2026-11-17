"""Build the competition deck from competition/deck_data.json.

    .venv/Scripts/python -m pip install python-pptx     # dev tool only; not a runtime dependency
    .venv/Scripts/python scripts/build_deck.py

Writes competition/PITCH_DECK.md (always) and competition/IntegrationRescue_Competition_Deck.pptx (when python-pptx
is installed). The .pptx is a clean, text-first draft meant to be polished in PowerPoint or Canva; visuals listed per
slide are placeholders to add there.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMP = ROOT / "competition"
DATA = json.loads((COMP / "deck_data.json").read_text(encoding="utf-8"))

BG, PANEL, TEXT, MUTED, ACCENT, OK, WARN = "0E1116", "151A21", "E6E9EE", "9099A6", "5B8DEF", "3FB37F", "E0A23B"


def write_markdown() -> None:
    out = ["# Pitch deck specification (15 slides)", "",
           f"Generated from `competition/deck_data.json` by `scripts/build_deck.py` ({DATA['updated']}). "
           "Edit the JSON, not this file. Every figure must match [TECHNICAL_EVIDENCE.md](TECHNICAL_EVIDENCE.md).", "",
           "Design: dark background, one message per slide, at most 4 short bullets, large numbers for evidence. The "
           "demo video is embedded on slide 7 (or linked, if the portal needs a separate upload). Draft file: "
           "`IntegrationRescue_Competition_Deck.pptx`.", ""]
    for s in DATA["slides"]:
        out += [f"## {s['n']}. {s['title']}", "", f"**Key message:** {s['message']}", "",
                "**Visible text (maximum):**", *[f"- {b}" for b in s["bullets"]], "",
                f"**Visual:** {s['visual']}", "", f"**Speaker notes:** {s['notes']}", "",
                f"**Evidence source:** {s['source']}", "",
                "**Needs founder validation:** " + ("; ".join(s["validate"]) if s["validate"] else "none"), ""]
    (COMP / "PITCH_DECK.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


def write_pptx() -> bool:
    try:
        from pptx import Presentation  # noqa: PLC0415 - optional dev dependency
        from pptx.dml.color import RGBColor  # noqa: PLC0415
        from pptx.util import Inches, Pt  # noqa: PLC0415
    except ImportError:
        print("python-pptx not installed: skipped the .pptx")
        return False

    def rgb(h: str) -> RGBColor:
        return RGBColor.from_string(h)

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]

    def text(slide, x, y, w, h, value, size, color=TEXT, bold=False):
        box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = value
        run.font.size, run.font.bold, run.font.color.rgb, run.font.name = Pt(size), bold, rgb(color), "Segoe UI"
        return tf

    for s in DATA["slides"]:
        slide = prs.slides.add_slide(blank)
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = rgb(BG)
        bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.18), prs.slide_height)
        bar.fill.solid()
        bar.fill.fore_color.rgb = rgb(ACCENT)
        bar.line.fill.background()
        hero = s["n"] in (1, 15)
        text(slide, 0.8, 1.6 if hero else 0.6, 11.8, 1.2, s["title"], 54 if hero else 36, bold=True)
        text(slide, 0.8, 2.9 if hero else 1.55, 11.8, 1.0, s["message"], 24 if hero else 20, color=ACCENT)
        top = 4.2 if hero else 2.75
        height = Inches(0.62 * len(s["bullets"]) + 0.4)
        panel = slide.shapes.add_shape(1, Inches(0.8), Inches(top), Inches(11.7), height)
        panel.fill.solid()
        panel.fill.fore_color.rgb = rgb(PANEL)
        panel.line.fill.background()
        tf = text(slide, 1.1, top + 0.2, 11.2, 0.6 * len(s["bullets"]), "", 20)
        for i, b in enumerate(s["bullets"]):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            run = p.add_run()
            run.text = ("" if hero else "•  ") + b
            warn = b.startswith("Code repair") or "not yet" in b
            run.font.size, run.font.name = Pt(20), "Segoe UI"
            run.font.color.rgb = rgb(WARN if warn else TEXT)
            p.space_after = Pt(10)
        text(slide, 0.8, 6.75, 9.5, 0.4, f"Visual to add: {s['visual']}", 11, color=MUTED)
        text(slide, 11.3, 6.75, 1.5, 0.4, f"{s['n']} / {len(DATA['slides'])}", 11, color=MUTED)
        notes = slide.notes_slide.notes_text_frame
        notes.text = (f"{s['notes']}\n\nEvidence: {s['source']}\nValidate before use: "
                      + ("; ".join(s["validate"]) or "none"))
    prs.save(COMP / "IntegrationRescue_Competition_Deck.pptx")
    return True


if __name__ == "__main__":
    write_markdown()
    built = write_pptx()
    print("wrote competition/PITCH_DECK.md" + (" and the .pptx" if built else ""))
