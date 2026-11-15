# Magenta-style animated scenes for the "5 things after your website launch" reel (no presenter footage).
# usage: python anim_web.py out.mp4 "0,9.2,18,25.8,33.7,40.3,48" 58.6      |   ... preview.jpg ... 58.6 preview
import sys, math, subprocess
import numpy as np, cv2

W, H, FPS = 1080, 1920, 30
MAG, WHITE, PANEL, GREY, GREEN = (224, 36, 117), (245, 245, 250), (22, 30, 84), (110, 120, 160), (60, 220, 140)
out, starts, dur = sys.argv[1], [float(x) for x in sys.argv[2].split(",")], float(sys.argv[3])
assert len(starts) == 7 and starts == sorted(starts), "need 7 ascending scene starts"
FONT = cv2.FONT_HERSHEY_DUPLEX

def backdrop():
    y = np.linspace(0, 1, H)[:, None, None]
    bg = np.broadcast_to(np.array([10, 18, 64.]) * (1 - y) + np.array([6, 10, 40.]) * y, (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    for cx, cy, r, col in [(900, 420, 440, MAG), (140, 1350, 420, (50, 90, 230))]:
        bg += np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r ** 2))[..., None] * np.array(col) * 0.24
    bg = np.where(((xx % 90 == 0) | (yy % 90 == 0))[..., None], bg + 9, bg)
    return np.clip(bg, 0, 255).astype(np.uint8)
BG = backdrop()
ease = lambda x: (lambda c: c * c * (3 - 2 * c))(min(1.0, max(0.0, x)))

def rr(img, x0, y0, x1, y1, r, col, th=-1):
    if th < 0:
        cv2.rectangle(img, (x0 + r, y0), (x1 - r, y1), col, -1); cv2.rectangle(img, (x0, y0 + r), (x1, y1 - r), col, -1)
        for cx, cy in [(x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)]:
            cv2.circle(img, (cx, cy), r, col, -1, cv2.LINE_AA)
    else:
        for (a, b), (c, d) in [((x0 + r, y0), (x1 - r, y0)), ((x0 + r, y1), (x1 - r, y1)), ((x0, y0 + r), (x0, y1 - r)), ((x1, y0 + r), (x1, y1 - r))]:
            cv2.line(img, (a, b), (c, d), col, th, cv2.LINE_AA)
        for cx, cy, a0 in [(x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90)]:
            cv2.ellipse(img, (cx, cy), (r, r), 0, a0, a0 + 90, col, th, cv2.LINE_AA)

def text(img, s, x, y, scale=1.0, col=WHITE, th=2, center=False):
    if center:
        x -= cv2.getTextSize(s, FONT, scale, th)[0][0] // 2
    cv2.putText(img, s, (int(x), int(y)), FONT, scale, col, th, cv2.LINE_AA)

