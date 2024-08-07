import streamlit as st
import os
from suno import Suno, ModelVersions

# Streamlit 應用設置
st.set_page_config(page_title="Suno AI Music Generator", page_icon="🎵")
st.title("Suno AI Music Generator")

# Suno 客戶端設置
@st.cache_resource
def get_suno_client():
    cookie = st.secrets["SUNO_COOKIE"]
    return Suno(cookie=cookie, model_version=ModelVersions.CHIRP_V3_5)

client = get_suno_client()

# 用戶輸入
prompt = st.text_input("Enter a prompt for your music:", "A serene landscape")

if st.button("Generate Music"):
    with st.spinner("Generating music..."):
        songs = client.generate(prompt=prompt, is_custom=False, wait_audio=True)
        
    if songs:
        for i, song in enumerate(songs):
            st.success(f"Song {i+1} generated successfully!")
            
            # 下載歌曲
            file_path = client.download(song=song)
            
            # 讀取音樂文件
            with open(file_path, "rb") as f:
                audio_bytes = f.read()
            
            # 在 Streamlit 中顯示音頻播放器
            st.audio(audio_bytes, format="audio/mp3")
            
            # 提供下載鏈接
            st.download_button(
                label=f"Download Song {i+1}",
                data=audio_bytes,
                file_name=f"SunoMusic_{i+1}.mp3",
                mime="audio/mp3"
            )
    else:
        st.error("Failed to generate music. Please try again.")

# 添加一些使用說明
st.markdown("""
## How to use:
1. Enter a prompt describing the kind of music you want.
2. Click 'Generate Music' to create your AI-generated song.
3. Listen to the generated music using the audio player.
4. Download the MP3 file if you like the result.

Note: Music generation may take a few minutes. Please be patient!
""")
