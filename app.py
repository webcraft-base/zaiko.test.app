from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


# DB接続
def get_db():
    conn = sqlite3.connect("stock.db")
    return conn


def init_db():
    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()

    # stockテーブル（在庫）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            quantity INTEGER
        )
    """)

    # itemsテーブル（商品）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    """)

    # 初期データ（空のときだけ）
    cursor.execute("SELECT COUNT(*) FROM items")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute("INSERT INTO items (name) VALUES ('牛乳')")
        cursor.execute("INSERT INTO items (name) VALUES ('いちご')")
        cursor.execute("INSERT INTO items (name) VALUES ('生クリーム')")

    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def index():

    conn = get_db()
    cursor = conn.cursor()

    # 追加処理
    if request.method == "POST":
        item_id = int(request.form["item"])
        quantity = int(request.form["quantity"])

        cursor.execute("SELECT quantity FROM stock WHERE item_id = ?", (item_id,))
        result = cursor.fetchone()

        if result:
            new_quantity = result[0] + quantity
            cursor.execute(
                "UPDATE stock SET quantity = ? WHERE item_id = ?",
                (new_quantity, item_id),
            )
        else:
            cursor.execute(
                "INSERT INTO stock (item_id, quantity) VALUES (?, ?)",
                (item_id, quantity),
            )

        conn.commit()

    # 在庫取得（JOINで商品名に戻す✨）
    cursor.execute("""
        SELECT items.name, stock.quantity
        FROM stock
        JOIN items ON stock.item_id = items.id
        ORDER BY stock.quantity ASC
    """)
    rows = cursor.fetchall()

    # 商品取得（プルダウン用）
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()

    conn.close()

    return render_template("index.html", stock_dict=rows, items=items)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
