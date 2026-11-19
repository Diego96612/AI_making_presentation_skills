"""產生便利貼風格提案簡報模板（18 種版型）。用法：uv run --with python-pptx python build_sticky_note_template.py sticky-note-template.pptx"""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.oxml.ns import qn
from lxml import etree

FONT = "Noto Sans TC"
TOTAL = 18

# 配色
C = dict(
    title="5E6573", text="222222", sub="7A7F88", grey="8C8F96",
    orange="D9822B", red="E8423F", navy="1F3B5E", blue="3C5A80",
    bg_light="EEF0F4", white="FFFFFF", card="F1F2F6",
    yellow="FBE3B0", yellow2="FCEBA8", cream="FDF9DC", sage="C3D5CD", sage_dark="93B5A6",
    pink="FDE2DE", pink2="FADCE8", pink_line="D6739A", rose="D9A49B", rose_bg="FDF3EC",
    band="E4EAF3", tape="E3C88E", teal="19B5BA", gold="F0D995", paper="DCD5C6",
    arrow_y="F2DC9B", arrow_o="F2B233", purple="B9A6E0", line="5E7C99", green="DDE8CF",
)


def rgb(h):
    return RGBColor.from_string(h)


def set_font(run, size, color, bold=False):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = rgb(color)
    f.name = FONT
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rpr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rpr, qn(tag))
        el.set("typeface", FONT)


def tb(s, x, y, w, h, text, size=18, color=C["text"], bold=False, align="l",
       anchor="t", spacing=None):
    """文字方塊；text 可用 list 表示多段，每段可為 (文字, 大小, 顏色, 粗體)。"""
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    paras = text if isinstance(text, list) else (text.split("\n") if isinstance(text, str) else [text])
    for i, p in enumerate(paras):
        if isinstance(p, str):
            p = (p, size, color, bold)
        t, sz, col, bd = p
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
        if spacing:
            para.line_spacing = spacing
        r = para.add_run()
        r.text = t
        set_font(r, sz, col, bd)
    return box


def shape(s, kind, x, y, w, h, fill=None, line=None, lw=1.0, rot=0, shadow=False, dash=False):
    sh = s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill:
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(fill)
    else:
        sh.fill.background()
    if line:
        sh.line.color.rgb = rgb(line)
        sh.line.width = Pt(lw)
        if dash:
            from pptx.enum.dml import MSO_LINE
            sh.line.dash_style = MSO_LINE.DASH
    else:
        sh.line.fill.background()
    sh.rotation = rot
    if not shadow:
        # 關掉主題預設陰影
        sppr = sh._element.spPr
        etree.SubElement(sppr, qn("a:effectLst"))
    else:
        sppr = sh._element.spPr
        eff = etree.SubElement(sppr, qn("a:effectLst"))
        sd = etree.SubElement(eff, qn("a:outerShdw"), blurRad="50800", dist="38100",
                              dir="5400000", algn="t", rotWithShape="0")
        clr = etree.SubElement(sd, qn("a:srgbClr"), val="000000")
        etree.SubElement(clr, qn("a:alpha"), val="28000")
    return sh


def alpha(sh, pct):
    fill = sh._element.spPr.find(qn("a:solidFill"))
    clr = fill[0]
    etree.SubElement(clr, qn("a:alpha"), val=str(int(pct * 1000)))


def line(s, x1, y1, x2, y2, color, w=1.5, dash=False):
    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    ln.line.color.rgb = rgb(color)
    ln.line.width = Pt(w)
    if dash:
        from pptx.enum.dml import MSO_LINE
        ln.line.dash_style = MSO_LINE.ROUND_DOT
    return ln


def pin(s, cx, cy, color=C["red"], size=0.42):
    """圖釘：針＋圓頭。"""
    shape(s, MSO_SHAPE.ISOSCELES_TRIANGLE, cx + size * 0.05, cy + size * 0.55, size * 0.18, size * 0.5,
          fill="555555", rot=160)
    shape(s, MSO_SHAPE.OVAL, cx - size / 2, cy - size / 2, size, size, fill=color, line="555555", lw=1.5)


def tape(s, x, y, w=1.6, h=0.32, rot=-2, color=C["tape"]):
    t = shape(s, MSO_SHAPE.RECTANGLE, x, y, w, h, fill=color, rot=rot)
    alpha(t, 85)
    return t


