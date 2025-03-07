#!/bin/bash

# Kiểm tra quyền sudo
if [ "$EUID" -ne 0 ]; then
    echo "Bạn cần phải có quyền root để chạy script này."
    exit 1
fi

# Kích hoạt môi trường ảo
source /home/user/myenv/bin/activate

# Gỡ cài đặt OpenCV nếu có
yes | /home/user/myenv/bin/pip uninstall opencv-python
yes | /home/user/myenv/bin/pip uninstall opencv-contrib-python

# Cài đặt các thư viện cần thiết
sudo apt update && sudo apt install -y \
    build-essential cmake git libgtk2.0-dev pkg-config \
    libavcodec-dev libavformat-dev libswscale-dev \
    python3-dev python3-numpy libtbb2 libtbb-dev \
    libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev

# Clone OpenCV và OpenCV Contrib
cd /home/user/
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git

# Tạo thư mục build
cd /home/user/opencv
mkdir /home/user/opencv/build
cd /home/user/opencv/build

# Cấu hình CMake
cmake -D WITH_FFMPEG=ON \
      -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
      -D PYTHON3_EXECUTABLE=$(which python3) \
      -D PYTHON3_INCLUDE_DIR=$(python3 -c "import sysconfig; print(sysconfig.get_path('include'))") \
      -D PYTHON3_PACKAGES_PATH=$(python3 -c "import site; print(site.getsitepackages()[0])") ..

# Biên dịch OpenCV
make -j$(nproc)

# Cài đặt OpenCV
sudo make install