# Environment Setup
Contains information on setting up and troubleshooting the development environment.

## Cloning
- Clone with `git clone --recurse-submodules https://github.com/Genisis2/nus_cs5246_project.git` to pull the `facebook/access` repository as a submodule

## Conda Virtual Env
- Optionally create an Anaconda environment for the project with `conda env create -f environment.yaml && conda activate nus_cs5246_project`
  
## Python Package Requirements
- Install python requirements with `pip install -r requirements.txt`
    - Installs the non-CUDA `torch` by default. Use the `requirements-cuda.txt` file to install CUDA-accelerated `torch` if preferred.
- Potential issues
    - If having issues installing `git://github.com/feralvam/easse.git` from submodule, need to setup a redirect in git since the `git://` protocol is phased out in GitHub. Run `git config --global url.https://github.com/.insteadOf git://github.com/` to setup redirect.
    - If you encounter a Windows error, need to install Visual C++ 14.0 devkit on your system (ref: https://www.scivision.dev/python-windows-visual-c-14-required/)
        - Download build tools from https://visualstudio.microsoft.com/visual-cpp-build-tools/
        - Run the `.exe`
        - Tick `Desktop Development with C++` -> In the side panel, untick all Optional installations -> Tick `MSVC v143 - VS 2022 C++ x64/x86 build tools` -> Tick `Windows 11 SDK`
        - Click `Install`. This will install around 8GB