def placeholder(s, x, y, w, h, text):
    box = shape(s, MSO_SHAPE.RECTANGLE, x, y, w, h, fill="F7F8FA", line="B8BEC8", lw=1.25, dash=True)
    tb(s, x, y, w, h, text, 16, C["grey"], align="c", anchor="m")
    return box


def bg(s, color):
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(color)


def title(s, text, red=None, y=0.25, size=44):
    paras = text
    box = s.shapes.add_textbox(Inches(0.55), Inches(y), Inches(10.5), Inches(1.0))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = paras
    set_font(r, size, C["title"], True)
    if red:
        r2 = p.add_run()
        r2.text = red
        set_font(r2, size - 6, C["red"], False)
    return box


def lead(s, text, color=C["orange"], y=1.25, size=28):
    return tb(s, 0.6, y, 11.5, 0.7, text, size, color)


def pageno(s, n):
    tb(s, 11.6, 7.05, 1.4, 0.3, f"{n} / {TOTAL}", 11, C["grey"], align="r")


def source(s, text):
    tb(s, 0.55, 7.0, 10.5, 0.35, text, 11, C["grey"])


def notes(s, text):
    s.notes_slide.notes_text_frame.text = text


def arrow_bullet(s, x, y, text, size=20, color=C["text"]):
    shape(s, MSO_SHAPE.CHEVRON, x, y + 0.08, 0.2, 0.24, fill=C["purple"])
    shape(s, MSO_SHAPE.CHEVRON, x + 0.14, y + 0.08, 0.2, 0.24, fill=C["purple"])
    tb(s, x + 0.45, y - 0.02, 3.4, 0.45, text, size, color)


# ---------------------------------------------------------------- 版型

def s01_cover(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["bg_light"])
    tb(s, 0.85, 0.6, 5, 0.4, "活動名稱｜階段名稱", 16, C["text"])
    tb(s, 0.65, 1.35, 5.6, 2.9, ["口號第一句、", "口號第二句、", "口號第三句"], 50, C["text"], True, spacing=1.05)
    tb(s, 0.7, 4.35, 5.5, 1.0, ["提案對象或場域名稱", "一句話說明提案主題"], 24, C["text"])
    line(s, 1.15, 5.8, 4.6, 5.8, C["line"], 3)
    tb(s, 0.6, 6.05, 6, 0.4, "提案人：學校 系所　姓名", 18, C["text"])
    tb(s, 0.6, 6.5, 6, 0.35, "（年月）", 14, C["text"])
    placeholder(s, 5.5, 1.05, 7.3, 5.45, "放主視覺圖\n（平面圖、產品照、示意圖）")
    notes(s, "封面：左邊放三句口號式主標題，右邊放一張最能代表提案的主視覺圖。")


def s02_summary(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "提案摘要：")
    tb(s, 0.65, 1.7, 12, 0.6, "用一句話說出這個提案要做什麼", 28, C["text"])
    tb(s, 0.65, 2.35, 12, 0.6, "再用一句話說明它分別幫誰解決了什麼。", 24, C["text"])
    for i, (h, b) in enumerate([("重點一", "一句話說明"), ("重點二", "一句話說明"), ("重點三", "一句話說明")]):
        x = 0.65 + i * 4.1
        shape(s, MSO_SHAPE.RECTANGLE, x, 4.0, 3.85, 2.65, fill=C["yellow"], line="555555", lw=2.25)
        pin(s, x + 1.92, 3.95)
        tb(s, x, 4.55, 3.85, 0.7, h, 32, C["orange"], align="c")
        tb(s, x, 5.3, 3.85, 0.55, b, 24, C["text"], align="c")
        tb(s, x, 5.95, 3.85, 0.45, "（補充說明，可刪）", 16, C["grey"], align="c")
    pageno(s, 2)
    notes(s, "提案摘要：三張便利貼對應簡報後面的三個主要章節。")


