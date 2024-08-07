import streamlit as st
import json

def main():
    st.title("歌曲生成多選介面")

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

    if st.button("確定"):
        st.subheader("您的選擇：")
        for category, selection in selections.items():
            st.write(f"{category}: {', '.join(selection)}")
        
        # 將所有選擇存儲在一個變量中
        all_selections = json.dumps(selections, ensure_ascii=False, indent=2)
        
        st.subheader("所有選擇的組合輸出：")
        st.code(all_selections)
        
        # 如果需要在Python中進一步處理，可以這樣使用：
        # selections_dict = json.loads(all_selections)
        st.info("提示：這個JSON字符串可以被存儲或傳遞給其他函數進行進一步處理。")

if __name__ == "__main__":
    main()
