# Kiểm tra quyền sudo
if [ "$EUID" -ne 0 ]; then
    echo "Bạn cần phải có quyền root để chạy script này."
    exit 1
fi

# Cài đặt thư viện venv cho ubuntu
sudo apt-get update && sudo apt-get install python3-venv

# Tạo một môi trường ảo tên myenv bằng venv
echo "Khởi tạo môi trường ảo myenv"
python3 -m venv myenv
# Kích hoạt môi trường ảo
source myenv/bin/activate

# Tạo 1 thư mục
mkdir /football-ai
cd /football-ai

# clone file từ git vào thư mục vừa tạo
git clone https://github.com/khanhprt/football-project-v1.git

# chuyển sang thư mục project
cd football-project-v1

# cài đặt các phụ thuộc cần thiết
pip install -r requirements.txt

yes | pip uninstall opencv-python
pip install opencv-python-headless

# Cài đặt gdown nếu chưa có
if ! command -v gdown &> /dev/null; then
    echo "Gdown không được tìm thấy. Cài đặt..."
    pip install gdown
fi

FOLDER_ID="1mTlpX9Y3IFmfLAMZV82Iw--xsrbquBou"
# Thư mục đích là thư mục models trong football-project-v1
MODEL_DIR="/models"

# Kiểm tra nếu chưa tồn tại thì tạo mới
if [ ! -d "$MODEL_DIR" ]; then
    mkdir "$MODEL_DIR"
fi

# Tải các file từ Google Drive
gdown --folder "https://drive.google.com/drive/folders/$FOLDER_ID" -O "$MODEL_DIR"
echo "Tải dữ liệu thành công! Dữ liệu sẽ được lưu trong thư mục models."


# Đặt ID của tệp Google Drive và tên tệp muốn tải
FILE_URL="https://drive.google.com/uc?id=12TqauVZ9tLAv8kWxTTBFWtgt2hNQ4_ZF"
FILE_NAME="0bfacc_0.mp4"
INPUT_DIR="/inputs"

# Kiểm tra nếu chưa tồn tại thì tạo mới
if [ ! -d "$INPUT_DIR" ]; then
    mkdir "$INPUT_DIR"
fi

# Tải file từ Google Drive
echo "Bắt đầu tải input..."
gdown -O "$INPUT_DIR/$FILE_NAME" "$FILE_URL"
echo "Tải input thành công! Input sẽ được lưu trong thư mục inputs."