def s03_three_benefits(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "01. 章節標題")
    tb(s, 0.75, 1.3, 11, 0.6, "對方可以從這個提案得到：", 28, C["text"])
    for i in range(3):
        x = 0.45 + i * 4.3
        shape(s, MSO_SHAPE.FOLDED_CORNER, x, 2.25, 4.0, 4.6, fill=C["sage"])
        tape(s, x + 1.25, 2.1, 1.6, 0.34, rot=-1.5)
        for k in range(7):
            shape(s, MSO_SHAPE.OVAL, x + 0.4 + k * 0.5, 2.62, 0.17, 0.17, fill=C["white"])
        pin(s, x + 0.45, 3.45, color="3E63C9", size=0.36)
        tb(s, x + 0.75, 3.05, 3.2, 0.75, f"收穫{'一二三'[i]}", 32, C["red"])
        tb(s, x + 0.25, 4.15, 3.5, 1.0, ["說明這項收穫的內容，", "建議兩行以內。"], 18, C["text"], align="c")
        tb(s, x + 0.25, 5.45, 3.5, 0.45, "對應的目標或依據", 17, C["grey"], align="c")
    pageno(s, 3)
    notes(s, "三欄膠帶卡：適合列出對方（評審、合作方）能得到的三個好處。")


def s04_problem_solution(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "02. 問題與解方")
    tb(s, 0.5, 1.35, 9, 0.6, "核心問題：一句話寫出最根本的問題", 28, C["red"])
    for i in range(2):
        x = 0.75 + i * 4.05
        shape(s, MSO_SHAPE.RECTANGLE, x, 2.3, 3.55, 2.6, fill=C["pink"])
        line(s, x, 2.3, x + 3.55, 2.3, "555555", 2)
        line(s, x, 4.9, x + 3.55, 4.9, "555555", 2)
        tape(s, x + 1.0, 2.1, 1.45, 0.38, rot=0, color="FCEBC1")
        tb(s, x, 2.55, 3.55, 0.6, f"問題{'一二'[i]}", 28, C["sub"], align="c")
        tb(s, x, 3.2, 3.55, 0.55, "問題名稱", 24, C["text"], align="c")
        tb(s, x, 4.05, 3.55, 0.5, "一句話描述問題", 15, C["text"], align="c")
        shape(s, MSO_SHAPE.ISOSCELES_TRIANGLE, x + 1.62, 5.0, 0.3, 0.2, fill="7A8796", rot=180)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 0.25, 5.3, 3.05, 1.65, fill=C["pink2"], line=C["pink_line"], lw=2, shadow=True)
        tb(s, x + 0.25, 5.45, 3.05, 1.4, ["解法", "一句話寫出解法"], 22, C["text"], align="c", anchor="m")
    placeholder(s, 9.35, 0.5, 3.4, 2.9, "放圖示\n（代表問題）")
    placeholder(s, 9.35, 3.75, 3.4, 3.1, "放圖示\n（代表對象）")
    pageno(s, 4)
    notes(s, "問題與解方總覽：上面是問題，箭頭往下接對應的解法。之後各用一頁展開。")


def s05_funnel(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "02. 問題與解方", red="（問題一）")
    tb(s, 0.5, 1.35, 9, 0.6, "用一個問句點出問題？", 28, C["red"])
    shape(s, MSO_SHAPE.RECTANGLE, 9.75, 0.3, 3.3, 1.75, fill=C["white"], line="222222", lw=1.5)
    tb(s, 9.85, 0.5, 3.1, 1.4, ["推測：", "根據數據推出的一句話結論"], 18, C["blue"], align="c")
    colors = [C["navy"], "3B6495", "5D86B5", C["orange"]]
    labels = ["階段一", "階段二", "階段三", "階段四"]
    for i in range(4):
        y = 2.4 + i * 1.12
        top = 5.8 - i * 1.0
        x = 0.65 + i * 0.5
        sh = shape(s, MSO_SHAPE.TRAPEZOID, x, y, top, 0.98, fill=colors[i], rot=180)
        sh.adjustments[0] = 0.5
        tb(s, x, y, top, 0.98, labels[i], 22, C["white"], align="c", anchor="m")
        ry = y
        tb(s, 7.05, ry, 1.7, 0.6, "00%", 34, C["orange"] if i == 3 else C["text"])
        tb(s, 8.75, ry + 0.05, 3.7, 0.5, "這個數字代表什麼", 18, C["text"], align="c")
        tb(s, 8.75, ry + 0.6, 3.75, 0.35, "資料來源，年份", 12, C["grey"], align="r")
        line(s, 7.0, ry + 1.03, 12.5, ry + 1.03, "D0D4DA", 1)
    source(s, "資料來源：來源一（日期）；來源二（日期）")
    pageno(s, 5)
    notes(s, "漏斗：用 3～5 個階段說明人數或比例如何一路流失，最後一階用強調色。")


