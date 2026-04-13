from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

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


# DB接続
def get_db():
    conn = sqlite3.connect("stock.db")
    return conn


@app.route("/", methods=["GET", "POST"])
def index():

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        item = request.form["item"]
        quantity = int(request.form["quantity"])

        # すでにあるか確認
        cursor.execute("SELECT quantity FROM stock WHERE name = ?", (item,))
        result = cursor.fetchone()

        if result:
            new_quantity = result[0] + quantity
            cursor.execute(
                "UPDATE stock SET quantity = ? WHERE name = ?", (new_quantity, item)
            )
        else:
            cursor.execute(
                "INSERT INTO stock (name, quantity) VALUES (?, ?)", (item, quantity)
            )

        conn.commit()

    # 在庫取得（少ない順）
    cursor.execute("SELECT name, quantity FROM stock ORDER BY quantity ASC")
    rows = cursor.fetchall()

    conn.close()

    return render_template("index.html", stock_dict=rows, items=items)


if __name__ == "__main__":
    app.run(debug=True)
