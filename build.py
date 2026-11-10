#!/usr/bin/env python3
"""Dựng index.html từ các file Markdown trong content/.

Chạy:  python3 build.py
Không cần cài thêm thư viện nào.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
UPDATED = "10/11/2026"

TABS = [
    ("tong-quan", "Tổng quan", "00-tong-quan.md"),
    ("dieu-kien", "Điều kiện", "01-dieu-kien.md"),
    ("ho-so", "Hồ sơ", "02-ho-so.md"),
    ("bieu-mau", "Biểu mẫu", "03-bieu-mau.md"),
    ("quy-trinh", "Quy trình · Vay · Bán lại", "04-quy-trinh.md"),
    ("hud", "HUD Thủ Đức", "10-hud-thu-duc.md"),
]

LINKS = {
    "./kien-thuc-noxh.md": "#tong-quan",
    "./kien-thuc-noxh-01-dieu-kien.md": "#dieu-kien",
    "./kien-thuc-noxh-02-ho-so-theo-doi-tuong.md": "#ho-so",
    "./kien-thuc-noxh-03-bieu-mau-va-luu-y.md": "#bieu-mau",
    "./kien-thuc-noxh-04-quy-trinh-vay-ban-lai.md": "#quy-trinh",
    "./du-an-noxh.md": "#hud",
    "./du-an-noxh-hud-thu-duc.md": "#hud",
}

FORMS = [
    ("mau-01-don-dang-ky-mua.pdf", "Mẫu 01 — Đơn đăng ký mua nhà ở xã hội"),
    ("mau-01a-xac-nhan-doi-tuong-thu-nhap.pdf", "Mẫu 01a — Xác nhận đối tượng và thu nhập (có hợp đồng lao động, công chức, viên chức, hưu trí)"),
    ("mau-05-khong-co-hop-dong-lao-dong.pdf", "Mẫu 05 — Xác nhận đối tượng và thu nhập (không có hợp đồng lao động)"),
    ("mau-04-thu-nhap-luc-luong-vu-trang.pdf", "Mẫu 04 — Xác nhận thu nhập của lực lượng vũ trang"),
    ("mau-02-xac-nhan-chua-co-nha.pdf", "Mẫu 02 — Xác nhận chưa có nhà ở"),
    ("mau-03-nha-duoi-15m2.pdf", "Mẫu 03 — Xác nhận có nhà dưới 15 m² sàn/người"),
    ("mau-14-phieu-yeu-cau-thong-tin-dat-dai.pdf", "Mẫu 14 — Phiếu yêu cầu cung cấp thông tin, dữ liệu đất đai"),
    ("mau-noca-bo-cong-an.pdf", "Mẫu NOCA — Xác nhận đối tượng thuộc Bộ Công an"),
    ("mau-bo-quoc-phong.pdf", "Mẫu Bộ Quốc phòng — Xác nhận đối tượng (Thông tư 94/2024/TT-BQP)"),
]


def slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text).lower()
    table = str.maketrans(
        "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ",
        "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd",
    )
    text = text.translate(table)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:60]


def inline(text: str) -> str:
    codes = []

    def stash(m):
        codes.append(html.escape(m.group(1)))
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)

    def link(m):
        label, url = m.group(1), m.group(2)
        url = LINKS.get(url, url)
        ext = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
        return f'<a href="{url}"{ext}>{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(
        r'(?<!["=>])\b(https?://[^\s<*]+[^\s<*.,;:)])',
        lambda m: f'<a href="{m.group(1)}" target="_blank" rel="noopener">{short_url(m.group(1))}</a>',
        text,
    )
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", text)


def short_url(url: str) -> str:
    host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
    return host


def cells(row: str):
    return [c.strip() for c in row.strip().strip("|").split("|")]


def render(md: str, prefix: str):
    """Trả về (html, [(id, tiêu đề h2)])."""
    lines = md.split("\n")
    out, toc = [], []
    i, n = 0, len(lines)

    def is_block_start(l):
        return (
            not l.strip()
            or l.startswith("#")
            or l.startswith("|")
            or l.startswith(">")
            or l.startswith("```")
            or re.match(r"\s*([-*]|\d+\.)\s", l)
        )

    while i < n:
        l = lines[i]
        if not l.strip():
            i += 1
            continue
        if l.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append("<pre>" + html.escape("\n".join(buf)) + "</pre>")
            continue
        m = re.match(r"(#{1,4})\s+(.*)", l)
        if m:
            level, text = len(m.group(1)), inline(m.group(2))
            hid = f"{prefix}-{slug(text)}"
            if level == 1:
                out.append(f"<h1>{text}</h1>")
            else:
                if level == 2:
                    toc.append((hid, re.sub(r"<[^>]+>", "", text)))
                out.append(f'<h{level} id="{hid}">{text}</h{level}>')
            i += 1
            continue
        if l.startswith("|") and i + 1 < n and re.match(r"\|[\s:|-]+\|?\s*$", lines[i + 1]):
            head = cells(l)
            i += 2
            rows = []
            while i < n and lines[i].startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            t = ['<div class="tbl"><table><thead><tr>']
            t += [f"<th>{inline(c)}</th>" for c in head]
            t.append("</tr></thead><tbody>")
            for r in rows:
                r += [""] * (len(head) - len(r))
                t.append("<tr>" + "".join(f'<td data-th="{html.escape(re.sub(r"[*_`]", "", h))}">{inline(c)}</td>' for h, c in zip(head, r)) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue
        if l.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i][1:].strip())
                i += 1
            text = " ".join(buf)
            cls = "note warn" if "không phải" in text.lower() or "⚠" in text else "note"
            out.append(f'<div class="{cls}">{inline(text)}</div>')
            continue
        m = re.match(r"(\s*)([-*]|\d+\.)\s+(.*)", l)
        if m:
            ordered = m.group(2)[0].isdigit()
            base = len(m.group(1))
            items = []
            while i < n:
                m2 = re.match(r"(\s*)([-*]|\d+\.)\s+(.*)", lines[i])
                if m2 and len(m2.group(1)) <= base + 1 and (m2.group(2)[0].isdigit() == ordered):
                    items.append(m2.group(3))
                    i += 1
                elif lines[i].strip() and lines[i].startswith(" ") and items:
                    items[-1] += " " + lines[i].strip()
                    i += 1
                else:
                    break
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        if l.strip() == "{{zalo}}":
            out.append(ZALO)
            i += 1
            continue
        buf = [l.strip()]
        i += 1
        while i < n and not is_block_start(lines[i]):
            buf.append(lines[i].strip())
            i += 1
        text = " ".join(buf)
        cls = ' class="warn-line"' if text.startswith("⚠") else ""
        out.append(f"<p{cls}>{inline(text)}</p>")
    return "\n".join(out), toc


ZALO = """<div class="zalo">
<img src="assets/img/zalo-nhom-ho-tro.jpg" alt="Mã QR nhóm Zalo hỗ trợ khách hàng" width="220" loading="lazy">
<div><p><strong>Nhóm Zalo hỗ trợ khách hàng</strong></p>
<p>Quét mã bằng Zalo để vào nhóm, được hướng dẫn về thành phần hồ sơ và các mẫu đơn.</p>
<p class="small">Đây là nhóm hỗ trợ của đơn vị lập trang này, <strong>không phải kênh chính thức của chủ đầu tư HUD</strong>. Kênh chính thức của HUD: hud.com.vn, noxh.hud.com.vn, hotline 085.85.55589.</p></div>
</div>"""

DOWNLOADS = (
    '<h2 id="tai-ve">Tải biểu mẫu</h2>'
    "<p>Các mẫu theo nghị định, thông tư, dùng chung cả nước. Chủ đầu tư từng dự án có thể phát bản đã cập nhật — ưu tiên bản của chủ đầu tư.</p>"
    '<ul class="files">'
    + "".join(f'<li><a href="assets/bieu-mau/{f}" target="_blank" rel="noopener">{html.escape(t)}</a></li>' for f, t in FORMS)
    + "</ul>"
)


def main():
    nav, sections = [], []
    for tid, title, fname in TABS:
        body, toc = render((ROOT / "content" / fname).read_text(encoding="utf-8"), tid)
        if tid == "bieu-mau":
            body += DOWNLOADS
            toc.append(("tai-ve", "Tải biểu mẫu"))
        toc_html = ""
        if len(toc) > 2:
            toc_html = '<nav class="toc" aria-label="Mục lục"><strong>Trong trang này</strong><ol>' + "".join(
                f'<li><a href="#{i}">{html.escape(t)}</a></li>' for i, t in toc
            ) + "</ol></nav>"
        nav.append(f'<a href="#{tid}" data-tab="{tid}">{title}</a>')
        sections.append(f'<section id="{tid}" class="tab">{toc_html}<article>{body}</article></section>')
    page = (ROOT / "template.html").read_text(encoding="utf-8")
    page = page.replace("{{nav}}", "\n".join(nav)).replace("{{sections}}", "\n".join(sections)).replace("{{updated}}", UPDATED)
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print("index.html:", len(page), "ký tự")


if __name__ == "__main__":
    main()