def s06_compare(prs, n, red_tag):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "02. 問題與解方", red=red_tag)
    shape(s, MSO_SHAPE.RECTANGLE, 0.4, 1.45, 12.3, 0.8, fill=C["band"])
    tb(s, 0.55, 1.5, 12, 0.7, "解方：一句話寫出這個解方", 30, C["red"], anchor="m")
    labels = [("目前做法：", "目前做法的問題："), ("我們提出的解方：", "能如何解決問題：")]
    for r in range(2):
        y = 2.55 + r * 2.15
        tb(s, 1.2, y, 4, 0.5, labels[r][0], 22, C["blue"])
        tb(s, 8.7, y, 4, 0.5, labels[r][1], 22, C["blue"])
        for c in range(2):
            x = 1.1 if c == 0 else 8.5
            shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y + 0.5, 3.55, 1.5, fill=C["rose_bg"], line=C["rose"], lw=3)
            if c == 0:
                tb(s, x + 0.2, y + 0.55, 3.2, 1.4, [("做法名稱", 22, C["orange"], False),
                                                     ("一到兩行說明這個做法。", 16, C["text"], False)])
            else:
                tb(s, x + 0.2, y + 0.55, 3.2, 1.4, "一到兩行說明。", 16, C["text"], anchor="m")
        shape(s, MSO_SHAPE.RIGHT_ARROW, 5.3, y + 0.75, 2.55, 1.05, fill=C["arrow_y"])
    pageno(s, n)
    notes(s, "現況與解方對照：上排是目前做法與它的問題，下排是你的解方與它如何解決。")


def s07_bignum(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "02. 問題與解方", red="（問題二）")
    tb(s, 0.65, 1.35, 9, 0.6, "用一個問句點出問題？", 28, C["red"])
    shape(s, MSO_SHAPE.RECTANGLE, 0.95, 2.6, 5.4, 4.3, fill="FBEDE6", line="222222", lw=2.25)
    shape(s, MSO_SHAPE.RECTANGLE, 1.15, 2.85, 5.0, 3.85, line="D88FD8", lw=1.25)
    for k in range(5):
        shape(s, MSO_SHAPE.DONUT, 1.7 + k * 0.82, 2.25, 0.45, 0.65, fill="A9A9A9", line="333333", lw=1)
    tb(s, 1.15, 3.0, 5.0, 0.6, "對象", 30, C["text"], align="c")
    tb(s, 1.15, 3.7, 5.0, 1.3, "00%", 72, C["orange"], align="c")
    tb(s, 1.3, 5.35, 4.8, 0.5, "這個數字代表什麼", 20, C["red"])
    tb(s, 1.3, 6.25, 4.75, 0.35, "資料來源，年份", 13, C["grey"], align="r")
    for k, y in enumerate([2.25, 4.75]):
        p = shape(s, MSO_SHAPE.RECTANGLE, 6.45, y, 6.2, 2.2, fill=C["paper"], rot=0.6)
        tb(s, 6.75, y + 0.2, 5.6, 0.5, f"觀點{'一二'[k]}", 20, C["text"])
        tb(s, 6.75, y + 0.8, 5.6, 0.9, "用兩行以內寫出這個角度看到的問題，可以引用調查或報告。", 18, C["text"])
        tb(s, 6.75, y + 1.7, 5.6, 0.35, "資料來源", 13, C["grey"], align="r")
    source(s, "資料來源：來源一（日期）；來源二；來源三")
    pageno(s, 7)
    notes(s, "大數字＋紙條：左邊一個最有力的數字，右邊兩個不同角度的佐證。")


