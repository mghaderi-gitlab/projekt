# Overlay for the website-launch reel: FA badge, series/step headers, handle, word-by-word Persian captions (active word magenta).
MAG_BGR, WHITE = "&H7524E0&", "&HFFFFFF&"
D = 58.6
STARTS = [0, 9.2, 18.0, 25.8, 33.7, 40.3, 48.0]

def t(s):
    return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"

def rrect(w, h, r):
    k = r * 0.45
    return (f"m {r} 0 l {w-r} 0 b {w-k} 0 {w} {k} {w} {r} l {w} {h-r} b {w} {h-k} {w-k} {h} {w-r} {h} "
            f"l {r} {h} b {k} {h} 0 {h-k} 0 {h-r} l 0 {r} b 0 {k} {k} 0 {r} 0")

# (start, end, spoken text): same wording as the recorded script; timings from the transcript segments
segs = [
    (0.0, 8.9, "سایتتون رو راه انداختید؟ فکر می‌کنید کار تمومه؟ نه، تازه شروعشه! این پنج کار رو بعد از لانچ حتماً انجام بدید."),
    (9.3, 17.7, "یک: سایت رو توی Google Search Console ثبت کنید. می‌بینید گوگل کدوم صفحه‌ها رو ایندکس کرده و مردم با چه کلمه‌هایی پیداتون می‌کنن."),
    (18.1, 25.8, "دو: برای کسب‌وکارتون توی Google Business Profile پروفایل بسازید. اینجوری مشتری‌ها شما رو توی گوگل و نقشه پیدا می‌کنن."),
    (25.8, 33.2, "سه: Google Analytics رو وصل کنید. می‌فهمید چند نفر اومدن، از کجا اومدن و توی سایت چیکار کردن."),
    (33.8, 39.9, "چهار: سایت رو توی Bing Webmaster Tools هم ثبت کنید، تا توی یه موتور جستجوی دیگه هم دیده بشید."),
    (40.4, 47.2, "پنج: سرعت سایت رو با PageSpeed Insights تست کنید. صفحه‌ی کند یعنی بازدیدکننده‌ای که رفته."),
    (48.2, 54.4, "طراحی سایت فقط قدم اوله. دیده شدن، تحلیل و بهینه‌سازی کسب‌وکارتون رو رشد می‌ده."),
    (54.6, 58.4, "این ویدیو رو ذخیره کنید که هیچ مرحله‌ای یادتون نره."),
]
heads = [  # (small line, big line(s))
    ("۵ کار ضروری بعد از لانچ", r"سایتتون رو راه انداختید؟\N{\c" + MAG_BGR + r"}تازه شروعشه!"),
    ("قدم ۱ از ۵", "Google Search Console"), ("قدم ۲ از ۵", "Google Business Profile"),
    ("قدم ۳ از ۵", "Google Analytics"), ("قدم ۴ از ۵", "Bing Webmaster Tools"), ("قدم ۵ از ۵", "PageSpeed Insights"),
    ("ذخیره کنید", r"طراحی سایت فقط\N{\c" + MAG_BGR + r"}قدم اوله"),
]

ev = []
def add(layer, style, text, s=0.0, e=D):
    ev.append(f"Dialogue: {layer},{t(s)},{t(e)},{style},,0,0,0,,{text}")

add(0, "Shape", r"{\an7\pos(40,175)\p1\1c&H7524E0&\bord0}" + rrect(130, 76, 20))
add(1, "Badge", r"{\an5\pos(105,213)}FA")
for k, (small, big) in enumerate(heads):
    s, e = STARTS[k], (STARTS[k + 1] if k < 6 else D)
    add(1, "Small", r"{\an8\pos(540,%d)\fad(150,0)}%s" % (200, small), s, e)
    add(1, "Big", r"{\an8\pos(540,%d)\fad(200,0)}{\c&HFFFFFF&}%s" % (290, big), s, e)
add(1, "Handle", r"{\an1\pos(205,1790)}@mgsina.tech", 0)
add(1, "Tag", r"{\an1\pos(205,1850)}آیتی ساده", 0)

def words_events(s, e, text, n=3):
    w = text.split()
    tot = sum(len(x) + 1 for x in w); p = s; stamps = []
    for x in w:  # word times proportional to length inside the segment
        q = p + (e - s) * (len(x) + 1) / tot; stamps.append((p, q)); p = q
    for c in range(0, len(w), n):
        for i in range(c, min(c + n, len(w))):
            line = " ".join(("{\\c%s}%s{\\c%s}" % (MAG_BGR, w[j], WHITE)) if j == i else w[j] for j in range(c, min(c + n, len(w))))
            add(2, "Cap", line, stamps[i][0], stamps[i][1] if i + 1 == min(c + n, len(w)) else stamps[i][1])

for s, e, txt in segs:
    words_events(s, e, txt)

head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Shape,Vazirmatn,20,&HFFFFFF&,&HFFFFFF&,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,-1
Style: Badge,Vazirmatn Black,46,&HFFFFFF&,&HFFFFFF&,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,-1
Style: Small,Vazirmatn,46,&HFFFFFF&,&HFFFFFF&,&H80000000,&H00000000,0,0,0,0,100,100,0,0,1,0,3,8,0,0,0,-1
Style: Big,Vazirmatn Black,86,&HFFFFFF&,&HFFFFFF&,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,6,4,8,40,40,0,-1
Style: Handle,Vazirmatn Black,50,&HFFFFFF&,&HFFFFFF&,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,4,3,1,0,0,0,-1
Style: Tag,Vazirmatn,38,&HFFFFFF&,&HFFFFFF&,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,3,2,1,0,0,0,-1
Style: Cap,Vazirmatn Black,78,&HFFFFFF&,&HFFFFFF&,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,8,0,2,60,60,430,-1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open("web.ass", "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")
print(len(ev), "events")