def check(img, cx, cy, s=16, col=GREEN, th=7):
    cv2.polylines(img, [np.array([[cx - s, cy], [cx - s // 3, cy + s * 2 // 3], [cx + s, cy - s * 2 // 3]])], False, col, th, cv2.LINE_AA)

def star(img, cx, cy, r, col):
    pts = [(cx + (r if i % 2 == 0 else r * 0.45) * math.sin(i * math.pi / 5), cy - (r if i % 2 == 0 else r * 0.45) * math.cos(i * math.pi / 5)) for i in range(10)]
    cv2.fillPoly(img, [np.array(pts, np.int32)], col, cv2.LINE_AA)

def nodes(img, t):  # drifting network dots, shared by all scenes
    rng = np.random.default_rng(3)
    pts = [(int(((rng.random() * W) + t * 14 * (0.5 + rng.random())) % W), int(430 + rng.random() * 900)) for _ in range(26)]
    for i, p in enumerate(pts):
        for q in pts[i + 1:]:
            if (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 < 170 ** 2:
                cv2.line(img, p, q, (40, 64, 130), 1, cv2.LINE_AA)
        cv2.circle(img, p, 4, (110, 90, 190), -1, cv2.LINE_AA)

_yy, _xx = np.mgrid[0:H, 0:W]
HALO = np.exp(-((_xx - 540) ** 2 + (_yy - 600) ** 2) / (2 * 300.0 ** 2)).astype(np.float32)
def s0(img, t):  # cover-style title card: magenta halo + ring behind the portrait (portrait overlaid by ffmpeg)
    g = HALO[..., None] * np.array(MAG, np.float32) * (0.55 + 0.08 * math.sin(t * 3))
    img[:] = np.clip(img.astype(np.float32) + g, 0, 255).astype(np.uint8)
    cv2.circle(img, (540, 600), 330, MAG, 4, cv2.LINE_AA)

def s1(img, t):  # Search Console: URL submitted, pages indexed, clicks rising
    rr(img, 110, 620, 970, 1230, 28, PANEL); rr(img, 110, 620, 970, 1230, 28, GREY, 2)
    rr(img, 150, 660, 930, 730, 34, (40, 52, 110))
    text(img, "yoursite.com", 190, 708, 1.1)
    cv2.circle(img, (880, 695), 18, MAG, 4, cv2.LINE_AA); cv2.line(img, (893, 708), (906, 721), MAG, 5, cv2.LINE_AA)
    for i in range(4):
        y = 790 + i * 62; on = t > 1.0 + i * 0.9
        rr(img, 150, y, 930, y + 44, 12, (52, 34, 72))
        if on:
            rr(img, 150, y, 150 + int(780 * ease((t - 1.0 - i * 0.9) / 0.6) * (0.55 + 0.12 * i)), y + 44, 12, MAG); check(img, 890, y + 22, 12, WHITE, 5)
    p = ease((t - 3.5) / 3.5); pts = [(170 + int(i * 76), 1190 - int(80 * (i / 10) ** 1.5 * 10 * p + 8 * math.sin(i * 2) * p)) for i in range(11)]
    k = max(2, int(2 + 9 * p)); cv2.polylines(img, [np.array(pts[:k])], False, GREEN, 6, cv2.LINE_AA)

def s2(img, t):  # Business Profile: map pin drops, card with stars
    rr(img, 110, 620, 970, 1230, 28, (28, 40, 64)); rr(img, 110, 620, 970, 1230, 28, GREY, 2)
    for i in range(1, 8): cv2.line(img, (110 + i * 107, 625), (110 + i * 107 - 50, 1225), (50, 66, 96), 3, cv2.LINE_AA)
    for j in range(1, 5): cv2.line(img, (115, 620 + j * 120), (965, 650 + j * 110), (50, 66, 96), 3, cv2.LINE_AA)
    d = ease(t / 1.2); y = int(560 + (780 - 560) * d - 50 * abs(math.sin(t * 3)) * (1 - d))
    cv2.circle(img, (540, y), 44, MAG, -1, cv2.LINE_AA); cv2.circle(img, (540, y), 16, WHITE, -1, cv2.LINE_AA)
    cv2.fillPoly(img, [np.array([[512, y + 30], [568, y + 30], [540, y + 78]])], MAG, cv2.LINE_AA)
    if t > 2.0:
        a = ease((t - 2.0) / 0.6); yy = int(1230 - 270 * a)
        rr(img, 200, yy, 880, yy + 250, 24, PANEL); rr(img, 200, yy, 880, yy + 250, 24, MAG, 3)
        text(img, "Your business", 250, yy + 70, 1.2)
        for i in range(5): star(img, 262 + i * 52, yy + 125, 22, (255, 200, 60) if t > 3 + i * 0.3 else GREY)
        for i, lab in enumerate(["Call", "Route", "Web"]): rr(img, 250 + i * 200, yy + 165, 410 + i * 200, yy + 225, 20, MAG); text(img, lab, 330 + i * 200, yy + 207, 0.9, WHITE, 2, True)

def s3(img, t):  # Analytics: visitors arrive from three sources, bars grow
    rr(img, 110, 620, 970, 1230, 28, PANEL); rr(img, 110, 620, 970, 1230, 28, GREY, 2)
    for i, (lab, w) in enumerate([("Search", 0.9), ("Social", 0.55), ("Direct", 0.4)]):
        y = 700 + i * 120; text(img, lab, 150, y + 34, 1.0, GREY)
        rr(img, 330, y, 930, y + 50, 16, (52, 34, 72)); rr(img, 330, y, 330 + max(32, int(600 * w * ease((t - 0.5 - i * 0.7) / 1.4))), y + 50, 16, MAG)
    rng = np.random.default_rng(5)
    for n in range(40):
        p = (t * 0.45 + rng.random()) % 1; sx = rng.random() * 760 + 160; e = ease(p)
        cv2.circle(img, (int(sx + (540 - sx) * e), int(1040 + (1130 - 1040) * e)), 6, WHITE, -1, cv2.LINE_AA)
    rr(img, 400, 1120, 680, 1200, 30, MAG); text(img, "visitors", 540, 1172, 1.1, WHITE, 2, True)

def s4(img, t):  # Bing: second search engine joins
    for k, (lab, y, on) in enumerate([("Google", 700, True), ("Bing", 920, t > 1.2)]):
        rr(img, 130, y, 500, y + 150, 28, PANEL); rr(img, 130, y, 500, y + 150, 28, MAG if on else GREY, 4 if on else 2)
        text(img, lab, 315, y + 94, 1.5, WHITE if on else GREY, 3, True)
        if on:
            a = ease((t - (0.2 if k == 0 else 1.2)) / 1.0); cv2.line(img, (500, y + 75), (500 + int(190 * a), 1000 - int((1000 - y - 75) * 0 + (y + 75 - 1000) * 0) if False else 1000 + int((y + 75 - 1000) * (1 - a))), MAG, 6, cv2.LINE_AA)
    cv2.circle(img, (800, 1000), 120, PANEL, -1, cv2.LINE_AA); cv2.circle(img, (800, 1000), 120, MAG, 4, cv2.LINE_AA); text(img, "Your", 800, 990, 1.0, WHITE, 2, True); text(img, "site", 800, 1030, 1.0, WHITE, 2, True)
    if t > 2.6: check(img, 760, 1190, 24, GREEN, 9); text(img, "connected", 810, 1204, 1.0, GREEN)

def s5(img, t):  # PageSpeed: gauge sweeps, fast
    c = (540, 940); p = ease(t / 3.0) * 0.93
    cv2.ellipse(img, c, (270, 270), 0, 135, 405, (60, 44, 80), 30, cv2.LINE_AA)
    col = tuple(int(MAG[i] + (GREEN[i] - MAG[i]) * ease(t / 3.0)) for i in range(3))
    cv2.ellipse(img, c, (270, 270), 0, 135, 135 + 270 * p, col, 30, cv2.LINE_AA)
    text(img, "FAST", 540, 975, 2.6, WHITE, 5, True)
    for i, lab in enumerate(["LCP", "INP", "CLS"]):
        x = 270 + i * 270; on = t > 3.0 + i * 0.5
        rr(img, x - 100, 1190, x + 100, 1250, 30, MAG if on else (52, 34, 72)); text(img, lab, x, 1232, 1.0, WHITE, 2, True)

def s6(img, t):  # recap checklist + bookmark
    for i, lab in enumerate(["Search Console", "Business Profile", "Analytics", "Bing Webmaster", "PageSpeed"]):
        y = 640 + i * 118; on = t > 0.5 + i * 0.8
        rr(img, 150, y, 930, y + 90, 24, PANEL); rr(img, 150, y, 930, y + 90, 24, MAG if on else GREY, 3)
        text(img, lab, 330, y + 60, 1.2)
        if on: check(img, 225, y + 46, 20, GREEN, 9)
    if t > 6.6:
        a = 1 + 0.08 * math.sin(t * 6); x, y = 540, 1300
        cv2.fillPoly(img, [np.array([[x - 45 * a, y - 70 * a], [x + 45 * a, y - 70 * a], [x + 45 * a, y + 70 * a], [x, y + 35 * a], [x - 45 * a, y + 70 * a]], np.int32)], MAG, cv2.LINE_AA)

SC = [s0, s1, s2, s3, s4, s5, s6]
def scene_img(k, t):
    img = BG.copy(); nodes(img, t); SC[k](img, t - starts[k]); return img
def frame(t):
    k = max(i for i in range(7) if t >= starts[i]); img = scene_img(k, t)
    if k and t - starts[k] < 0.3:
        a = (t - starts[k]) / 0.3; img = cv2.addWeighted(scene_img(k - 1, t), 1 - a, img, a, 0)
    return img

if sys.argv[4:] == ["preview"]:
    ts = [s + 3.2 for s in starts] + [starts[6] + 8]
    tiles = [cv2.resize(frame(min(t, dur - 0.05))[420:1360], (320, 470)) for t in ts]
    cv2.imwrite(out, cv2.cvtColor(np.vstack([np.hstack(tiles[:4]), np.hstack(tiles[4:])]), cv2.COLOR_RGB2BGR))
else:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for n in range(int(dur * FPS)):
        enc.stdin.write(frame(n / FPS).tobytes())
    enc.stdin.close(); enc.wait(); assert enc.returncode == 0, "encode failed"
print("ok")