def s08_give_get(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "03. 使用者與利益")
    tb(s, 0.6, 1.3, 12, 0.6, "一句話說明這些使用者和你的關係：", 30, C["text"])
    for i in range(2):
        x = 0.6 + i * 4.55
        shape(s, MSO_SHAPE.RECTANGLE, x + 0.05, 2.35, 4.0, 4.6, fill="C7C9CF")
        shape(s, MSO_SHAPE.RECTANGLE, x, 2.25, 4.0, 4.55, fill=C["yellow2"])
        pin(s, x + 3.6, 2.45)
        tb(s, x + 0.2, 2.35, 3.3, 0.4, "和你的關係（例如：租戶）", 14, C["text"], align="c")
        tb(s, x + 0.4, 2.85, 3.5, 0.6, f"使用者{'一二'[i]}", 30, C["red"])
        tb(s, x + 0.4, 3.55, 3, 0.4, "付出：", 20, C["sub"])
        arrow_bullet(s, x + 0.5, 4.0, "付出的東西", 20)
        tb(s, x + 0.4, 4.6, 3, 0.4, "得到：", 20, C["orange"])
        for k in range(3):
            arrow_bullet(s, x + 0.5, 5.05 + k * 0.45, f"得到的好處 {k + 1}", 18)
    placeholder(s, 9.75, 2.25, 3.2, 4.55, "放插圖\n（使用情境）")
    pageno(s, 8)
    notes(s, "付出／得到便利貼：每種使用者一張，說明他付出什麼、得到什麼。")


def s09_stakeholders(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "03. 使用者與利益")
    lead(s, "各方關係人：各自想得到什麼，你提供什麼？")
    heads = ["關係人", "有哪些", "想得到什麼", "你提供什麼"]
    xs = [1.0, 2.35, 5.95, 9.3]
    for h, x in zip(heads, xs):
        tb(s, x, 2.35, 3.3, 0.5, h, 20, C["blue"])
    line(s, 0.95, 2.95, 12.45, 2.95, "2E3C4F", 2)
    shape(s, MSO_SHAPE.RECTANGLE, 2.05, 2.25, 0.08, 4.8, fill="7A6E6A")
    for r in range(4):
        y = 3.05 + r * 1.0
        tb(s, 1.0, y, 1.0, 0.8, f"第{'一二三四'[r]}端", 17, C["red"], anchor="m")
        tb(s, 2.35, y, 3.4, 0.8, "列出這一端有哪些對象", 16, C["text"], anchor="m")
        tb(s, 5.95, y, 3.2, 0.8, "他們想要的東西", 16, C["text"], anchor="m")
        tb(s, 9.3, y, 3.2, 0.8, "你能提供的東西", 16, C["text"], anchor="m")
        line(s, 0.95, y + 0.97, 12.45, y + 0.97, "C8CCD2", 1)
    pageno(s, 9)
    notes(s, "關係人表：適合 3～5 類關係人，逐列對照需求與你的提供。")


def s10_journey(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "03. 使用者與利益")
    tb(s, 9.6, 0.45, 3.2, 0.4, "假設前提：一句話", 15, C["text"], align="r")
    lead(s, "不同對象的使用歷程，以及每一步的收穫", y=1.35)
    for r in range(3):
        y = 2.55 + r * 1.5
        tb(s, 0.3, y, 2.3, 0.95, f"對象{'甲乙丙'[r]}得到", 25, C["red"], anchor="m")
        for c in range(3):
            x = 2.65 + c * 3.75
            shape(s, MSO_SHAPE.RECTANGLE, x, y, 2.4, 0.95, fill="F4F0E8", line="D8D2C6", lw=0.75, shadow=True)
            for k in range(3):
                shape(s, MSO_SHAPE.OVAL, x + 0.1, y + 0.15 + k * 0.28, 0.08, 0.08, fill=C["white"], line="CFC8BB", lw=0.5)
            tb(s, x + 0.2, y, 2.15, 0.95, f"步驟{c + 1}", 22, C["text"], align="c", anchor="m")
            if c < 2:
                shape(s, MSO_SHAPE.RIGHT_ARROW, x + 2.6, y + 0.15, 1.0, 0.65, fill=C["arrow_o"], line="E39A1E", lw=1.5)
    pageno(s, 10)
    notes(s, "三列歷程：每列一種對象，從左到右寫出三個步驟或收穫。")


