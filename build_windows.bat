pyinstaller --onefile --name="Vision Tuner" --noconfirm --noconsole ^
    --distpath=output/dist --workpath=output/build --specpath=output/spec ^
    src/visionTuner.py
rmdir /s /q "src/__pycache__/"
xcopy /y "src\visionTuner.ui" "output\dist"
xcopy /y /s "src\img\*" "output\dist\img\"