import streamlit as st
import os
from suno import Suno, ModelVersions
import base64
import requests

# Streamlit 應用設置
st.set_page_config(page_title="Suno AI Music Generator", page_icon="🎵")
st.title("Suno AI Music Generator")

# Suno 客戶端設置
@st.cache_resource
def get_suno_client():
    cookie = st.secrets.get("SUNO_COOKIE")
    if not cookie:
        st.error("SUNO_COOKIE is not set in the secrets. Please configure it in the Streamlit Cloud settings.")
        st.stop()
    return Suno(cookie=cookie, model_version=ModelVersions.CHIRP_V3_5)

try:
    client = get_suno_client()
except Exception as e:
    st.error(f"Failed to initialize Suno client: {str(e)}")
    st.stop()

# 用戶輸入
prompt = st.text_input("Enter a prompt for your music:", "A serene landscape")

if st.button("Generate Music"):
    try:
        with st.spinner("Generating music..."):
            songs = client.generate(prompt=prompt, is_custom=False, wait_audio=True)
        
        if songs:
            for i, song in enumerate(songs):
                st.success(f"Song {i+1} generated successfully!")
                
                # 下載歌曲
                try:
                    file_path = client.download(song=song)
                except Exception as e:
                    st.error(f"Failed to download song {i+1}: {str(e)}")
                    continue
                
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
            st.warning("No songs were generated. Please try a different prompt.")
    except requests.exceptions.RequestException as e:
        st.error(f"Network error occurred: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred while generating music: {str(e)}")
        st.info("Please check your Suno API credentials and ensure you have the necessary permissions.")

# 添加一些使用說明
st.markdown("""
## How to use:
1. Enter a prompt describing the kind of music you want.
2. Click 'Generate Music' to create your AI-generated song.
3. Listen to the generated music using the audio player.
4. Download the MP3 file if you like the result.

Note: Music generation may take a few minutes. Please be patient!
""")

# 添加錯誤報告功能
st.markdown("---")
st.subheader("Having issues?")
error_description = st.text_area("Describe the error you're experiencing:")
if st.button("Submit Error Report"):
    # 這裡你可以添加將錯誤報告發送到某個端點的邏輯
    st.success("Thank you for your report. We'll look into it.")
