# Animated backdrop for the "Microsoft 365 outage" reel: 7 scenes, timings from scene-start list.
# usage: python anim.py out.mp4 "0,5,15,22,32,46,55" 56      (render video)
#        python anim.py preview.jpg "0,5,15,22,32,46,55" 56 preview   (montage of sample frames)
import sys, math, subprocess
import numpy as np, cv2

W, H, FPS = 1080, 1920, 30
GREEN, RED, YEL, WHITE, GREY, BLUE = (34, 227, 107), (240, 70, 70), (250, 200, 50), (240, 240, 245), (95, 105, 125), (70, 120, 230)
out, starts, dur = sys.argv[1], [float(x) for x in sys.argv[2].split(",")], float(sys.argv[3])
assert len(starts) == 7 and starts == sorted(starts), "need 7 ascending scene starts"
rng = np.random.default_rng(7)
PX, PY, PS = rng.random(400), rng.random(400), rng.random(400)  # particle seeds

def backdrop():
    y = np.linspace(0, 1, H)[:, None, None]
    bg = np.broadcast_to(np.array([18, 26, 52.]) * (1 - y) + np.array([8, 30, 22.]) * y, (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    for cx, cy, r, col in [(900, 330, 420, (40, 220, 110)), (150, 1250, 380, (60, 90, 200))]:
        bg += np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r ** 2))[..., None] * np.array(col) * 0.35
    bg = np.where(((xx % 90 == 0) | (yy % 90 == 0))[..., None], bg + 10, bg)
    return np.clip(bg, 0, 255).astype(np.uint8)
BG = backdrop()

def cross(img, cx, cy, s, col=RED, th=8):
    cv2.line(img, (cx - s, cy - s), (cx + s, cy + s), col, th, cv2.LINE_AA)
    cv2.line(img, (cx - s, cy + s), (cx + s, cy - s), col, th, cv2.LINE_AA)

def rack(img, cx, cy, state, w=150, h=105, t=0.0):
    col = {"ok": GREEN, "dead": GREY, "warn": YEL, "bad": RED, "off": (60, 68, 90)}[state]
    sx = int(4 * math.sin(t * 60)) if state == "bad" else 0
    x0, y0 = cx - w // 2 + sx, cy - h // 2
    cv2.rectangle(img, (x0, y0), (x0 + w, y0 + h), (28, 36, 62), -1)
    cv2.rectangle(img, (x0, y0), (x0 + w, y0 + h), col, 3, cv2.LINE_AA)
    for k in range(3):
        yk = y0 + 18 + k * 26
        cv2.line(img, (x0 + 14, yk), (x0 + w - 44, yk), col if state != "dead" else GREY, 4, cv2.LINE_AA)
        cv2.circle(img, (x0 + w - 22, yk), 6, col, -1, cv2.LINE_AA)
    if state == "dead":
        cross(img, cx, cy, 24, RED, 7)

def particles(img, n, t, tgt, y0=340, spread=360, spd=0.55, col=WHITE):
    for i in range(n):
        p = (t * spd + PS[i]) % 1.0
        e = p * p * (3 - 2 * p)
        tx, ty = tgt[i % len(tgt)]
        sx = 540 + (PX[i] - 0.5) * 2 * spread
        cv2.circle(img, (int(sx + (tx - sx) * e), int(y0 + (ty - y0) * e)), 5, col, -1, cv2.LINE_AA)

def globe(img, t):
    cx, cy, R = 540, 560, 215
    for lat in range(-80, 81, 10):
        for lon in range(0, 360, 10):
            l = math.radians(lon) + t * 0.8
            if math.cos(l) <= 0:
                continue
            ph = math.radians(lat)
            x, y = cx + R * math.cos(ph) * math.sin(l), cy - R * math.sin(ph)
            land = (math.sin(lon * 0.37 + lat * 0.21) + math.sin(lon * 0.11 - lat * 0.4)) > 0.2
            cv2.circle(img, (int(x), int(y)), max(2, int(5 * math.cos(l) * math.cos(ph) + 1)), RED if land else (110, 60, 70), -1, cv2.LINE_AA)

def s1(img, t):  # global outage
    globe(img, t)
    for i, name in enumerate(["Outlook", "Teams", "Copilot"]):
        cx = 300 + i * 240
        down = t > 1.3 + i * 0.5
        cv2.rectangle(img, (cx - 80, 810), (cx + 80, 910), (28, 36, 62), -1)
        cv2.rectangle(img, (cx - 80, 810), (cx + 80, 910), RED if down else BLUE, 4, cv2.LINE_AA)
        cv2.putText(img, name, (cx - 62, 872), cv2.FONT_HERSHEY_DUPLEX, 1.0, WHITE, 2, cv2.LINE_AA)
        if down:
            cross(img, cx + 78, 812, 16, RED, 6)

