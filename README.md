# 🌐 Multi-Modal Translation App

A user-friendly **Streamlit-based web application** that allows users to extract text from various input sources (text, image, document), translate it into multiple languages, and optionally convert the translated text to speech (TTS). This app is ideal for travelers, language learners, educators, and accessibility tools.

## 🚀 Features

- ✅ Translate plain text input in real-time
- 🖼️ Extract and translate text from images using OCR (Tesseract)
- 📄 Upload and translate documents (PDF, DOCX, TXT)
- 🔈 Convert translated text to speech (TTS) using gTTS
- 🧠 Auto-detect or manually select source and target languages
- 🕓 Maintains a session-based history of translations
- 🔊 Audio download link for translated speech
- 💡 Streamlit interface with modern UX


## 📁 Supported Input Formats

- **Text**: Manual text input
- **Image**: `.png`, `.jpg`, `.jpeg`
- **Documents**: `.pdf`, `.docx`, `.txt`



## 🛠️ Installation

### 🔗 Prerequisites

- Python 3.8+
- Tesseract-OCR installed on your system  
  Download from: https://github.com/tesseract-ocr/tesseract

### 📦 Dependencies

Install required libraries using pip:

```bash
pip install streamlit numpy pandas pytesseract pillow gTTS googletrans==3.1.0a0 opencv-python PyPDF2 python-docx


### Run the App
streamlit run app.py

###Future Enhancements
Speech-to-text support

Multi-language document translation

Dark mode UI

Save/export full translation history

Cloud storage integration


For collabortion , contact me :
mail id : mahesh.v2022ai-ds@sece.ac.in
