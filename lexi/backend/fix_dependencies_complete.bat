@echo off
echo ========================================
echo LexiLearn Dependency Fix Script
echo ========================================
echo.

echo Step 1: Uninstalling problematic packages...
pip uninstall -y numpy tensorflow keras opencv-python transformers torch torchvision protobuf grpcio

echo.
echo Step 2: Installing tf-keras for compatibility...
pip install tf-keras==2.13.1

echo.
echo Step 3: Installing compatible versions...
pip install numpy==1.24.3
pip install protobuf==3.20.3
pip install grpcio==1.57.0
pip install tensorflow==2.13.0
pip install opencv-python==4.8.1.78
pip install transformers==4.30.2
pip install torch==2.0.1 torchvision==0.15.2

echo.
echo Step 4: Installing remaining requirements...
pip install -r requirements_fixed.txt

echo.
echo Step 5: Setting environment variables for compatibility...
set TF_ENABLE_ONEDNN_OPTS=0
set TF_CPP_MIN_LOG_LEVEL=2

echo.
echo ========================================
echo Dependency fix complete!
echo ========================================
echo.
echo To make environment variables permanent, add these to your system:
echo TF_ENABLE_ONEDNN_OPTS=0
echo TF_CPP_MIN_LOG_LEVEL=2
echo.
echo You can now run: python main.py
echo.
pause