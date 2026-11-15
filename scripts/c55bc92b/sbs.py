import sys
from PIL import Image
a = Image.open(sys.argv[1]).convert("RGB"); b = Image.open(sys.argv[2]).convert("RGB")
w = a.width + b.width + 20; h = max(a.height, b.height)
c = Image.new("RGB", (w, h), (255, 255, 255)); c.paste(a, (0, 0)); c.paste(b, (a.width + 20, 0)); c.save(sys.argv[3]); print(c.size)
