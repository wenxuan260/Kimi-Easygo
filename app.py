import os
import base64
import re
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1"
)

def detect_image_type(b64_str):
    # 已包含 data:image/... 前缀，直接返回
    if b64_str.startswith("data:image/"):
        return b64_str

    # 尝试判断文件类型
    if b64_str.startswith("/9j/"):
        mime = "jpeg"
    elif b64_str.startswith("iVBOR"):
        mime = "png"
    elif b64_str.startswith("R0lGOD"):
        mime = "gif"
    else:
        mime = "jpeg"  # 默认类型

    return f"data:image/{mime};base64,{b64_str}"

@app.route("/recognize", methods=["POST"])
def recognize():
    data = request.get_json()
    base64_image = data.get("base64_image")

    if not base64_image:
        return jsonify({"error": "base64_image not provided"}), 400

    image_url = detect_image_type(base64_image)

    try:
        completion = client.chat.completions.create(
            model="moonshot-v1-8k-vision-preview",
            messages=[
                {"role": "system", "content": "你是 Kimi。"},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": "从下面的图片中提取信息：起始地，目的地，行驶距离，行驶时长，驾驶时间（日期时间），并用 JSON 返回：请返回格式如下：{\n \"start_location\": \"\",\n \"end_location\": \"\",\n \"distance\": \"\",\n \"duration\": \"\",\n \"start_time\": \"\"\n}"}
                    ]
                }
            ]
        )
        return jsonify({"result": completion.choices[0].message.content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

