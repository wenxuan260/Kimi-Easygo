import os
import base64
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    #api_key=os.environ.get("MOONSHOT_API_KEY"),  # 推荐使用 Render 的环境变量
    api_key=sk-MMw06tR25JX52nHURjEiheSw6cV1qTiywnj8X9bsnO1roXnf
    base_url="https://api.moonshot.cn/v1"
)

@app.route("/recognize", methods=["POST"])
def recognize():
    data = request.get_json()
    base64_image = data.get("base64_image")

    if not base64_image:
        return jsonify({"error": "base64_image not provided"}), 400

    image_url = f"data:image/jpeg;base64,{base64_image}"

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

