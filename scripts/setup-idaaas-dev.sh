#!/bin/bash

# Script to collect, set-up, build, and prepare all dependencies for GudPy development.
# Tested on ISIS Rocky8 images on IDAaaS
#
# Run from your home directory.

# Clone repositories
git clone https://github.com/disorderedmaterials/GudPy
git clone https://github.com/disorderedmaterials/ModEx
git clone https://github.com/disorderedmaterials/Gudrun

# Upgrade compiler
sudo yum install -y gcc-toolset-10

# Install missing basic dependencies
sudo dnf install -y cmake3 zlib-devel gsl-devel

# Enable powertools repo and install libaec-devel (required by HDF5)
sudo dnf --enablerepo=powertools install -y libaec-devel

# Install HDF5 development stuff and static libs
sudo dnf install -y hdf5-devel hdf5-static

# Fix PySide
sudo dnf install -y xcb-util-keysyms xcb-util-image
sudo dnf --enablerepo=powertools install -y xcb-util-wm-devel
sudo ln -s /usr/lib64/libxcb-util.so.1 /usr/lib64/libxcb-render-util.so.0

# Fix broken gcc
sudo ln -s /opt/rh/gcc-toolset-10/root/usr/lib/gcc/x86_64-redhat-linux/10/plugin/annobin.so /opt/rh/gcc-toolset-10/root/usr/lib/gcc/x86_64-redhat-linux/10/plugin/gcc-annobin.so

# Upgrade Python
sudo dnf module -y install python39
sudo alternatives --set python3 /usr/bin/python3.9

#
# MAIN BUILD
#

# Do everything else in separate shells with gcc-10

# Gudrun
scl enable gcc-toolset-10 -- << \GUDRUN
cd Gudrun
mkdir build && cd build
cmake ../ -DBUILD_SZIP:bool=true
cmake --build .
cmake --install . --prefix=$HOME/GudPy
GUDRUN

# ModEx
scl enable gcc-toolset-10 -- << \MODEX
cd ModEx
mkdir build && cd build
cmake ../
cmake --build .
cmake --install . --prefix=$HOME/GudPy
MODEX

# GudPy
cd GudPy
python3 -m pip install -r requirements.txt
pyside6-rcc gudpy/gui/widgets/resources/resources.qrc > gudpy/gui/widgets/resources/resources_rc.py
cp -r ../Gudrun/StartupFiles ./bin
