REM pyinstaller --onefile --name="Vision Tuner" --noconfirm ^
REM     --distpath=output/dist --workpath=output/build --specpath=output/spec ^
REM     --hidden-import="numpy.core._dtype_ctypes" ^
REM     src/visionTuner.py
rmdir /s /q "src/__pycache__/"
xcopy /y "src\visionTuner.ui" "output\dist"
xcopy /y /s "src\img\*" "output\dist\img\"