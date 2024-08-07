import streamlit as st

def main():
    st.title("歌曲生成選擇介面")

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
        choice = st.radio(
            f"選擇一個{category}或輸入自定義選項：",
            options + ["自定義"],
            key=f"{category}_radio"
        )
        
        if choice == "自定義":
            custom_input = st.text_input(f"請輸入自定義{category}：", key=f"{category}_custom")
            selections[category] = custom_input
        else:
            selections[category] = choice

    if st.button("確定"):
        st.subheader("您的選擇：")
        for category, selection in selections.items():
            st.write(f"{category}: {selection}")

if __name__ == "__main__":
    main()
