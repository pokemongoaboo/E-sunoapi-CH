import streamlit as st
import json
from openai import OpenAI
from suno import Suno, ModelVersions
import time

# OpenAI API 设置
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

# Suno 设置
suno_client = Suno(
    cookie=st.secrets["SUNO_COOKIE"],
    model_version=ModelVersions.CHIRP_V3_5
)

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

    請提供一個簡潔而富有意境的主題。"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional song theme creator."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def generate_song(lyrics, theme):
    clips = suno_client.generate(
        prompt=lyrics,
        tags="六十年代台語歌曲風",
        title=theme,
        make_instrumental=False,
        is_custom=True,
        wait_audio=True
    )
    if clips:
        return clips[0]
    return None

def check_video_status(clip):
    max_attempts = 30  # 最多检查30次，每次间隔10秒
    for _ in range(max_attempts):
        if not clip.is_video_pending:
            return clip.video_url
        time.sleep(10)
        clip = suno_client.get_clip(clip.id)
    return None

def main():
    st.title("台語歌曲生成器")

    categories = {
        "主題": ["回憶過往", "晚年幸福", "金婚紀念", "孫兒相伴", "永恆的愛"],
        "心情": ["溫暖", "感恩", "柔情", "幸福", "懷舊"],
        "物品": ["老照片", "手織毛衣", "古董鐘錶", "婚戒", "祖傳首飾"],
        "場景": ["櫻花樹下", "古老庭院", "夕陽下的長椅", "餐廳裡的燭光晚餐", "鄉間小路"],
        "人物": ["摯愛伴侶", "親密好友", "孫兒", "子女", "相伴一生的人"]
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

            with st.spinner('正在處理歌曲影片，請稍候...'):
                video_url = check_video_status(clip)
            
            if video_url:
                st.subheader("歌曲影片：")
                video_html = f"""
                    <video controls width="100%">
                        <source src="{video_url}" type="video/mp4">
                        您的浏览器不支持video标签。
                    </video>
                """
                st.markdown(video_html, unsafe_allow_html=True)
            else:
                st.warning("歌曲影片仍在生成中，請稍後再試。")
        else:
            st.error("歌曲生成失敗，請稍後再試。")

if __name__ == "__main__":
    main()
