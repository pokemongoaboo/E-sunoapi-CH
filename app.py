import streamlit as st
import os
from suno import Suno, ModelVersions
import base64

# Streamlit 應用設置
st.set_page_config(page_title="Suno AI Music & Video Generator", page_icon="🎵")
st.title("Suno AI Music & Video Generator")

# Suno 客戶端設置
@st.cache_resource
def get_suno_client():
    cookie = st.secrets["SUNO_COOKIE"]
    return Suno(cookie=cookie)

client = get_suno_client()

# 用戶輸入
prompt = st.text_input("Enter a prompt for your music and video:", "A serene landscape with gentle piano music")

# 模型選擇
model_options = {
    "Chirp v1": ModelVersions.CHIRP_V1,
    "Bark v2": ModelVersions.BARK_V2,
    "Chirp v3.5": ModelVersions.CHIRP_V3_5
}
selected_model = st.selectbox("Choose a model:", list(model_options.keys()))

if st.button("Generate Music and Video"):
    try:
        with st.spinner("Generating music and video..."):
            results = client.generate(
                prompt=prompt, 
                model_version=model_options[selected_model],
                video_generation=True,
                duration=30,  # 設置視頻持續時間（秒）
                wait_audio=True,
                wait_video=True
            )
        
        if results:
            for i, result in enumerate(results):
                st.success(f"Music and Video {i+1} generated successfully!")
                
                # 下載音頻
                audio_path = client.download(result, audio_or_video='audio')
                
                # 下載視頻
                video_path = client.download(result, audio_or_video='video')
                
                # 讀取音頻文件
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()
                
                # 讀取視頻文件
                with open(video_path, "rb") as f:
                    video_bytes = f.read()
                
                # 在 Streamlit 中顯示音頻播放器
                st.audio(audio_bytes, format="audio/mp3")
                
                # 在 Streamlit 中顯示視頻播放器
                st.video(video_bytes)
                
                # 提供音頻下載鏈接
                st.download_button(
                    label=f"Download Audio {i+1}",
                    data=audio_bytes,
                    file_name=f"SunoMusic_{i+1}.mp3",
                    mime="audio/mp3"
                )
                
                # 提供視頻下載鏈接
                st.download_button(
                    label=f"Download Video {i+1}",
                    data=video_bytes,
                    file_name=f"SunoVideo_{i+1}.mp4",
                    mime="video/mp4"
                )
        else:
            st.error("Failed to generate music and video. Please try again.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# 添加一些使用說明
st.markdown("""
## How to use:
1. Enter a prompt describing the kind of music and video you want.
2. Choose a Suno AI model from the dropdown menu.
3. Click 'Generate Music and Video' to create your AI-generated content.
4. Listen to the generated music and watch the video using the embedded players.
5. Download the MP3 audio file or MP4 video file if you like the result.

Note: Music and video generation may take a few minutes. Please be patient!
""")
