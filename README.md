# ⚽ Football Tracking and Analysis System

![Project Banner](https://github.com/khanhprt/football_tracking_and_analysis/raw/main/docs/banner.png)

A comprehensive computer vision solution for automated football match analysis with player tracking, tactical insights, and performance metrics.

## ✨ Key Features

| Feature Category | Description |
|-----------------|-------------|
| **Real-time Tracking** | Multi-player detection with YOLO + DeepSORT |
| **Tactical Analysis** | Team formations, passing networks, heatmaps |
| **Performance Metrics** | Distance covered, speed, sprint stats |
| **Video Processing** | Support for 4K match footage at 60fps |
| **Data Export** | CSV, JSON, and video overlays |

## 🚀 Quick Installation

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/khanhprt/football_tracking_and_analysis.git

# Setup environment
conda create -n football_analysis python=3.8
conda activate football_analysis
pip install -r requirements.txt

# Download pretrained models
python scripts/download_models.py