def s11_image_list(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "04. 章節標題")
    lead(s, "一句話說明這張圖的重點", y=1.3, size=30)
    placeholder(s, 0.35, 2.3, 6.4, 4.65, "放圖片\n（平面圖、架構圖、截圖）")
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 7.0, 2.3, 6.0, 4.65, fill="FAF0E0")
    tape(s, 9.3, 2.05, 1.4, 0.32, rot=0, color="F06CA8")
    for k in range(3):
        y = 2.75 + k * 1.4
        shape(s, MSO_SHAPE.STAR_5_POINT, 7.35, y + 0.05, 0.42, 0.42, fill="2F6E7E")
        tb(s, 7.9, y - 0.03, 4.8, 0.5, f"項目{'一二三'[k]}", 22, C["text"])
        tb(s, 8.15, y + 0.5, 4.7, 0.45, "▷ 一句話說明", 20, C["text"])
    pageno(s, 11)
    notes(s, "圖片＋說明清單：左邊放圖，右邊解釋圖上最重要的三個區塊。")


def s12_three_cards(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "05. 章節標題")
    lead(s, "一句話說明策略方向", y=1.35, size=32)
    for i in range(3):
        x = 0.6 + i * 4.1
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, 2.3, 3.9, 4.0, fill=C["card"]).adjustments[0] = 0.08
        pin(s, x + 0.45, 2.85, color="C9D3E0", size=0.32)
        tb(s, x + 0.8, 2.6, 3, 0.6, f"類別{'一二三'[i]}", 26, C["orange"])
        arrow_bullet(s, x + 0.45, 3.5, "目標對象", 18)
        pin(s, x + 0.45, 4.55, color="C9D3E0", size=0.32)
        tb(s, x + 0.8, 4.35, 3, 0.45, "誘因", 18, C["sub"])
        arrow_bullet(s, x + 0.45, 5.15, "吸引他們的原因", 18)
    source(s, "補充說明：例如「以上為類型，不是名單」。")
    pageno(s, 12)
    notes(s, "三欄灰卡：三種目標類別，各寫對象與誘因。")


def s13_hub_list(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "06. 章節標題")
    tb(s, 1.1, 1.35, 10, 0.6, "一句話說明運作方式", 30, C["red"])
    shape(s, MSO_SHAPE.OVAL, 0.7, 2.6, 3.9, 4.1, fill=C["gold"])
    tb(s, 0.7, 2.6, 3.9, 4.1, ["核心單位", "名稱"], 28, C["text"], align="c", anchor="m")
    for k in range(5):
        y = 2.4 + k * 0.88
        if k < 4:
            shape(s, MSO_SHAPE.OVAL, 5.2, y, 0.62, 0.62, fill=C["teal"], shadow=True)
        else:
            shape(s, MSO_SHAPE.STAR_5_POINT, 5.15, y - 0.05, 0.72, 0.72, fill="F08A6E")
        tb(s, 6.0, y, 7, 0.62, f"工作項目{k + 1}－一句話說明", 24, C["text"], anchor="m")
    pageno(s, 13)
    notes(s, "中心＋清單：左邊是負責的核心單位，右邊列出它負責的 4～5 件事，最後一項用星號強調。")


def s14_esg(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "07. 章節標題")
    lead(s, "一句話說明三個面向", y=1.3, size=32)
    for i, (L, name) in enumerate([("A", "面向一"), ("B", "面向二"), ("C", "面向三")]):
        x = 0.6 + i * 4.1
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, 2.25, 3.9, 4.6, fill=C["card"]).adjustments[0] = 0.08
        tb(s, x, 2.55, 3.9, 1.2, (L, 66, C["red"], True), align="c")
        tb(s, x, 3.8, 3.9, 0.8, name, 40, "1E3354", align="c")
        tb(s, x + 0.3, 4.75, 3.3, 1.6, "用兩到三行說明具體做法", 22, "1E3354", align="c")
    pageno(s, 14)
    notes(s, "三面向大字母：適合 ESG、三大支柱等可以用一個字母或關鍵字代表的內容。")


