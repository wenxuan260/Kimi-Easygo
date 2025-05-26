import os
from flask import Flask, request, jsonify
from openai import OpenAI
import logging
logging.basicConfig(level=logging.INFO) 
app = Flask(__name__)
 
client = OpenAI(
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1"
)
 
def build_image_data_url(b64_str):
    if b64_str.startswith("data:image/"):
        return b64_str
 
    if b64_str.startswith("/9j/"):  # JPEG
        mime = "jpeg"
    elif b64_str.startswith("iVBOR"):  # PNG
        mime = "png"
    elif b64_str.startswith("R0lGOD"):  # GIF
        mime = "gif"
    else:
        mime = "jpeg"
 
    return f"data:image/{mime};base64,{b64_str}"
 
@app.route("/recognize", methods=["POST"])
def recognize():
    try:
        # 读取 text/plain 传来的 base64 字符串
        base64_str = request.get_data(as_text=True).strip()
 
        if not base64_str:
            return jsonify({"error": "Empty base64 string"}), 400
 
        image_url = build_image_data_url(base64_str)
 
        # 调用 Moonshot API
        completion = client.chat.completions.create(
            model="moonshot-v1-8k-vision-preview",
            messages=[
                {"role": "system", "content": "你是 Kimi。"},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": "从下面的图片中提取信息：起始地，目的地，行驶距离，行驶时长，驾驶时间（日期时间），返回合法JSON ，严格执行如下格式：{\n \"start_location\": \"\",\n \"end_location\": \"\",\n \"distance\": \"\",\n \"duration\": \"\",\n \"start_time\": \"\"\n}，字段要求如下：1. \"start_location\"：提取图中明确标注的出发地名称（如“北京市”）。2. \"end_location\"：提取图中明确标注的目的地名称（如“天津市”）。3. \"distance\"：提取图中显示的行驶距离，单位为公里（如“120.5”），仅保留数字部分。4. \"duration\"：提取图中完整的行驶时长，格式统一为“小时:分钟:秒”，如“00:48:47”。5. \"start_time\"：提取图中标注的出发时间，统一格式为“yyyy-MM-dd HH:mm”，如“2025-05-22 08:30”。6.最终输出必须是合法的、可解析的 JSON 字符串，不能包含多余内容。7.若某字段图片中未显示或无法识别，请填入空字符串 \"\"，不要省略字段。"}
                    ]
                }
            ]
        )
        print(completion.choices[0].message.content) 
        return jsonify(completion.choices[0].message.content)
 
    except Exception as e:
        logging.error("发生错误：%s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)






