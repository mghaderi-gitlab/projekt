# Writes overlay.ass (reel) or story.ass (argv[1]=="story": shifted into the Story safe zone, logo slot on top).
import sys
STORY = sys.argv[1:] == ["story"]
DY = 270 if STORY else 0  # header shift: Story profile bar + logo above it
G, NAVY, WHITE = "&H006BE322", "&H00331A0B", "&H00FFFFFF"

caps = [  # (start, end, text) cleaned from the Whisper transcript
    (0.0, 2.9, "سلام به همه دوستان، امیدوارم خوب باشید"),
    (3.1, 6.8, "یه پستی گذاشته بودم راجع به دیتاکمپ"),
    (6.9, 11.8, "و دوره‌هایی که دیتاکمپ واسه هوش مصنوعی"),
    (11.9, 15.8, "گذاشته بود، همون AI"),
    (16.0, 19.6, "خواستم بگم هنوز دوره‌هاش هست"),
    (19.7, 21.6, "می‌تونین استفاده کنین"),
    (21.7, 25.1, "خوبیش اینه که نیازی به وارد کردن"),
    (25.2, 28.0, "کارت اعتباری یا هیچ اطلاعاتی نیست"),
    (28.1, 31.9, "خیلی پرفکته واسه بچه‌هایی که از ایران هستن"),
    (32.0, 34.4, "می‌تونین اینفوی خوبی بگیرین"),
    (34.5, 38.5, "آگاهی‌تون نسبت به هوش مصنوعی بیشتر بشه"),
    (38.6, 42.3, "با اطلاعاتی که توی دوره‌ها در اختیارتون میذارن"),
    (42.4, 44.8, "واقعاً، واقعاً خوبه"),
    (44.9, 45.9, "برین استفاده کنین"),
    (46.0, 48.1, "پستش رو توی پیج اینستاگرامم گذاشتم"),
    (48.2, 50.7, "دوباره استوری می‌کنم، لینکش اونجاست"),
    (50.8, 52.6, "برین استفاده کنین"),
    (52.7, 54.5, "موفق باشین، بدرود"),
]

def t(s):
    return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"

def rrect(w, h, r):  # rounded rectangle as an ASS vector drawing
    k = r * 0.45
    return (f"m {r} 0 l {w-r} 0 b {w-k} 0 {w} {k} {w} {r} l {w} {h-r} b {w} {h-k} {w-k} {h} {w-r} {h} "
            f"l {r} {h} b {k} {h} 0 {h-k} 0 {h-r} l 0 {r} b 0 {k} {k} 0 {r} 0")

END = t(54.6)
ev = []
def add(layer, style, text, s=0.0, e=None):
    ev.append(f"Dialogue: {layer},{t(s)},{e or END},{style},,0,0,0,,{text}")

add(0, "Mono", r"{\an8\pos(540,%d)\fad(400,0)}# FREE ACCESS" % (110 + DY))
add(0, "Title", r"{\an8\pos(540,%d)\fad(600,0)}DataCamp AI" % (185 + DY))
add(0, "Sub", r"{\an8\pos(540,%d)\fad(800,0)}دوره‌های رایگان هوش مصنوعی" % (350 + DY))
for x, w, label in [(300, 440, "بدون کارت اعتباری"), (780, 440, "Python · AI · Data")]:
    add(0, "Shape", r"{\an5\pos(%d,%d)\p1\1c&H00402A1A&\3c&H00FFFFFF&\bord2\1a&H30&\fad(1000,0)}%s" % (x, 505 + DY, rrect(w, 84, 42)))
    add(1, "Pill", r"{\an5\pos(%d,%d)\fad(1000,0)}%s" % (x, 505 + DY, label))
add(0, "Shape", r"{\an7\pos(0,%d)\p1\1c&H6BE322&\bord0}m 0 0 l 1080 0 l 1080 110 l 0 110" % (1680 if STORY else 1810))
add(1, "Bar", r"{\an5\pos(540,%d)}%s" % ((1725, "روی لینک بزن و رایگان ثبت‌نام کن ↑") if STORY else (1865, "لینک در استوری و پیج اینستاگرام ↑")))
for s, e, txt in caps:
    add(2, "Cap", r"{\fad(80,80)}" + txt, s, t(e))

CAP_V = 260 if STORY else 170
head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Mono,JetBrains Mono,60,{G},{G},&H00000000,&H00000000,1,0,0,0,100,100,2,0,1,0,0,8,0,0,0,1
Style: Title,Vazirmatn Black,140,{WHITE},{WHITE},&H80000000,&H00000000,1,0,0,0,100,100,0,0,1,0,6,8,0,0,0,1
Style: Sub,Vazirmatn,58,{WHITE},{WHITE},&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,8,0,0,0,1
Style: Pill,Vazirmatn,46,{WHITE},{WHITE},&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Shape,Vazirmatn,20,{WHITE},{WHITE},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Bar,Vazirmatn,44,&H00000000,&H00000000,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Cap,Vazirmatn,64,{WHITE},{WHITE},&H40331A0B,&H00000000,1,0,0,0,100,100,0,0,3,18,0,2,60,60,{CAP_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open("story.ass" if STORY else "overlay.ass", "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")
assert all(s < e for s, e, _ in caps) and all(a[1] <= b[0] for a, b in zip(caps, caps[1:])), "caption overlap"
print(len(ev), "events")
