Reel pipeline (needs: ffmpeg, python venv with mediapipe/opencv/openai-whisper, selfie_multiclass_256x256.tflite from storage.googleapis.com/mediapipe-models).
1. Voice: ffmpeg highpass/afftdn/EQ/acompressor/loudnorm (-14 LUFS) -> voice.wav
2. Transcribe: whisper turbo, language=fa, word timestamps -> pick the 7 scene start times
3. anim.py out.mp4 "s1,...,s7" DURATION       -> animated backdrop
4. compose.py face.mov model.tflite bg.mp4 0 anim.mp4 0.72  -> person cut-out over backdrop
5. make_ass.py (captions/overlays), then ffmpeg ass + logo + voice.wav -> final mp4
Logo: logo_mgsina.png (Canva 'Modern Tech Logo with Grid Emblem'), logo_mgsina_cut.png = keyed overlay version. Default Instagram account: mgsina.tech. Always add logo + Persian captions.
