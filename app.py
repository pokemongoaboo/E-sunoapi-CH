import streamlit as st
import os
from suno import Suno, ModelVersions
import base64

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
            
            # 創建一個唯一的鍵來存儲這首歌的狀態
            song_key = f"song_{i}"
            
            # 在 session_state 中初始化播放狀態
            if song_key not in st.session_state:
                st.session_state[song_key] = {
                    "playing": False,
                    "volume": 0.5,
                    "progress": 0
                }
            
            # 創建播放控件
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                play_button = st.button("▶️ Play" if not st.session_state[song_key]["playing"] else "⏸️ Pause", key=f"play_{i}")
                if play_button:
                    st.session_state[song_key]["playing"] = not st.session_state[song_key]["playing"]
            
            with col2:
                st.session_state[song_key]["progress"] = st.slider("Progress", 0.0, 100.0, st.session_state[song_key]["progress"], key=f"progress_{i}")
            
            with col3:
                st.session_state[song_key]["volume"] = st.slider("Volume", 0.0, 1.0, st.session_state[song_key]["volume"], key=f"volume_{i}")
            
            # 在 Streamlit 中顯示音頻播放器（隱藏，用於實際播放）
            st.audio(audio_bytes, format="audio/mp3", start_time=st.session_state[song_key]["progress"])
            
            # 提供下載鏈接
            st.download_button(
                label=f"Download Song {i+1}",
                data=audio_bytes,
                file_name=f"SunoMusic_{i+1}.mp3",
                mime="audio/mp3"
            )
            
            # 添加一些 JavaScript 來控制音頻播放
            audio_base64 = base64.b64encode(audio_bytes).decode()
            st.markdown(
                f"""
                <script>
                    var audio = new Audio("data:audio/mp3;base64,{audio_base64}");
                    audio.volume = {st.session_state[song_key]["volume"]};
                    audio.currentTime = {st.session_state[song_key]["progress"]};
                    audio.{'play()' if st.session_state[song_key]["playing"] else 'pause()'};
                </script>
                """,
                unsafe_allow_html=True
            )
    else:
        st.error("Failed to generate music. Please try again.")

# 添加一些使用說明
st.markdown("""
## How to use:
1. Enter a prompt describing the kind of music you want.
2. Click 'Generate Music' to create your AI-generated song.
3. Use the play/pause button, progress slider, and volume control to listen to your music.
4. Download the MP3 file if you like the result.

Note: Music generation may take a few minutes. Please be patient!
""")
