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
                        {"type": "text", "text": "从下面的图片中提取信息：起始地，目的地，行驶距离，行驶时长，驾驶时间（日期时间），并用 JSON 返回：请返回格式如下：{\n \"start_location\": \"\",\n \"end_location\": \"\",\n \"distance\": \"\",\n \"duration\": \"\",\n \"start_time\": \"\"\n}"}
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







