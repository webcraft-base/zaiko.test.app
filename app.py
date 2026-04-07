from flask import Flask, render_template, request
import json
import os

app = Flask(__name__)

# JSONファイル名
JSON_FILE = "stock.json"

# 商品リスト
items = [
    "コーヒー（ブラジル）",
    "コーヒー（コロンビア）",
    "コーヒー（オリジナルブレンド）",
    "いちご",
    "生クリーム",
    "小麦粉",
    "牛乳",
    "砂糖",
    "紙コップ",
]

# 起動時にJSONから在庫を読み込む
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        stock_dict = json.load(f)
else:
    stock_dict = {}


@app.route("/", methods=["GET", "POST"])
def index():
    global stock_dict

    if request.method == "POST":
        item = request.form["item"]
        quantity = int(request.form["quantity"])

        # 在庫更新
        if item in stock_dict:
            stock_dict[item] += quantity
        else:
            stock_dict[item] = quantity

        # JSONに書き込み
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(stock_dict, f, ensure_ascii=False, indent=2)

    # 在庫を少ない順にソート
    sorted_stock = sorted(stock_dict.items(), key=lambda x: x[1])
    return render_template("index.html", stock_dict=sorted_stock, items=items)


if __name__ == "__main__":
    app.run(debug=True)
