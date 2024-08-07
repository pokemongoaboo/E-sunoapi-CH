import time
import streamlit as st
from suno import Suno, ModelVersions

MAX_RETRIES = 60  # 最大重試次數
RETRY_DELAY = 10  # 每次重試間隔秒數
MAX_TITLE_LENGTH = 100  # 最大標題長度

def initialize_suno_client():
    return Suno(
        cookie=st.secrets["SUNO_COOKIE"],
        model_version=ModelVersions.CHIRP_V3_5
    )

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

def wait_for_video_url(suno_client, clip_id):
    retries = 0
    
    while retries < MAX_RETRIES:
        all_clips = suno_client.get_clips()
        clip = next((c for c in all_clips if c.id == clip_id), None)
        
        if clip:
            if clip.video_url:
                return clip.video_url
            elif not clip.is_video_pending:
                st.warning("視頻處理完成，但URL不可用")
                return None
        else:
            st.warning(f"無法找到ID為 {clip_id} 的clip")
            return None
        
        retries += 1
        remaining_time = (MAX_RETRIES - retries) * RETRY_DELAY
        st.info(f"等待視頻URL生成... (剩餘等待時間約 {remaining_time} 秒)")
        time.sleep(RETRY_DELAY)
    
    st.error("等待視頻URL生成超時")
    return None

def generate_and_wait_for_url(lyrics, theme):
    suno_client = initialize_suno_client()
    
    with st.spinner('正在生成音樂...'):
        clip = generate_music(suno_client, lyrics, theme)
        if not clip:
            st.error('音樂生成失敗')
            return None
        
        st.success(f'音樂生成成功! Clip ID: {clip.id}')
    
    with st.spinner('正在等待視頻URL生成...'):
        video_url = wait_for_video_url(suno_client, clip.id)
        if video_url:
            st.success('成功獲取視頻URL!')
            return video_url
        else:
            st.error('無法獲取視頻URL')
            return None

# Streamlit 介面
st.title("Suno音樂生成與視頻URL等待器")

lyrics = st.text_area("請輸入歌詞", height=150)
theme = st.text_input("請輸入主題")

if st.button("生成音樂並獲取視頻URL"):
    if lyrics and theme:
        video_url = generate_and_wait_for_url(lyrics, theme)
        if video_url:
            st.markdown(f"視頻URL: {video_url}")
            st.video(video_url)
    else:
        st.error("請輸入歌詞和主題")
