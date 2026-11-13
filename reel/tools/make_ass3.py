# Overlay for the Microsoft 365 news reel: title, bottom bar, Persian captions (own wording of the spoken text).
# usage: python make_ass3.py [story]
import sys
STORY = sys.argv[1:] == ["story"]
DY = 120 if STORY else 0  # shift the header below the Story profile bar
G, WHITE = "&H006BE322", "&H00FFFFFF"
D = 67.7

def t(s):
    return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"

# (start, end, cleaned text) per spoken segment; long ones are split into timed chunks below
segs = [
    (0.0, 7.3, "سلام دوستان، امیدوارم خوب باشین. دیشب خبری اومد که بخش عظیمی از دنیا رو تحت تأثیر قرار داد."),
    (8.0, 18.8, "سرورهای مایکروسافت شات‌دان شدن و پنجشنبه شب تستشون رو رد کردن. تیمز، آوت‌لوک و کوپایلوت تو سراسر دنیا از کار افتادن."),
    (20.0, 29.1, "ماجرا این بود که پنجشنبه شب سرورها تست سلامت رو رد کردن و خودکار خودشون رو خاموش کردن."),
    (30.3, 44.6, "الان تو سایت connectivity.office.com می‌بینیم که سرورها تقریباً به حالت عادی برگشتن."),
    (45.8, 48.6, "لینک سایت رو زیر ویدیو می‌ذارم، نگاه کنین."),
    (48.6, 63.9, "لینکش رو زیر ویدیو می‌ذارم. توی این سایت می‌تونین ببینین سرویس‌های مایکروسافت کجای دنیا چه مشکلی دارن."),
    (64.0, 66.4, "لینک رو زیر ویدیو گذاشتم، حتماً استفاده کنین."),
]

def chunks(text, n=6):
    w = text.split()
    out, cur = [], []
    for x in w:
        cur.append(x)
        if len(cur) >= n or x.endswith((".", "،")):
            out.append(" ".join(cur)); cur = []
    return out + ([" ".join(cur)] if cur else [])

caps = []
for s, e, txt in segs:
    cs = chunks(txt)
    tot = sum(len(c) for c in cs)
    p = s
    for c in cs:
        q = p + (e - s) * len(c) / tot
        caps.append((p, q - 0.05, c)); p = q

ev = []
def add(layer, style, text, s=0.0, e=D):
    ev.append(f"Dialogue: {layer},{t(s)},{t(e)},{style},,0,0,0,,{text}")

add(0, "Title", r"{\an8\pos(540,%d)\fad(500,0)}قطعی Microsoft 365" % (200 + DY))
add(1, "Bar", r"{\an5\pos(540,%d)}" % ((1725 if STORY else 1865)) + "چک کن: وضعیت سرویس‌ها ↓", 45.8)
add(0, "Shape", r"{\an7\pos(0,%d)\p1\1c&H6BE322&\bord0}m 0 0 l 1080 0 l 1080 110 l 0 110" % (1680 if STORY else 1810), 45.8)
for s, e, c in caps:
    add(2, "Cap", r"{\fad(80,80)}" + c, s, e)

CAP_V = 260 if STORY else 170
head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Vazirmatn Black,96,{WHITE},{WHITE},&H80000000,&H00000000,1,0,0,0,100,100,0,0,1,0,6,8,0,0,0,1
Style: Bar,Vazirmatn,44,&H00000000,&H00000000,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Cap,Vazirmatn,64,{WHITE},{WHITE},&H40331A0B,&H00000000,1,0,0,0,100,100,0,0,3,18,0,2,60,60,{CAP_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
name = "story3.ass" if STORY else "overlay3.ass"
open(name, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")
assert all(a[1] <= b[0] + 0.01 for a, b in zip(caps, caps[1:])), "caption overlap"
print(name, len(ev), "events")
