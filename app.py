import json  # 记得顶部引入

@app.route("/recognize", methods=["POST"])
def recognize():
    try:
        base64_str = request.get_data(as_text=True).strip()

        if not base64_str:
            return jsonify({"error": "Empty base64 string"}), 400

        image_url = build_image_data_url(base64_str)

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

        # 把字符串结果转成 dict
        result_json = json.loads(completion.choices[0].message.content)
        print(result_json)

        # 直接返回 JSON 对象
        return jsonify(result_json)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)







