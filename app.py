import time
import streamlit as st
import json
from openai import OpenAI
from suno import Suno, ModelVersions

# Constants
MAX_TITLE_LENGTH = 100
CHECK_INTERVAL = 5  # 檢查間隔秒數

# OpenAI API 設置
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

def initialize_suno_client():
    try:
        return Suno(
            cookie=st.secrets["SUNO_COOKIE"],
            model_version=ModelVersions.CHIRP_V3_5
        )
    except Exception as e:
        st.error(f"初始化Suno客戶端時出錯: {str(e)}")
        return None

def generate_lyrics(all_selections):
    prompt = f"""你是[世界頂尖的國語歌詞創作大師]，請你寫一首[充滿溫暖、浪漫、緩慢、有感情]的中文歌詞。
    描述[{all_selections}]。
    音樂的風格是[六十年代國語歌曲風]。
    詞曲的結構是[Verse1]-[Chorus]-[Verse2]-[Chorus]-[Bride]-[Chorus]-[Outro](結構兩旁要加上方號[]，並與上一段有一個空格)
    最前面加上 [intro] 最後面加上[End]"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional Taiwanese song lyricist."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def generate_theme(lyrics):
    prompt = f"""根據以下歌詞，給出一個適合的歌曲主題：
    {lyrics}
    請提供一個簡潔而富有意境的主題。"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional song theme creator."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def generate_music(suno_client, lyrics, theme):
    try:
        clips = suno_client.generate(
            prompt=lyrics,
            tags="六十年代國語歌曲風, 國語男歌手, 民歌腔, 國語歌",
            title=theme[:MAX_TITLE_LENGTH],
            make_instrumental=False,
            is_custom=True,
            wait_audio=True
        )
        if clips and clips[0].audio_url:
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
    st.title("音樂歌曲生成器(Music Generator)")

    # 使用 session_state 來保存狀態
    if 'clip' not in st.session_state:
        st.session_state.clip = None
    if 'video_url' not in st.session_state:
        st.session_state.video_url = None
    if 'lyrics' not in st.session_state:
        st.session_state.lyrics = None
    if 'theme' not in st.session_state:
        st.session_state.theme = None

    categories = {
        "主題(Themes)": ["回憶過往", "晚年幸福", "金婚紀念", "孫兒相伴", "永恆的愛"],
        "心情(Moods)": ["溫暖", "感恩", "柔情", "幸福", "懷舊"],
        "時間(Time)": ["天光", "日頭赤炎炎", "三更半暝", "黃昏", "透早"],
        "物品(Items)": ["老照片", "手織毛衣", "古董鐘錶", "婚戒", "祖傳首飾"],
        "場景(Scene)": ["櫻花樹下", "古老庭院", "夕陽下的長椅", "餐廳裡的燭光晚餐", "鄉間小路"],
        "人物(People)": ["摯愛伴侶", "親密好友", "孫兒", "子女", "相伴一生的人"]
    }

    selections = {}
    for category, options in categories.items():
        st.subheader(f"{category}")
        selected = st.multiselect(
            f"選擇一個或多個{category}：",
            options,
            key=f"{category}_multiselect"
        )
        
        custom_input = st.text_input(f"輸入自定義{category}（多個請用逗號分隔）：", key=f"{category}_custom")
        if custom_input:
            custom_options = [option.strip() for option in custom_input.split(',')]
            selected.extend(custom_options)
        
        selections[category] = selected

    if st.button("生成歌詞和主題(Generate Lyrics and Themes)"):
        st.subheader("您的選擇：")
        for category, selection in selections.items():
            st.write(f"{category}: {', '.join(selection)}")
        
        all_selections = json.dumps(selections, ensure_ascii=False)
        
        with st.spinner('正在生成歌詞，請稍候...'):
            st.session_state.lyrics = generate_lyrics(all_selections)
        
        st.subheader("生成的歌詞：")
        st.text_area("歌詞", st.session_state.lyrics, height=300)

        with st.spinner('正在生成歌曲主題，請稍候...'):
            st.session_state.theme = generate_theme(st.session_state.lyrics)
        
        st.subheader("生成的歌曲主題：")
        st.write(st.session_state.theme)

    # 初始化 Suno 客戶端並顯示 credits_info
    suno_client = initialize_suno_client()
    #if suno_client:
    #    try:
    #        credits_info = suno_client.get_credits()
    #        st.write(credits_info['credits_left'])
    #        st.write(credits_info['period'])
    #        st.write(credits_info['monthly_limit'])
    #        st.write(credits_info['monthly_usage'])
    #    except Exception as e:
    #        st.error(f"取得credits_info 過程: {str(e)}")
    #        return None
            

    # 創建可更新的佔位符
    audio_player = st.empty()
    video_status = st.empty()

    if st.session_state.lyrics and st.session_state.theme:
        if st.button("生成音樂(Generate Music)"):
            if not suno_client:
                return
            with st.spinner('正在生成音樂(Music generating)...'):
                st.session_state.clip = generate_music(suno_client, st.session_state.lyrics, st.session_state.theme)
                if not st.session_state.clip:
                    st.error('音樂生成失敗')
                    return
            st.success(f'音樂生成成功! Clip ID: {st.session_state.clip.id}')
            
            # 立即顯示音頻播放器
            audio_player.audio(st.session_state.clip.audio_url, format='audio/mp3')
            
            # 開始檢查視頻URL
            st.session_state.video_url = None
            video_status.info('影片生成中(Video Generating)，請稍候...')
            
            # 使用非阻塞方式檢查視頻URL
            for _ in range(60):  # 最多等待5分鐘 (60 * 5 秒)
                video_url = check_video_url(suno_client, st.session_state.clip.id)
                if video_url:
                    st.session_state.video_url = video_url
                    video_status.success(f'影片已生成: {st.session_state.video_url}')
                    break
                time.sleep(CHECK_INTERVAL)
            
            if not st.session_state.video_url:
                video_status.warning('影片生成超時，請稍後再試。')

    # 當 video_url 存在時顯示播放按鈕
    if st.session_state.video_url:
        if st.button('播放影片(Play video)'):
            video_html = f"""
                <video controls width="100%">
                <source src="{st.session_state.video_url}" type="video/mp4">
                您的浏览器不支持video标签。
                </video>
            """
            st.markdown(video_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
