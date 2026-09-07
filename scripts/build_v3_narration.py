#!/usr/bin/env python3
"""Optional audio regeneration: stock Kokoro am_michael, no custom voice cloning.
Usage: python scripts/build_v3_narration.py /path/to/kokoro-model-directory
Requires kokoro-onnx, numpy, scipy, soundfile, ffmpeg. Media rebuilds can use the
committed narration FLAC without these optional development dependencies.
"""
import json,sys,tempfile,subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from kokoro_onnx import Kokoro
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/media/source';SR=48000
model=Path(sys.argv[1]);engine=Kokoro(str(model/'kokoro-v1.0.onnx'),str(model/'voices-v1.0.bin'))
beats=json.loads((OUT/'storyboard.json').read_text());voice=np.zeros(SR*36);audit=[]
with tempfile.TemporaryDirectory() as temp:
 for i,b in enumerate(beats):
  y,sr=engine.create(b['voice'],voice='am_michael',speed=1.04,lang='en-us')
  duration=len(y)/sr;budget=b['end']-b['start']-.4;tempo=max(1,duration/budget)
  if tempo>1.35:raise ValueError(f'Segment {i} needs shorter copy: tempo {tempo}')
  if tempo>1:
   a=Path(temp)/'raw.wav';f=Path(temp)/'fit.wav';sf.write(a,y,sr)
   subprocess.run(['ffmpeg','-v','error','-y','-i',str(a),'-af',f'atempo={tempo}',str(f)],check=True)
   y,sr=sf.read(f)
  y=resample_poly(y,SR,sr);y*=.63/max(abs(y));start=round((b['start']+.15)*SR)
  assert start+len(y)<=round(b['end']*SR)
  voice[start:start+len(y)]+=y
  audit.append(dict(segment=i+1,raw_seconds=duration,tempo=tempo,spoken_start=start/SR,spoken_end=(start+len(y))/SR))
  print(audit[-1],flush=True)
sf.write(OUT/'michael-narration.flac',voice,SR,subtype='PCM_24')
(OUT/'narration-timing.json').write_text(json.dumps(audit,indent=2)+'\n')
