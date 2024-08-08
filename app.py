import time
import streamlit as st
from suno import Suno, ModelVersions

MAX_TITLE_LENGTH = 100
CHECK_INTERVAL = 5  # 檢查間隔秒數

def initialize_suno_client():
    try:
        return Suno(
            cookie=st.secrets["SUNO_COOKIE"],
            model_version=ModelVersions.CHIRP_V3_5
        )
    except Exception as e:
        st.error(f"初始化Suno客戶端時出錯: {str(e)}")
        return None

def generate_music(suno_client, lyrics, theme):
    try:
        clips = suno_client.generate(
            prompt=lyrics,
            tags="六十年代台語歌曲風, 台語男歌手, 台灣話, 台語歌",
            title=theme[:MAX_TITLE_LENGTH],
            make_instrumental=False,
            is_custom=True,
            wait_audio=True
        )
        if clips:
            return clips[0]
    except Exception as e:
        st.error(f"生成歌曲時發生錯誤: {str(e)}")
    return None

def check_video_url(suno_client, clip_id):
    try:
        songs = suno_client.get_songs(song_ids=f"{clip_id}")
        if songs and len(songs) > 0:
            return songs[0].video_url
    except Exception as e:
        st.error(f"檢查視頻URL時發生錯誤: {str(e)}")
    return None

def main():
    st.title("Suno音樂生成與視頻URL等待器")

    # 使用 session_state 來保存狀態
    if 'clip' not in st.session_state:
        st.session_state.clip = None
    if 'video_url' not in st.session_state:
        st.session_state.video_url = None

    lyrics = st.text_area("請輸入歌詞", height=150)
    theme = st.text_input("請輸入主題")

    suno_client = initialize_suno_client()
    if suno_client:
        credits_info = suno_client.get_credits()
        st.write(credits_info)

    if st.button("生成音樂"):
        if lyrics and theme:
            if not suno_client:
                return
            with st.spinner('正在生成音樂...'):
                st.session_state.clip = generate_music(suno_client, lyrics, theme)
                if not st.session_state.clip:
                    st.error('音樂生成失敗')
                    return
            st.success(f'音樂生成成功! Clip ID: {st.session_state.clip.id}')
            st.audio(st.session_state.clip.audio_url, format='audio/mp3')
            
            st.session_state.video_url = None
            placeholder = st.empty()
            while not st.session_state.video_url:
                placeholder.info('影片生成中，請稍候...')
                st.session_state.video_url = check_video_url(suno_client, st.session_state.clip.id)
                if not st.session_state.video_url:
                    time.sleep(CHECK_INTERVAL)
            placeholder.success(f'影片已生成: {st.session_state.video_url}')
        else:
            st.error("請輸入歌詞和主題")

    # 當 video_url 存在時顯示播放按鈕
    if st.session_state.video_url:
        if st.button('播放影片'):
            video_html = f"""
                <video controls width="100%">
                <source src="{st.session_state.video_url}" type="video/mp4">
                您的浏览器不支持video标签。
                </video>
            """
            st.markdown(video_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
