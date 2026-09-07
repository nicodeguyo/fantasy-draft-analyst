#!/usr/bin/env python3
"""Build the standalone skill deterministically, including its shared Python core."""
from pathlib import Path
import argparse
import os
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def build(output=None):
    source = ROOT / 'skills/fantasy-draft-analyst'
    output = Path(output or ROOT / 'dist/fantasy-draft-analyst.zip')
    output.parent.mkdir(parents=True, exist_ok=True)
    files = {}
    for path in sorted(source.rglob('*')):
        if any(part in {'__pycache__', '.git', '.venv'} for part in path.parts):
            continue
        if path.is_symlink():
            raise ValueError(f'Package may not depend on a symlink: {path}')
        if not path.is_file() or path.suffix in {'.pyc', '.pyo'} or path.name.startswith('.'):
            continue
        files['fantasy-draft-analyst/' + path.relative_to(source).as_posix()] = path.read_bytes()
    files['fantasy-draft-analyst/LICENSE'] = (ROOT / 'LICENSE').read_bytes()
    fd, temp = tempfile.mkstemp(dir=output.parent, suffix='.zip')
    os.close(fd)
    try:
        with zipfile.ZipFile(temp, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(files.items()):
                info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
        os.replace(temp, output)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    print(build(args.out))
