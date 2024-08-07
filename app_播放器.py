import streamlit as st

def main():
    st.title("视频播放器")

    video_url = "https://cdn1.suno.ai/60451233-718c-403f-a769-d06ef51c7b11.mp4"

    # 使用HTML5 video标签
    video_html = f"""
        <video controls width="100%">
            <source src="{video_url}" type="video/mp4">
            您的浏览器不支持video标签。
        </video>
    """

    # 使用markdown显示HTML
    st.markdown(video_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
