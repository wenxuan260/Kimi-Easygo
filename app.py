import os
from flask import Flask, request, jsonify
from openai import OpenAI
 
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
                        {"type": "text", "text": "请从以下图片中准确提取以下信息字段，并严格按照 JSON 格式返回：{\n  "start_location": "出发地（如：北京市）",\n  "end_location": "目的地（如：天津市）",\n  "distance": "行驶距离，（如：120.5）", \n  "duration": "行驶时长，格式为小时:分钟:秒（如：00:48:47）", \n  "start_time": "出发时间，格式为 yyyy-MM-dd HH:mm（如：2025-05-22 08:30）"\n}\n要求： \n1. 所有字段必须提取自图片中能识别到的文字内容；\n2. 若某字段无法识别，请填入空字符串 ""，不要省略字段；\n3. 返回结果必须是合法的 JSON 字符串。"}
                    ]
                }
            ]
        )
        print(completion.choices[0].message.content) 
        return jsonify(completion.choices[0].message.content)
 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)






