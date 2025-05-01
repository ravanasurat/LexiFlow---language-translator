import streamlit as st
import numpy as np
import pandas as pd
import pytesseract
from PIL import Image
import io
import os
import json
import datetime
from gtts import gTTS
from googletrans import Translator
import base64
import cv2
import docx2txt
import PyPDF2
from tempfile import NamedTemporaryFile

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.set_page_config(page_title="Multi-Modal Translation App", layout="wide")


if 'history' not in st.session_state:
    st.session_state.history = []

def save_to_history(source_text, translated_text, source_language, target_language, content_type, audio_bytes=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    history_item = {
        "timestamp": timestamp,
        "source_text": source_text[:500] + "..." if len(source_text) > 500 else source_text,
        "translated_text": translated_text[:500] + "..." if len(translated_text) > 500 else translated_text,
        "source_language": source_language if source_language else "Auto-detected",
        "target_language": target_language,
        "content_type": content_type,
        "full_source": source_text,
        "full_translation": translated_text,
        "has_audio": audio_bytes is not None
    }
    
    if audio_bytes:
        b64_audio = base64.b64encode(audio_bytes).decode()
        history_item["audio_b64"] = b64_audio

    st.session_state.history.insert(0, history_item)
    
    if len(st.session_state.history) > 50:
        st.session_state.history = st.session_state.history[:50]

def extract_text_from_image(image):
    try:

        img_np = np.array(image)
        

        if len(img_np.shape) == 3: 
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_np
            
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        denoised = cv2.medianBlur(binary, 3)
        
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(denoised, config=custom_config)
        
        return text
    except Exception as e:
        st.error(f"Error in OCR: {e}")
        return ""

def translate_text(text, target_language):
    try:
        if not text or text.strip() == "":
            return ""
            
        translator = Translator()
        
        if len(text) > 1000:
            chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
            translated_chunks = []
            
            for chunk in chunks:
                translation = translator.translate(chunk, dest=target_language)
                translated_chunks.append(translation.text)
            
            return ' '.join(translated_chunks)
        else:
            translation = translator.translate(text, dest=target_language)
            return translation.text
    except Exception as e:
        st.error(f"Translation error: {e}")
        st.info("If you're experiencing issues with Google Translate, try reinstalling the library with: pip install googletrans==3.1.0a0")
        return ""

def text_to_speech(text, language='en'):
    try:
        tts = gTTS(text=text, lang=language, slow=False)

        with NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_file = fp.name
            tts.save(temp_file)

        with open(temp_file, 'rb') as audio_file:
            audio_bytes = audio_file.read()

        os.unlink(temp_file)
        
        return audio_bytes
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")
        return None

# Function to get language code
def get_language_code(language_name):
    language_dict = {
        'English': 'en',
        'Spanish': 'es',
        'French': 'fr',
        'German': 'de',
        'Italian': 'it',
        'Portuguese': 'pt',
        'Russian': 'ru',
        'Japanese': 'ja',
        'Korean': 'ko',
        'Chinese (Simplified)': 'zh-cn',
        'Arabic': 'ar',
        'Hindi': 'hi',
        'Bengali': 'bn',
        'Tamil': 'ta',
        'Telugu': 'te'
    }
    return language_dict.get(language_name, 'en')

def get_audio_download_link(audio_bytes, filename="audio.mp3", text="Download Audio"):
    b64 = base64.b64encode(audio_bytes).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">{text}</a>'
    return href

def enhance_image_for_ocr(image):

    img_np = np.array(image)
    
    if len(img_np.shape) == 3:  
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_np
        

    threshold = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
 
    denoised = cv2.fastNlMeansDenoising(threshold, None, 10, 7, 21)
    

    enhanced_img = Image.fromarray(denoised)
    
    return enhanced_img


def extract_text_from_document(file):
    try:
        file_extension = os.path.splitext(file.name)[1].lower()
        
        if file_extension == '.pdf':
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text() + "\n"
            return text
            
        elif file_extension == '.docx':
            # Extract text from DOCX
            text = docx2txt.process(file)
            return text
            
        elif file_extension == '.txt':
            # Extract text from TXT
            text = file.getvalue().decode('utf-8')
            return text
            
        else:
            st.error(f"Unsupported file format: {file_extension}")
            return ""
            
    except Exception as e:
        st.error(f"Error extracting text from document: {e}")
        return ""

# App title and description
st.title("Multi-Modal Translation App")

tab1, tab2, tab3, tab4 = st.tabs(["Text Translation", "Image Translation", "Document Translation", "Translation History"])

with tab1:
    st.header("Text Translation")
    

    input_text = st.text_area("Enter text to translate:", height=150)

    source_language_name = st.selectbox(
        "Select source language (optional):",
        ['Auto-detect', 'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese', 
         'Russian', 'Japanese', 'Korean', 'Chinese (Simplified)', 'Arabic',
         'Hindi', 'Bengali', 'Tamil', 'Telugu']
    )
 
    target_language_name = st.selectbox(
        "Select target language:",
        ['English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese', 
         'Russian', 'Japanese', 'Korean', 'Chinese (Simplified)', 'Arabic',
         'Hindi', 'Bengali', 'Tamil', 'Telugu']
    )
    
    source_language = None if source_language_name == 'Auto-detect' else get_language_code(source_language_name)
    target_language = get_language_code(target_language_name)
    
    col1, col2 = st.columns(2)
    
    with col1:
        translate_button = st.button("Translate Text")
    
    with col2:
        audio_button = st.button("Generate Audio")
    
    if translate_button and input_text:
        # Translate the text
        translated_text = translate_text(input_text, target_language)
        
        if translated_text:
            st.subheader("Translation Result:")
            st.write(translated_text)
            
            # Store the translation in session state for audio generation
            st.session_state.last_translation = translated_text
            st.session_state.last_language = target_language
            
            # Save to history
            save_to_history(
                input_text, 
                translated_text, 
                source_language if source_language else "Auto-detected", 
                target_language, 
                "Text"
            )
    
    if audio_button and input_text:
        # Check if there's a translation in the session state
        if 'last_translation' in st.session_state:
            translated_text = st.session_state.last_translation
            target_language = st.session_state.last_language
        else:
            # Translate the text for audio
            translated_text = translate_text(input_text, target_language)
            
        if translated_text:
            st.subheader("Translation Result:")
            st.write(translated_text)
            
            # Generate audio from the translated text
            audio_bytes = text_to_speech(translated_text, target_language)
            
            if audio_bytes:
                st.audio(audio_bytes, format='audio/mp3')
                st.markdown(get_audio_download_link(audio_bytes), unsafe_allow_html=True)
                
                # Save to history with audio
                save_to_history(
                    input_text, 
                    translated_text, 
                    source_language if source_language else "Auto-detected", 
                    target_language, 
                    "Text (Audio)", 
                    audio_bytes
                )

with tab2:
    st.header("Image Translation")
    
    uploaded_file = st.file_uploader("Upload an image with text", type=["jpg", "jpeg", "png"])
    

    enhance_image = st.checkbox("Enhance image for better OCR", value=True)
    
    # Select target language for image
    img_target_language_name = st.selectbox(
        "Select target language for image text:",
        ['English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese', 
         'Russian', 'Japanese', 'Korean', 'Chinese (Simplified)', 'Arabic',
         'Hindi', 'Bengali', 'Tamil', 'Telugu'],
        key="img_language"
    )
    
    img_target_language = get_language_code(img_target_language_name)
    
    if uploaded_file is not None:
      
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption="Uploaded Image", use_column_width=True)
        
      
        if enhance_image:
            processed_image = enhance_image_for_ocr(image)
            with col2:
                st.image(processed_image, caption="Enhanced Image for OCR", use_column_width=True)
      
            extracted_text = extract_text_from_image(processed_image)
        else:
           
            extracted_text = extract_text_from_image(image)
        
        st.subheader("Extracted Text:")
        st.write(extracted_text if extracted_text else "No text detected in the image.")
        
        if extracted_text:

            corrected_text = st.text_area("Edit extracted text if needed:", extracted_text, height=150)
            
            
            img_translated_text = translate_text(corrected_text, img_target_language)
            
            st.subheader("Translated Text:")
            st.write(img_translated_text)
            
  
            img_audio_bytes = text_to_speech(img_translated_text, img_target_language)
            
            if img_audio_bytes:
                st.subheader("Audio Translation:")
                st.audio(img_audio_bytes, format='audio/mp3')
                st.markdown(get_audio_download_link(img_audio_bytes, "image_translation.mp3"), unsafe_allow_html=True)
                
                # Save to history with audio
                save_to_history(
                    corrected_text,
                    img_translated_text,
                    "Auto-detected",
                    img_target_language,
                    "Image (Audio)",
                    img_audio_bytes
                )
            else:
              
                save_to_history(
                    corrected_text,
                    img_translated_text,
                    "Auto-detected",
                    img_target_language,
                    "Image",
                    None
                )

