# Demo media

The two 32-second MP4s share the same 1080×1350 (4:5), 25 fps visual edit:

- `draft-board-demo.mp4`: Michael’s AI narration, on-screen captions, and the selected upbeat electronic music.
- `draft-board-demo-no-narration.mp4`: on-screen captions and the same music without narration.
- `draft-board-demo.vtt`: English narration transcript for the website player.
- `draft-board-demo-poster.jpg`: opening comparison question, used as the cover.
- `draft-board-demo.gif`: 14-second silent tour for the README: seven captioned screens, two seconds each.

The footage shows the real saved comparison and board, with presentation reframed for a phone-sized video and editorial captions/highlights added. The evidence card summarizes the repository benchmark. The sample comparison is one illustrative draft; the +90 figure is the average internal policy comparison across 800 simulated drafts. Neither is a real-season performance claim. Marking picks records selections without recomputing recommendations.

Narration was generated locally with Kokoro v1.0, stock `am_michael` American English voice, through `kokoro-onnx` 0.4.7. No custom voice cloning was used. [Model card](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/README.md), [stock voice documentation](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md), [runtime](https://github.com/thewh1teagle/kokoro-onnx). Model/runtime binaries are not included in this repository.

The instrumental was composed and synthesized from scratch for this project, without third-party recordings or music samples. The selected composition uses brighter plucks and a 124 BPM rhythm. Both mixes fade at the end. The narrated mix lowers the music during speech.

File sizes, dimensions, durations and SHA-256 checksums are recorded in `manifest.json`.

`draft-board-story-silent.mp4` is the same 14-second seven-screen GIF sequence as a silent MP4. The final GIF screen says “Tested across 800 simulated drafts”; it refers to the internal benchmark, not the number of simulations behind every recommendation.
