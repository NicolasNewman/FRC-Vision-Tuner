#!/bin/sh
pyinstaller --onefile --name="Vision Tuner" --noconfirm \
    --distpath=output/dist --workpath=output/build --specpath=output/spec \
    src/visionTuner.py
rm -rf __pycache__
cp src/visionTuner.ui output/dist/visionTuner.ui