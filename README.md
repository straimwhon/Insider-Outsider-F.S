# Insider-Outsider-F.S

This application performs real-time face detection and allows users to register their faces. It utilizes OpenCV for face detection and SQLite for storing user information.

## Features

- **Real-time Face Detection**: Detects faces using a webcam.
- **User Registration**: Allows users to register their face along with their student ID, first name, and last name.
- **Face Recognition**: Compares faces captured in real-time with the registered faces and identifies users.

## Installation

1. **Clone the repository**:
    ```bash
    git clone  https://github.com/straimwhon/Insider-Outsider-F.S.git
    cd facedetectionapp
    ```

2. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the application**:
    ```bash
    python face_detection_app.py
    ```

2. **Register a user**:
    - Click on the "REGISTER" button.
    - Fill in the Student ID, First Name, and Last Name in the registration form.
    - Capture your face using the webcam.
    - Submit the captured image.

3. **Face Detection**:
    - The application will continuously detect faces using the webcam.
    - If a registered face is detected, it will display the user's name.
    - If an unregistered face is detected, it will display "Outsider".

## Requirements

- Python 3.6+
- OpenCV
- NumPy
- Pillow
- Tkinter

 

