# Vision Tuner

The intent of this project is to aid in fine tuning values used for FRC Team 4500's vision pipeline.


## Installing

1) Navigate to this repo's [releases](https://github.com/NicolasNewman/FRC-Vision-Tuner/releases) and download the version for your system.
2) Extract the contents to a desired directory.
3) Run the executable

## Getting Started

**TODO**

## Prerequisites for building

If you wish to make changes to the project, the following are needed:

```sh
# 1) Make sure Python 3, pip3, and the Python3-dev are installed on your OS
# 2) Execute the following command:
pip3 install numpy opencv-python PyQt5 pyqt5-tools pyinstaller
```
## Building

Pyinstaller is used to build the executable files. To generate an executable for Windows, run *build_windows.bat*. To generate an executable for Linux, run *build_linux.sh*. The executable is stored in *output/dist/*

## Authors

* **Nicolas Newman** - *Initial work* - [NicolasNewman](https://github.com/NicolasNewman)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
