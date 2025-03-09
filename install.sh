#!/bin/bash

# Kiểm tra quyền sudo
if [ "$EUID" -ne 0 ]; then
    echo "Bạn cần phải có quyền root để chạy script này."
    exit 1
fi

sudo chmod -R 777 /home/user/

# Cài đặt thư viện venv cho ubuntu
sudo apt-get update && sudo apt-get install python3-venv

# Tạo một môi trường ảo tên myenv bằng venv
echo "Khởi tạo môi trường ảo myenv"
python3 -m venv myenv
# Kích hoạt môi trường ảo
source /home/user/myenv/bin/activate

# Tạo 1 thư mục
mkdir /home/user/football-ai
cd /home/user/football-ai

# clone file từ git vào thư mục vừa tạo
git clone https://github.com/khanhprt/football-project-v1.git

# chuyển sang thư mục project
cd /home/user/football-ai/football-project-v1

# cài đặt các phụ thuộc cần thiết
/home/user/myenv/bin/pip install -r requirements.txt

yes | /home/user/myenv/bin/pip uninstall opencv-python
/home/user/myenv/bin/pip install opencv-python-headless

# Cài đặt gdown nếu chưa có
if ! command -v gdown &> /dev/null; then
    echo "Gdown không được tìm thấy. Cài đặt..."
    pip install gdown
fi

# Tải yolov8x-football.pt từ drive
FILE_URL_MODEL_FB="https://drive.google.com/uc?id=1JS8hpKHkERWGEsIQK7UPCg16O_5IFRmN"
FILE_NAME_MODEL_FB="yolov8x-football.pt"
INPUT_DIR_MODEL_FB="/home/user/football-ai/football-project-v1/models"

# Kiểm tra nếu chưa tồn tại thì tạo mới
if [ ! -d "$INPUT_DIR_MODEL_FB" ]; then
    mkdir "$INPUT_DIR_MODEL_FB"
fi

# Tải file từ Google Drive
echo "Bắt đầu tải yolov8x-football..."
gdown -O "$INPUT_DIR_MODEL_FB/$FILE_NAME_MODEL_FB" "$FILE_URL_MODEL_FB"
echo "Tải model thành công! Model sẽ được lưu trong thư mục models."

# Tải key_points_pitch_ver2.pt từ drive
FILE_URL_MODEL_KP="https://drive.google.com/uc?id=1ul_FCU03J2PYiup-WTgcW5YcUHlDrmLY"
FILE_NAME_MODEL_KP="key_points_pitch_ver2.pt"
INPUT_DIR_MODEL_KP="/home/user/football-ai/football-project-v1/models"

# Kiểm tra nếu chưa tồn tại thì tạo mới
if [ ! -d "$INPUT_DIR_MODEL_KP" ]; then
    mkdir "$INPUT_DIR_MODEL_KP"
fi

# Tải file từ Google Drive
echo "Bắt đầu tải input..."
gdown -O "$INPUT_DIR_MODEL_KP/$FILE_NAME_MODEL_KP" "$FILE_URL_MODEL_KP"
echo "Tải model thành công! Model sẽ được lưu trong thư mục models."


# Tải video outputs từ drive
FILE_URL="https://drive.google.com/uc?id=1RDTNqZMxbZIOYGRaBaUYz6R2d07QG3vH"
FILE_NAME="ok_798b45_0.mp4"
INPUT_DIR="/home/user/football-ai/football-project-v1/inputs"

# Kiểm tra nếu chưa tồn tại thì tạo mới
if [ ! -d "$INPUT_DIR" ]; then
    mkdir "$INPUT_DIR"
fi

# Tải file từ Google Drive
echo "Bắt đầu tải input..."
gdown -O "$INPUT_DIR/$FILE_NAME" "$FILE_URL"
echo "Tải input thành công! Input sẽ được lưu trong thư mục inputs."

echo "Re-build opecvn export .mp4"
sudo chmod -R 777 /home/user/
# Kích hoạt môi trường ảo
source /home/user/myenv/bin/activate

# Gỡ cài đặt OpenCV nếu có
yes | /home/user/myenv/bin/pip uninstall opencv-python
yes | /home/user/myenv/bin/pip uninstall opencv-contrib-python

# Cài đặt các thư viện cần thiết
sudo apt install build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev python3-dev python3-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-dev
# Clone OpenCV và OpenCV Contrib
cd /home/user/
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git

# Tạo thư mục build
cd /home/user/opencv
mkdir /home/user/opencv/build
cd /home/user/opencv/build

# Cấu hình CMake
cmake -D WITH_FFMPEG=ON -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules -D PYTHON3_EXECUTABLE=$(which python3) -D PYTHON3_INCLUDE_DIR=$(python3 -c "import sysconfig; print(sysconfig.get_path('include'))") -D PYTHON3_PACKAGES_PATH=$(python3 -c "import site; print(site.getsitepackages()[0])") ..

# Biên dịch OpenCV
make -j$(nproc)

# Cài đặt OpenCV
sudo make install