def s2(img, t):  # health check scan, most servers drop
    scan = min(1.0, t / 3.0)
    for i in range(10):
        cx, cy = 540 + (i % 5 - 2) * 190, 470 + (i // 5) * 200
        dead = t > 4.0 + (i * 0.37 % 2.2) and i not in (3, 8)
        rack(img, cx, cy, "dead" if dead else "ok", t=t)
    y = int(350 + scan * 340) if t < 3.2 else -1
    if y > 0:
        cv2.line(img, (110, y), (970, y), WHITE, 3, cv2.LINE_AA)

def s3(img, t):  # all traffic onto the two survivors
    st = "ok" if t < 1.5 else "warn" if t < 3.5 else "bad"
    pos = [(380, 800), (700, 800)]
    for x, y in pos:
        rack(img, x, y, st, 190, 130, t)
    particles(img, 260, t, [(x, y - 70) for x, y in pos])

def s4(img, t):  # who was hit
    def draw(i, cx, cy, col):
        if i == 0: cv2.rectangle(img, (cx - 30, cy - 55), (cx + 30, cy + 55), col, 5, cv2.LINE_AA); cv2.circle(img, (cx, cy + 40), 6, col, -1)
        elif i == 1: cv2.rectangle(img, (cx - 55, cy - 20), (cx + 55, cy + 55), col, 5, cv2.LINE_AA); cv2.line(img, (cx - 65, cy - 20), (cx + 65, cy - 20), col, 8, cv2.LINE_AA)
        elif i == 2:
            cv2.polylines(img, [np.array([[cx - 60, cy - 15], [cx, cy - 60], [cx + 60, cy - 15]])], True, col, 5, cv2.LINE_AA)
            for k in (-40, -13, 13, 40): cv2.line(img, (cx + k, cy - 5), (cx + k, cy + 50), col, 5, cv2.LINE_AA)
        elif i == 3:
            cv2.rectangle(img, (cx - 60, cy - 10), (cx + 60, cy + 55), col, 5, cv2.LINE_AA)
            cv2.polylines(img, [np.array([[cx - 60, cy - 10], [cx, cy - 55], [cx + 60, cy - 10]])], True, col, 5, cv2.LINE_AA)
        else:
            cv2.rectangle(img, (cx - 35, cy - 75), (cx + 35, cy + 55), col, 5, cv2.LINE_AA)
            for r in range(4): cv2.line(img, (cx - 20, cy - 50 + r * 28), (cx + 20, cy - 50 + r * 28), col, 3)
    for i in range(5):
        cx, cy, on = 140 + i * 200, 640, t > 0.4 + i * 1.3
        if on:
            hit = t > 1.0 + i * 1.3
            draw(i, cx, cy, RED if hit else WHITE)
            if hit: cross(img, cx + 45, cy - 70, 18, RED, 7)

def s5(img, t):  # restart fails: handshake work, then flood
    cx, cy = 540, 520
    if t < 3:
        rack(img, cx, cy, "ok", 260, 170, t)
        fill = min(1, t / 2.5); col = GREEN
    elif t < 8:
        rack(img, cx, cy, "ok", 260, 170, t)
        fill, col = 1, GREEN
        cv2.rectangle(img, (180, 760), (260, 860), WHITE, 4, cv2.LINE_AA); cv2.circle(img, (220, 760), 24, WHITE, 4, cv2.LINE_AA)  # padlock
        cv2.rectangle(img, (820, 750), (880, 870), WHITE, 4, cv2.LINE_AA)  # phone
        for k in range(10):
            x = 280 + ((k * 54 + t * 160) % 540)
            cv2.circle(img, (int(x), 810), 7, GREEN, -1, cv2.LINE_AA)
    else:
        k = min(1, (t - 8) / 4)
        rack(img, cx, cy, "bad" if k > 0.5 else "warn", 260, 170, t)
        particles(img, int(60 + 340 * k), t, [(cx, cy - 90)], spread=480, spd=0.9)
        fill, col = min(1, 0.4 + k), RED
    cv2.rectangle(img, (240, 900), (840, 930), GREY, 2, cv2.LINE_AA)
    cv2.rectangle(img, (240, 900), (240 + int(600 * fill), 930), col, -1)

def s6(img, t):  # throttled power-up, one rack at a time
    cv2.rectangle(img, (110, 470), (470, 492), WHITE, -1); cv2.rectangle(img, (610, 470), (970, 492), WHITE, -1)  # gate
    particles(img, 40, t, [(540, 600)], y0=340, spread=330, spd=0.3)
    for i in range(10):
        cx, cy = 540 + (i % 5 - 2) * 190, 690 + (i // 5) * 140
        rack(img, cx, cy, "ok" if t > 0.8 + i * 0.8 else "off", 150, 95, t)

def s7(img, t):
    for i in range(10):
        rack(img, 540 + (i % 5 - 2) * 190, 560 + (i // 5) * 200, "ok", t=t)

SCENES = [s1, s2, s3, s4, s5, s6, s7]

def scene_img(k, t):
    img = BG.copy()
    SCENES[k](img, t - starts[k])
    return img

def frame(t):
    k = max(i for i in range(7) if t >= starts[i])
    img = scene_img(k, t)
    if k and t - starts[k] < 0.3:  # short crossfade from previous scene
        a = (t - starts[k]) / 0.3
        img = cv2.addWeighted(scene_img(k - 1, t), 1 - a, img, a, 0)
    return img

if sys.argv[4:] == ["preview"]:
    ts = [s + 3.5 for s in starts]
    tiles = [cv2.resize(frame(min(t, dur - 0.1))[:1100], (360, 440)) for t in ts]
    cv2.imwrite(out, cv2.cvtColor(np.vstack([np.hstack(tiles[:4]), np.hstack(tiles[4:] + [np.zeros_like(tiles[0])])]), cv2.COLOR_RGB2BGR))
else:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for n in range(int(dur * FPS)):
        enc.stdin.write(frame(n / FPS).tobytes())
    enc.stdin.close(); enc.wait()
    assert enc.returncode == 0, "encode failed"
print("ok")
