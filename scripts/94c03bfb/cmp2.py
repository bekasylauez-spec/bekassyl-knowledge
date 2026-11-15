from PIL import Image, ImageDraw, ImageFont
a = Image.open(r'C:\Users\Admin\AppData\Local\Temp\claude\825e6488202eeeff\94c03bfb-48e3-4972-8913-5871021722f0\scratchpad\pdf_p5_zoom.png').convert('RGB'); b = Image.open(r'D:\_claude_work\Kasymova\revit\png\q_core25.png').convert('RGB')
H = 760; a = a.resize((int(a.width * H / a.height), H)); b = b.resize((int(b.width * H / b.height), H))
im = Image.new('RGB', (a.width + b.width + 30, H + 60), 'white'); im.paste(a, (0, 60)); im.paste(b, (a.width + 30, 60))
d = ImageDraw.Draw(im); f = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 30)
d.text((10, 12), '2.5 ядро — бұрын (200/200, 2000/150 қабаттасқан)', fill='black', font=f); d.text((a.width + 40, 12), '2.5 ядро — қазір', fill='black', font=f)
d.line([(a.width + 15, 0), (a.width + 15, H + 60)], fill=(150, 150, 150), width=3); im.save(r'C:\Users\Admin\AppData\Local\Temp\claude\825e6488202eeeff\94c03bfb-48e3-4972-8913-5871021722f0\scratchpad\Жазулар_бұрын_қазір.png'); print(im.size)
