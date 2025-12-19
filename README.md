# 🔐 Multimedia Steganography Web Application

A full-stack Flask-based web application that allows users to securely hide and extract secret information inside **Images, Audio, and Video files** using **steganography techniques**.

This project integrates **Image, Audio, and Video steganography** into a single responsive web platform with **authentication, history tracking, and modern UI**.

---

## 🚀 Features

### 🔑 Authentication
- User Registration
- User Login & Logout
- Session management using Flask-Login

### 🖼️ Image Steganography
- Hide secret text inside **PNG images**
- Decode hidden text
- Decoded text is saved as a `.txt` file
- Uses **LSB (Least Significant Bit)** technique via `stegano` library

### 🔊 Audio Steganography
- Hide secret text inside **WAV audio files**
- Decode hidden data back to text
- Uses **LSB-based audio steganography**

### 🎥 Video Steganography
- Hide secret **text or files** inside videos
- Uses **lossless MKV container (FFV1 codec)** to preserve hidden data
- Decode only the generated `.mkv` file
- Robust handling of video frames using OpenCV

### 🗂️ History Tracking
- Logs all Encode / Decode operations
- User-specific history stored in database

### 🎨 UI & UX
- Card-based dashboard
- Icons (Font Awesome)
- Dark mode toggle
- Bootstrap-based responsive design
- Clear alerts and messages

---

## 🧠 Technologies Used

| Category | Technology |
|--------|------------|
| Backend | Flask, Flask-Login, Flask-SQLAlchemy |
| Frontend | HTML, CSS, Bootstrap 5 |
| Image Stego | `stegano`, Pillow |
| Audio Stego | Python Wave, NumPy |
| Video Stego | OpenCV, FFmpeg (FFV1 codec) |
| Database | SQLite |
| Version Control | Git & GitHub |

---

## 📂 Project Structure

Multimedia-Steganography/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── modules/
│ ├── image_steg/
│ ├── audio_steg/
│ └── video_steg/
│
├── templates/
│ ├── base.html
│ ├── dashboard.html
│ ├── image.html
│ ├── audio.html
│ ├── video.html
│ └── auth pages
│
├── static/
│ └── css/
│
├── instance/
│ └── stego.db
│
└── .gitignore



---

## ⚙️ Installation & Setup

### ✅ Prerequisites
- Python **3.9+**
- Git
- FFmpeg (for video steganography)

---

# 1. Clone the repository
git clone <your-github-repo-url>
cd Multimedia-Steganography

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 4. Install required dependencies
pip install -r requirements.txt

# 5. Run the Flask application
python app.py
