# Replace the video background with a navy/neon-green backdrop (reference style).
# usage: python compose.py in.mov model.tflite out.mp4 [max_frames] [bg_video] [person_scale]
# bg_video: animated backdrop (anim.py); person_scale<1 shrinks the cut-out person, anchored bottom-centre.
import subprocess, sys
import numpy as np, cv2, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

src, model, dst = sys.argv[1:4]
limit = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] != "0" else None
bgvid = sys.argv[5] if len(sys.argv) > 5 else None
SC = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
W, H, FPS = 1080, 1920, 30

def backdrop():
    y = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array([18, 26, 52.]), np.array([8, 30, 22.])  # RGB navy -> deep green-navy
    bg = np.broadcast_to(top * (1 - y) + bot * y, (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    for cx, cy, r, col in [(900, 330, 420, (40, 220, 110)), (150, 1250, 380, (60, 90, 200))]:
        g = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r ** 2))[..., None]
        bg += g * np.array(col) * 0.35
    grid = ((xx % 90 == 0) | (yy % 90 == 0))[..., None]
    bg = np.where(grid, bg + 10, bg)
    return np.clip(bg, 0, 255).astype(np.float32)

bg = backdrop()
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=model),
    running_mode=vision.RunningMode.VIDEO, output_confidence_masks=True))

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"scale={W}:{H}", "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "fast",
                        "-pix_fmt", "yuv420p", dst], stdin=subprocess.PIPE)
bgdec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", bgvid, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE) if bgvid else None
prev, i = None, 0
while limit is None or i < limit:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    res = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=frame), i * 1000 // FPS)
    m = 1.0 - res.confidence_masks[0].numpy_view()  # 1 - background confidence
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)
    prev = m if prev is None else 0.5 * m + 0.5 * prev  # temporal smoothing against edge flicker
    # keep only the largest blob (the person) so ceiling lights / plants don't leak through
    n, lab, st, _ = cv2.connectedComponentsWithStats((prev > 0.5).astype(np.uint8))
    keep = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])) if n > 1 else np.ones_like(lab, bool)
    keep = cv2.dilate(keep.astype(np.uint8), np.ones((25, 25), np.uint8)).astype(np.float32)
    a = np.clip((cv2.GaussianBlur(prev * keep, (0, 0), 2) - 0.35) / 0.3, 0, 1)[..., None]
    if bgdec:
        b = bgdec.stdout.read(W * H * 3)
        cur = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32) if len(b) == W * H * 3 else bg
    else:
        cur = bg
    if SC != 1.0:  # shrink person + alpha, paste bottom-centre
        w2, h2 = int(W * SC), int(H * SC)
        f2 = np.zeros((H, W, 3), np.float32); a2 = np.zeros((H, W, 1), np.float32)
        f2[H - h2:, (W - w2) // 2:(W - w2) // 2 + w2] = cv2.resize(frame, (w2, h2), interpolation=cv2.INTER_AREA)
        a2[H - h2:, (W - w2) // 2:(W - w2) // 2 + w2, 0] = cv2.resize(a[..., 0], (w2, h2), interpolation=cv2.INTER_AREA)
        x = np.arange(w2, dtype=np.float32); ramp = np.clip(np.minimum(x, w2 - 1 - x) / 70, 0, 1)  # feather cut shoulder edges
        a2[H - h2:, (W - w2) // 2:(W - w2) // 2 + w2, 0] *= ramp[None, :]
        frame, a = f2, a2
    enc.stdin.write((frame * a + cur * (1 - a)).astype(np.uint8).tobytes())
    i += 1
enc.stdin.close(); enc.wait(); dec.kill()
if bgdec: bgdec.kill()
assert i > 0 and enc.returncode == 0, "no frames written"
print("frames", i)
