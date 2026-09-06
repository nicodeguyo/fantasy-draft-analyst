# Demo media

The two 32-second MP4s share the same 1080×1350 (4:5), 25 fps visual edit:

- `draft-board-demo.mp4`: AI narration, on-screen captions, and original music.
- `draft-board-demo-no-narration.mp4`: on-screen captions and the same music without narration.
- `draft-board-demo.vtt`: English narration transcript for the website player.
- `draft-board-demo-poster.jpg`: opening comparison question, used as the cover.
- `draft-board-demo.gif`: seven-second silent comparison loop for the README.

The footage shows the real saved comparison and board, with presentation reframed for a phone-sized video and editorial captions/highlights added. The evidence card summarizes the repository benchmark. The sample comparison is one illustrative draft; the +90 figure is the average internal policy comparison across 800 simulated drafts. Neither is a real-season performance claim. Marking picks records selections without recomputing recommendations.

Narration was generated locally with Kokoro v1.0, stock `af_heart` voice, through `kokoro-onnx` 0.4.7. No custom voice cloning was used. [Model card](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/README.md), [stock voice documentation](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md), [runtime](https://github.com/thewh1teagle/kokoro-onnx). Model/runtime binaries are not included in this repository.

The instrumental was composed and synthesized from scratch for this project, without third-party recordings or music samples. Both mixes fade at the end. The narrated mix lowers the music during speech.

File sizes, dimensions, durations and SHA-256 checksums are recorded in `manifest.json`.
