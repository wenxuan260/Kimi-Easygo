import os
import json
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1"
)

@app.route("/recognize", methods=["POST"])
def recognize():
    data = request.get_json()
    base64_image = data.get("base64_image")

    if not base64_image:
        return jsonify({"error": "base64_image not provided"}), 400

    # 这里假设 base64_image 已经是带data:image/...前缀的字符串或者你自己处理好了
    image_url = base64_image if base64_image.startswith("data:image/") else f"data:image/jpeg;base64,{base64_image}"

    try:
        completion = client.chat.completions.create(
            model="moonshot-v1-8k-vision-preview",
            messages=[
                {"role": "system", "content": "你是 Kimi。"},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": (
                            "从下面的图片中提取信息：起始地，目的地，行驶距离，行驶时长，驾驶时间（日期时间），并用 JSON 返回："
                            "{\n \"start_location\": \"\",\n \"end_location\": \"\",\n \"distance\": \"\",\n \"duration\": \"\",\n \"start_time\": \"\"\n}"
                        )}
                    ]
                }
            ]
        )
        
        # 这里把字符串转成JSON对象
        json_result = json.loads(completion.choices[0].message.content)

        return jsonify(json_result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)




