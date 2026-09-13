name: Build Android APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install System Dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y build-essential git ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev openjdk-17-jdk unzip wget expect

      - name: Install Buildozer and Cython
        run: |
          pip install --upgrade pip setuptools
          pip install "cython<3.0.0" buildozer

      - name: Build APK with Buildozer
        run: |
          expect -c '
          set timeout -1
          spawn buildozer -v android debug
          expect {
              "Accept? (y/N):" { send "y\r"; exp_continue }
              "Press y to accept" { send "y\r"; exp_continue }
              eof
          }
          '

      - name: Upload APK Artifact
        uses: actions/upload-artifact@v4
        with:
          name: BLOCK_IYAD_APK
          path: bin/*.apk
          if-no-files-found: error