with tab3:
    st.header("Document Translation")
    
    uploaded_doc = st.file_uploader("Upload a document (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    
    # Select target language for document
    doc_target_language_name = st.selectbox(
        "Select target language for document text:",
        ['English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese', 
         'Russian', 'Japanese', 'Korean', 'Chinese (Simplified)', 'Arabic',
         'Hindi', 'Bengali', 'Tamil', 'Telugu'],
        key="doc_language"
    )
    
    doc_target_language = get_language_code(doc_target_language_name)
    
    if uploaded_doc is not None:
        # Display file info
        st.write(f"File: {uploaded_doc.name} ({uploaded_doc.type})")
    
        extracted_doc_text = extract_text_from_document(uploaded_doc)
        
        if extracted_doc_text:
            st.subheader("Extracted Text:")
            
            # Show a preview (first 1000 characters)
            preview_text = extracted_doc_text[:1000] + "..." if len(extracted_doc_text) > 1000 else extracted_doc_text
            st.text_area("Document content preview:", preview_text, height=200, disabled=True)
            
            corrected_doc_text = st.text_area("Edit extracted text if needed:", extracted_doc_text, height=150)
            

            doc_translate_button = st.button("Translate Document")
            
            if doc_translate_button:
                doc_translated_text = translate_text(corrected_doc_text, doc_target_language)
                
                if doc_translated_text:
                    st.subheader("Translated Document Text:")
                
                    preview_translated = doc_translated_text[:10000] + "..." if len(doc_translated_text) > 10000 else doc_translated_text
                    st.text_area("Translation preview:", preview_translated, height=200)
                    
                    translated_file = doc_translated_text.encode('utf-8')
                    st.download_button(
                        label="Download full translation as TXT",
                        data=translated_file,
                        file_name=f"translated_{uploaded_doc.name.split('.')[0]}.txt",
                        mime="text/plain"
                    )
                    
                    # Generate audio from the translated text (preview only - first 3000 chars)
                    audio_preview_text = doc_translated_text[:10000] if len(doc_translated_text) > 10000 else doc_translated_text
                    doc_audio_bytes = text_to_speech(audio_preview_text, doc_target_language)
                    
                    if doc_audio_bytes:
                        st.subheader("Audio Translation (Preview):")
                        st.audio(doc_audio_bytes, format='audio/mp3')
                        st.markdown(get_audio_download_link(doc_audio_bytes, "document_translation_preview.mp3", "Download Preview Audio"), unsafe_allow_html=True)
                        
                        # Save to history
                        save_to_history(
                            f"Document: {uploaded_doc.name} (Preview)",
                            doc_translated_text,
                            "Auto-detected",
                            doc_target_language,
                            "Document (Audio)",
                            doc_audio_bytes
                        )
                    else:
                  
                        save_to_history(
                            f"Document: {uploaded_doc.name}",
                            doc_translated_text,
                            "Auto-detected",
                            doc_target_language,
                            "Document",
                            None
                        )
        else:
            st.error("Could not extract text from the document. Please check the file format and content.")

with tab4:
    st.header("Translation History")
    
    if not st.session_state.history:
        st.info("No translation history available. Start translating to see your history here!")
    else:
    
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export History"):
                export_history = []
                for item in st.session_state.history:
                    export_item = item.copy()
                    if "audio_b64" in export_item:

                        del export_item["audio_b64"]
                    export_history.append(export_item)
                

                json_str = json.dumps(export_history, indent=2)
                st.download_button(
                    label="Download History as JSON",
                    data=json_str,
                    file_name="translation_history.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("Clear History"):
                st.session_state.history = []
                st.rerun()

        for i, item in enumerate(st.session_state.history):
            with st.expander(f"{item['timestamp']} - {item['content_type']} ({item['source_language']} → {item['target_language']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Source:")
                    st.text_area(f"Source text {i}", item["source_text"], height=100, disabled=True)
                
                with col2:
                    st.markdown("#### Translation:")
                    st.text_area(f"Translated text {i}", item["translated_text"], height=100, disabled=True)
                
                button_col1, button_col2, button_col3 = st.columns(3)
                
                with button_col1:
 
                    if len(item["full_source"]) > 500 or len(item["full_translation"]) > 500:
                        if st.button(f"View Full Text #{i}"):
                            st.text_area("Full Source Text", item["full_source"], height=300)
                            st.text_area("Full Translation", item["full_translation"], height=300)
                
                with button_col2:
                    new_lang = st.selectbox(
                        f"Translate to another language #{i}",
                        ['English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese', 
                        'Russian', 'Japanese', 'Korean', 'Chinese (Simplified)', 'Arabic',
                        'Hindi', 'Bengali', 'Tamil', 'Telugu'],
                        key=f"new_lang_{i}"
                    )
                    
                    if st.button(f"Translate Again #{i}"):
                        new_lang_code = get_language_code(new_lang)
                        new_translation = translate_text(item["full_source"], new_lang_code)
                        if new_translation:

                            save_to_history(
                                item["full_source"],
                                new_translation,
                                item["source_language"],
                                new_lang,
                                f"Retranslation ({item['content_type']})"
                            )
                            st.success(f"Text retranslated to {new_lang}!")
                            st.experimental_rerun()
                
                with button_col3:
                    if item.get("has_audio") and "audio_b64" in item:
                        audio_data = base64.b64decode(item["audio_b64"])
                        st.audio(audio_data, format='audio/mp3')
                    elif st.button(f"Generate Audio #{i}"):
                        audio_bytes = text_to_speech(item["full_translation"], get_language_code(item["target_language"]))
                        if audio_bytes:
                            st.audio(audio_bytes, format='audio/mp3')
                            b64_audio = base64.b64encode(audio_bytes).decode()
                            st.session_state.history[i]["audio_b64"] = b64_audio
                            st.session_state.history[i]["has_audio"] = True