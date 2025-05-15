import os
import base64
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1"
)

# 判断图片 MIME 类型并添加 data URI 前缀
def wrap_base64_image(b64_str):
    if b64_str.startswith("data:image/"):
        return b64_str

    if b64_str.startswith("/9j/"):
        mime = "jpeg"
    elif b64_str.startswith("iVBOR"):
        mime = "png"
    elif b64_str.startswith("R0lGOD"):
        mime = "gif"
    else:
        mime = "jpeg"

    return f"data:image/{mime};base64,{b64_str}"

@app.route("/recognize", methods=["POST"])
def recognize():
    data = request.get_json()
    base64_image = data.get("base64_image")

    if not base64_image:
        return jsonify({"error": "base64_image not provided"}), 400

    image_url = wrap_base64_image(base64_image)

    try:
        completion = client.chat.completions.create(
            model="moonshot-v1-8k-vision-preview",
            messages=[
                {"role": "system", "content": "你是 Kimi。"},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": "请从图片中提取以下字段并用 JSON 返回：起始地、目的地、行驶距离、行驶时长、驾驶时间（日期时间）。返回格式为：{\n \"start_location\": \"\",\n \"end_location\": \"\",\n \"distance\": \"\",\n \"duration\": \"\",\n \"start_time\": \"\"\n}"}
                    ]
                }
            ]
        )
        return jsonify({"result": completion.choices[0].message.content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


