import cv2
import dehazing_algorithm as alg
import time
import numpy as np
from PIL import Image
import streamlit as st
import tempfile
from moviepy.editor import ImageSequenceClip
import os

def dehaze_image(image):
    cap = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    start_time = time.time()
    output = alg.dehaze_frame(cap, 4, 8) * 255
    end_time = time.time()
    total_time = end_time - start_time
    output = output.astype(np.uint8)
    return Image.fromarray(cv2.cvtColor(output, cv2.COLOR_BGR2RGB)), total_time

def dehaze_video(file_buffer):
    skip = 1
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(file_buffer.read())
    cap = cv2.VideoCapture(tfile.name)

    if not cap.isOpened():
        st.error("Error: Could not open video")
        return

    frames = []
    dehazed_frames = []

    with st.spinner("Processing video..."):
        i=0
        while cap.isOpened():
            success, frame = cap.read()
            if i % skip == 0:
                if not success:
                    break
                frames.append(frame)
                dehazed_frame = alg.dehaze_frame(frame, 5, n=8) * 255
                dehazed_frames.append(dehazed_frame.astype(np.uint8))
            i += 1

    cap.release()
    
    if frames:
        st.subheader("Original Video")
        st.video(tfile.name)

        st.subheader("Dehazed Video")
        
        dehazed_frames_rgb = [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in dehazed_frames]
        clip = ImageSequenceClip(dehazed_frames_rgb, fps=30)
        
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        output_filename = output_file.name
        output_file.close()
        
        clip.write_videofile(output_filename, codec='libx264')
        
        with open(output_filename, "rb") as file:
            video_bytes = file.read()
        st.video(video_bytes)

    else:
        st.error("No frames were processed from the video.")

st.set_page_config(page_title="Dehazing App", page_icon="🌫️", layout="wide")
st.title("Dehazing System")

st.sidebar.title("Options")
app_mode = st.sidebar.selectbox("Choose the mode", ["Upload Image", "Upload Video", "Realtime Dehazing"])

if app_mode == "Upload Image":
    st.subheader("Upload Image to be Dehazed")
    uploaded_image = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg", "gif"])
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Original Image", use_column_width=True)
        
        if st.button("Dehaze Image"):
            dehazed_image, processing_time = dehaze_image(image)
            st.image(dehazed_image, caption="Dehazed Image", use_column_width=True)
            st.write(f"Time taken to dehaze: {processing_time:.2f} seconds")
            
elif app_mode == "Upload Video":
    st.subheader("Upload Video to be Dehazed")
    uploaded_video = st.file_uploader("Choose a video...", type=["mp4", "avi", "mkv"])
    if uploaded_video is not None:
        if st.button("Dehaze Video"):
            dehaze_video(uploaded_video)

elif app_mode == "Realtime Dehazing":
    st.subheader("Realtime Dehazing")
    # dehaze_realtime()
    st.write("For realtime dehazing, please download our desktop application:")
    st.markdown("[Download Desktop App](https://github.com/chhaviGupta986/Dehazing-Software/releases/tag/v1.0.0)")


st.markdown("""
    <style>
    .stApp {
        background: #1c1c1c;
        color: white;
    }
    .css-1offfwp, .css-1offfwp:visited {
        color: white;
        text-decoration: none;
    }
    </style>
""", unsafe_allow_html=True)
