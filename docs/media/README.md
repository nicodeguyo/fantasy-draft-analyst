# Current v3 media

The current tour restores the original navy/lime visual identity, stock Michael narrator, upbeat instrumental, and a 15-second README GIF. Its six scenes explain the draft benefit, the +66 comparison, a lost target, the Walker next-pick decision, the 793/800 result, and setup.

- `v3-tour.gif`: 15-second silent loop, 480×600, used in the README.
- `v3-walkthrough.mp4`: 36-second narrated 1080×1350 tour with original music and embedded on-screen captions.
- `v3-walkthrough-music-only.mp4`: same visuals and music, without narration.
- `v3-walkthrough.vtt`: English narration captions.
- `v3-video-poster.png`: benchmark cover for the prominent website video.
- `v3-decision.png`: updated shortlist image.
- `social-preview-v3.png`: 1280×640 benchmark social card.
- `v3-manifest.json`: exported file hashes and sizes.

The figures come from the public [benchmark](../../examples/v3-benchmark/README.md) and [next-turn comparison](../../examples/v3-benchmark/next-turn-800.json). They are simulated projected results. No private draft information appears in these assets.

## Rebuild

Install Playwright and Chromium in a development environment and put ffmpeg on PATH. From the repository root:

```bash
python scripts/build_v3_demo.py
node scripts/build_v3_media.cjs
```

Set `NODE_PATH` if Playwright lives outside the repository. These are optional media-development dependencies, not skill or website runtime requirements.

The media builder uses committed audio in `source/`: the original upbeat composition and the updated Michael narration. `storyboard.json` holds the spoken script, on-screen captions, and timings. To regenerate narration, use `scripts/build_v3_narration.py /path/to/models` with kokoro-onnx, scipy, numpy, and soundfile installed. The model folder must contain `kokoro-v1.0.onnx` and `voices-v1.0.bin`. `narration-timing.json` records speech fit. Playback is user-controlled; the short GIF loops.

The narrator is the stock Kokoro `am_michael` voice, not a cloned real person. [Model information](https://huggingface.co/hexgrad/Kokoro-82M). The instrumental is the original upbeat composition used in the previous launch video, without third-party samples.

---

# Archived v2 media

The two 32-second MP4s share the same 1080×1350 (4:5), 25 fps visual edit:

- `draft-board-demo.mp4`: Michael’s AI narration, on-screen captions, and the selected upbeat electronic music.
- `draft-board-demo-no-narration.mp4`: on-screen captions and the same music without narration.
- `draft-board-demo.vtt`: English narration transcript for the website player.
- `draft-board-demo-poster.jpg`: opening comparison question, used as the cover.
- `draft-board-demo.gif`: 15-second silent tour for the README: a two-second opening comparison, five two-second benefit/proof views, and a three-second skill download invitation.

The footage shows the real saved comparison and board, with presentation reframed for a phone-sized video and editorial captions/highlights added. The evidence card summarizes the repository benchmark. The sample comparison is one illustrative draft; the +90 figure is the average internal policy comparison across 800 simulated drafts. Neither is a real-season performance claim. Marking picks records selections without recomputing recommendations.

Narration was generated locally with Kokoro v1.0, stock `am_michael` American English voice, through `kokoro-onnx` 0.4.7. No custom voice cloning was used. [Model card](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/README.md), [stock voice documentation](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md), [runtime](https://github.com/thewh1teagle/kokoro-onnx). Model/runtime binaries are not included in this repository.

The instrumental was composed and synthesized from scratch for this project, without third-party recordings or music samples. The selected composition uses brighter plucks and a 124 BPM rhythm. Both mixes fade at the end. The narrated mix lowers the music during speech.

File sizes, dimensions, durations and SHA-256 checksums are recorded in `manifest.json`.

`draft-board-story-silent.mp4` is the same 15-second GIF sequence as a silent MP4. The evidence screen refers to 800 simulated drafts in the internal benchmark, not the number of simulations behind every recommendation. The closing screen and video narration invite viewers to download the skill and build their own plan with Claude.
