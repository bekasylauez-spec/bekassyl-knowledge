# -*- coding: utf-8 -*-
"""HTML бетін таза мәтінге айналдыру (тек стандарт кітапхана). Қолдану: python -I html2txt.py in.html out.txt"""
import sys, re, html
from html.parser import HTMLParser


class T(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1
        if tag in ("p", "br", "div", "tr", "li", "h1", "h2", "h3", "h4", "table"):
            self.out.append("\n")
        if tag in ("td", "th"):
            self.out.append(" | ")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.skip:
            self.skip -= 1
        if tag in ("p", "div", "tr", "li", "h1", "h2", "h3", "h4", "table"):
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def main(src, dst):
    raw = open(src, "rb").read()
    txt = raw.decode("utf-8", errors="replace")
    p = T()
    p.feed(txt)
    s = "".join(p.out)
    s = s.replace("\xa0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    open(dst, "w", encoding="utf-8").write(s)
    print(src, "->", dst, len(s), "chars,", s.count("\n"), "lines")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
