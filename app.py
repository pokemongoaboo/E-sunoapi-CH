import streamlit as st
import json
from openai import OpenAI
import time
from suno import Suno, ModelVersions

# OpenAI API 设置
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

# Suno 设置
suno_client = Suno(
    cookie=st.secrets["SUNO_COOKIE"],
    model_version=ModelVersions.CHIRP_V3_5
)

# 设置标题最大长度
MAX_TITLE_LENGTH = 50

def generate_lyrics(all_selections):
    prompt = f"""你是[世界頂尖的台語歌詞創作大師]，請你寫一首[充滿溫暖、浪漫、緩慢、有感情]的歌詞。
    描述[{all_selections}]。
    音樂的風格是[六十年代台語歌曲風]。
    詞曲的結構是[Verse1]-[Chorus]-[Verse2]-[Chorus]-[Bride]-[Chorus]-[Outro](結構兩旁要加上方號[]，並與上一段有一個空格)
    最前面加上 [intro 阮阮] 最後面加上[End]"""

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

    請提供一個簡潔而富有意境的主題，不超過{MAX_TITLE_LENGTH}個字符。"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional song theme creator."},
            {"role": "user", "content": prompt}
        ]
    )
    theme = response.choices[0].message.content
    return theme[:MAX_TITLE_LENGTH]

def generate_song(lyrics, theme):
    try:
        clips = suno_client.generate(
            prompt=lyrics,
            tags="六十年代台語歌曲風",
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

def check_video_status(clip):
    max_attempts = 30  # 最多检查30次，每次间隔10秒
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for attempt in range(max_attempts):
        if not clip.is_video_pending:
            progress_bar.progress(1.0)
            status_text.text("視頻生成完成！")
            return clip.video_url
        
        progress = (attempt + 1) / max_attempts
        progress_bar.progress(progress)
        status_text.text(f"正在等待視頻生成，已嘗試 {attempt + 1} 次...")
        
        time.sleep(10)
        clip = suno_client.get_clip(clip.id)
    
    status_text.text("視頻生成超時。")
    return None

def main():
    st.title("台語歌曲生成器")

    categories = {
        "主題": ["懷念舊時", "晚年快樂", "金婚慶典", "孫仔陪伴", "永遠的情份"],
        "心情": ["溫暖", "感恩", "糖甘蜜甜", "足幸福", "懷舊思念"],
        "物品": ["舊相片", "手織毛衣衫", "古董時鐘", "結婚手戒指", "祖傳珠寶"],
        "場景": ["櫻花樹腳", "古厝庭園", "夕陽下的長椅", "餐廳的燭光晚餐", "鄉下路仔"],
        "人物": ["老伴", "老朋友", "孫仔", "囝仔", "一世人伴"]    
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

    if st.button("生成歌曲"):
        st.subheader("您的選擇：")
        for category, selection in selections.items():
            st.write(f"{category}: {', '.join(selection)}")
        
        all_selections = json.dumps(selections, ensure_ascii=False)
        
        with st.spinner('正在生成歌詞，請稍候...'):
            lyrics = generate_lyrics(all_selections)
        
        st.subheader("生成的歌詞：")
        st.text_area("歌詞", lyrics, height=300)

        with st.spinner('正在生成歌曲主題，請稍候...'):
            theme = generate_theme(lyrics)
        
        st.subheader("生成的歌曲主題：")
        st.write(theme)

        with st.spinner('正在生成歌曲，請稍候...'):
            clip = generate_song(lyrics, theme)
        
        if clip:
            st.subheader("生成的歌曲：")
            st.audio(clip.audio_url)

            st.subheader("歌曲影片生成狀態：")
            video_url = check_video_status(clip)
            
            if video_url:
                st.subheader("歌曲影片：")
                st.video(video_url)
            else:
                st.warning("歌曲影片生成超時，請稍後檢查或重試。您可以稍後再次訪問此頁面查看是否生成成功。")
        else:
            st.error("歌曲生成失敗，請稍後再試。")

if __name__ == "__main__":
    main()