def s15_indicators(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "08. 章節標題", red="（副標）")
    for k, (h, body) in enumerate([("（一）指標類別", ["一句話定義這個指標，", "可以再細分成哪幾類。"]),
                                     ("（三）指標類別", ["A. 指標項目", "B. 指標項目", "C. 指標項目"])]):
        y = 1.6 + k * 2.9
        shape(s, MSO_SHAPE.FOLDED_CORNER, 0.75, y, 5.8, 2.55, fill="F8E2A6", shadow=True)
        for d in range(4):
            shape(s, MSO_SHAPE.OVAL, 1.0, y + 0.35 + d * 0.55, 0.28, 0.28, fill=C["white"])
        pin(s, 3.6, y - 0.05, color="E06A63", size=0.45)
        tb(s, 1.5, y + 0.4, 4.8, 0.6, h, 28, C["red"])
        tb(s, 1.9, y + 1.0, 4.6, 1.4, body, 19, C["text"])
    shape(s, MSO_SHAPE.FOLDED_CORNER, 7.2, 1.5, 5.75, 5.65, fill="FCF3A0", rot=1, shadow=True)
    tb(s, 7.6, 1.9, 5, 0.6, "（二）指標類別", 28, C["red"])
    tb(s, 7.5, 2.65, 5.2, 0.45, "列出這類指標包含的面向", 20, C["text"], align="c")
    line(s, 7.6, 3.2, 12.6, 3.2, "222222", 2.5, dash=True)
    items = [("A. ", "對象一", "：指標內容。"), ("B. ", "對象二", "：指標內容。"),
             ("C. ", "對象三", "：指標內容。"), ("D. ", "對象四", "：指標內容。")]
    for k, (a, b, c) in enumerate(items):
        box = tb(s, 7.55, 3.35 + k * 0.85, 5.3, 0.8, a, 19, C["text"])
        p = box.text_frame.paragraphs[0]
        r = p.add_run(); r.text = b; set_font(r, 19, C["blue"])
        r = p.add_run(); r.text = c; set_font(r, 19, C["text"])
    pageno(s, 15)
    notes(s, "指標便利貼：左邊兩張放主要指標與門檻指標，右邊大張放分項指標。")


def s16_timeline(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "09. 短、中、長期目標")
    lead(s, "第一年做到什麼，第二年做到什麼，第三年做到什麼", y=1.2, size=28)
    dots = ["F48AB0", "F59A9A", "F7B9A0"]
    for i, h in enumerate(["短期目標", "中期目標", "長期目標"]):
        x = 0.45 + i * 4.35
        shape(s, MSO_SHAPE.RECTANGLE, x, 2.55, 3.75, 3.75, fill=C["cream"], line="E3DFC8", lw=0.75, shadow=True)
        tp = shape(s, MSO_SHAPE.OVAL, x + 1.42, 2.1, 0.92, 0.85, fill="B8AA99")
        tb(s, x, 2.95, 3.75, 0.6, h, 28, C["title"], True, align="c")
        for k in range(3):
            shape(s, MSO_SHAPE.OVAL, x + 0.3, 3.85 + k * 0.52, 0.24, 0.24, fill=dots[k])
            tb(s, x + 0.65, 3.73 + k * 0.52, 3.0, 0.45, "具體目標", 20, C["sub"])
    pageno(s, 16)
    notes(s, "三階段目標：每張 2～3 點，寫成可以檢驗的目標。")


