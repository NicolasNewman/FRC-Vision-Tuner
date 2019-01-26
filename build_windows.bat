pyinstaller --onefile --name="Vision Tuner" --noconfirm ^
    --distpath=output/dist --workpath=output/build --specpath=output/spec ^
    --hidden-import="numpy.core._dtype_ctypes" ^
    src/visionTuner.py
rmdir /s /q "src/__pycache__/"
xcopy /y "src\visionTuner.ui" "output\dist"
xcopy /y /s "src\img\*" "dist\img"