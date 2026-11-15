# Cut the avatar portrait out (RGBA, soft bottom fade) and make a round magenta-ringed profile version.
# usage: python avatar_prep.py avatar.png model.tflite out_cut.png out_round.png
import sys
import numpy as np, cv2, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

src, model, out_cut, out_round = sys.argv[1:5]
img = cv2.cvtColor(cv2.imread(src), cv2.COLOR_BGR2RGB)
h, w = img.shape[:2]
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.IMAGE, output_confidence_masks=True))
res = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=img))
m = cv2.resize(1.0 - res.confidence_masks[0].numpy_view(), (w, h), interpolation=cv2.INTER_CUBIC)
a = np.clip((cv2.GaussianBlur(m, (0, 0), 1.5) - 0.4) / 0.25, 0, 1)
n, lab, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8))
assert n > 1, "no person found"
a *= cv2.dilate((lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8), np.ones((9, 9), np.uint8))  # drop stray blobs
a *= np.clip((h - np.arange(h)) / (h * 0.12), 0, 1)[:, None]  # soft fade where the shirt is cut off
a *= np.clip(np.minimum(np.arange(w), w - 1 - np.arange(w)) / (w * 0.07), 0, 1)[None, :]  # feather cut shirt sides
cv2.imwrite(out_cut, cv2.cvtColor(np.dstack([img, (a * 255).astype(np.uint8)]), cv2.COLOR_RGBA2BGRA))

# round profile picture: square crop around the face + magenta ring
cx, cy, s = 590, 560, 400
crop = cv2.resize(img[cy - s:cy + s, cx - s:cx + s], (400, 400), interpolation=cv2.INTER_AREA)
yy, xx = np.mgrid[0:400, 0:400]; d = np.hypot(xx - 199.5, yy - 199.5)
alpha = np.clip(200 - d, 0, 1)
ring = np.clip(1 - np.abs(d - 190) / 10, 0, 1)[..., None]
rgb = crop * (1 - ring) + np.array([224, 36, 117]) * ring
cv2.imwrite(out_round, cv2.cvtColor(np.dstack([rgb, alpha[..., None] * 255]).astype(np.uint8), cv2.COLOR_RGBA2BGRA))
print("ok")