def s17_finance(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["white"])
    title(s, "10. 成果與預期效益")
    lead(s, "一句話說明這頁的數字", y=1.35, size=30)
    rows, cols = 5, 5
    tbl = s.shapes.add_table(rows, cols, Inches(0.45), Inches(2.6), Inches(6.2), Inches(2.0)).table
    data = [["項目", "第一年", "第二年", "第三年", "合計"]] + [[f"收入項目{r}", "0", "0", "0", "0"] for r in range(1, 4)] + \
           [["總收入", "0", "0", "0", "0"]]
    for r in range(rows):
        for c in range(cols):
            cell = tbl.cell(r, c)
            cell.text = data[r][c]
            cell.fill.solid(); cell.fill.fore_color.rgb = rgb("F3F4F6" if r == 0 else "FFFFFF")
            for p in cell.text_frame.paragraphs:
                for run in p.runs:
                    set_font(run, 11, C["text"], r in (0, rows - 1))
    tbl2 = s.shapes.add_table(4, 5, Inches(0.45), Inches(4.85), Inches(6.2), Inches(1.6)).table
    data2 = [["項目", "第一年", "第二年", "第三年", "合計"], ["成本項目1", "0", "0", "0", "0"],
             ["成本項目2", "0", "0", "0", "0"], ["總成本", "0", "0", "0", "0"]]
    for r in range(4):
        for c in range(5):
            cell = tbl2.cell(r, c)
            cell.text = data2[r][c]
            cell.fill.solid(); cell.fill.fore_color.rgb = rgb("F3F4F6" if r == 0 else "FFFFFF")
            for p in cell.text_frame.paragraphs:
                for run in p.runs:
                    set_font(run, 11, C["text"], r in (0, 3))
    cd = CategoryChartData()
    cd.categories = ["第一年", "第二年", "第三年"]
    cd.add_series("總收入", (1400, 1650, 1750))
    cd.add_series("成本", (400, 480, 490))
    gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(6.9), Inches(3.0), Inches(6.1), Inches(4.0), cd)
    ch = gf.chart
    ch.has_title = True
    ch.chart_title.text_frame.text = "圖表標題（單位）"
    set_font(ch.chart_title.text_frame.paragraphs[0].runs[0], 16, C["text"])
    ch.has_legend = True
    ch.legend.position = XL_LEGEND_POSITION.TOP
    ch.legend.include_in_layout = False
    ch.legend.font.size = Pt(12)
    for ser, col in zip(ch.series, ["234E8C", "A6A6A6"]):
        ser.format.fill.solid(); ser.format.fill.fore_color.rgb = rgb(col)
    pl = ch.plots[0]
    pl.has_data_labels = True
    pl.data_labels.font.size = Pt(12)
    pl.gap_width = 60
    ch.value_axis.has_major_gridlines = True
    ch.value_axis.major_gridlines.format.line.color.rgb = rgb("E3E5E8")
    ch.value_axis.tick_labels.font.size = Pt(11)
    ch.category_axis.tick_labels.font.size = Pt(13)
    shape(s, MSO_SHAPE.RECTANGLE, 9.75, 0.35, 3.3, 2.6, fill=C["green"], line="B9CDA3", lw=2)
    tape(s, 11.9, 0.2, 1.4, 0.32, rot=35, color="4E7F8C")
    tb(s, 9.95, 0.5, 3, 0.5, "三年累計可獲得", 22, C["text"])
    for k in range(3):
        pin(s, 10.15, 1.25 + k * 0.52, color="B0103A", size=0.24)
        tb(s, 10.4, 1.0 + k * 0.52, 2.6, 0.5, f"效益重點{k + 1}", 22, C["text"])
    pageno(s, 17)
    notes(s, "效益：左邊收入與成本表，右邊長條圖（在 PowerPoint 按右鍵「編輯資料」改數字），右上便利貼寫結論。")


def s18_conclusion(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, C["bg_light"])
    tb(s, 0.7, 0.45, 4, 0.8, "結論", 44, C["title"], True)
    tb(s, 0.75, 1.5, 9.5, 1.9, ["一句話寫出最重要的成果數字", "再一句話寫出長期價值"], 40, C["text"], spacing=1.1)
    placeholder(s, 0.9, 3.7, 2.4, 2.3, "放圖示")
    for k, hgt in enumerate([1.45, 1.6, 2.15, 2.9]):
        shape(s, MSO_SHAPE.RECTANGLE, 7.15 + k * 1.5, 6.05 - hgt, 0.95, hgt, fill="000000")
    shape(s, MSO_SHAPE.RIGHT_ARROW, 7.4, 1.95, 5.9, 0.7, fill="000000", rot=-27)
    line(s, 0.8, 6.05, 12.6, 6.05, C["line"], 1.5)
    tb(s, 0.8, 6.2, 7, 0.45, "提案人｜學校 系所 年級　姓名", 18, C["text"])
    tb(s, 8.6, 6.2, 4, 0.45, "活動名稱｜階段名稱", 16, C["text"], align="r")
    tb(s, 0.8, 6.75, 11, 0.6, ["計算方法：貼上連結", "參考資料：貼上連結"], 9, C["text"])
    notes(s, "結論：用兩句話收尾，第一句放最重要的數字，第二句放長期價值。下面附計算方法與參考資料連結。")


def main(out):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    s01_cover(prs); s02_summary(prs); s03_three_benefits(prs); s04_problem_solution(prs)
    s05_funnel(prs); s06_compare(prs, 6, "（解方）"); s07_bignum(prs); s08_give_get(prs)
    s09_stakeholders(prs); s10_journey(prs); s11_image_list(prs); s12_three_cards(prs)
    s13_hub_list(prs); s14_esg(prs); s15_indicators(prs); s16_timeline(prs)
    s17_finance(prs); s18_conclusion(prs)
    prs.save(out)
    print("slides:", len(prs.slides), "->", out)


if __name__ == "__main__":
    main(sys.argv[1])
