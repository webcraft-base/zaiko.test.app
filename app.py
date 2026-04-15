from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# =========================
# DB接続
# =========================
def get_db():
    conn = sqlite3.connect("stock.db")
    return conn


# =========================
# 初期化（テーブル＋初期データ）
# =========================
def init_db():
    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()

    # stockテーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            quantity INTEGER,
            is_deleted INTEGER DEFAULT 0
        )
    """)

    # itemsテーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    """)

    # 初期データ
    cursor.execute("SELECT COUNT(*) FROM items")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute("INSERT INTO items (name) VALUES ('牛乳')")
        cursor.execute("INSERT INTO items (name) VALUES ('いちご')")
        cursor.execute("INSERT INTO items (name) VALUES ('生クリーム')")

    conn.commit()
    conn.close()


# =========================
# 一覧ページ（通常）
# =========================
@app.route("/", methods=["GET", "POST"])
def index():

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        item_id = int(request.form["item"])
        quantity = int(request.form["quantity"])

        cursor.execute("SELECT quantity FROM stock WHERE item_id = ?", (item_id,))
        result = cursor.fetchone()

        if result:
            new_quantity = result[0] + quantity
            cursor.execute(
                "UPDATE stock SET quantity = ?, is_deleted = 0 WHERE item_id = ?",
                (new_quantity, item_id),
            )
        else:
            cursor.execute(
                "INSERT INTO stock (item_id, quantity) VALUES (?, ?)",
                (item_id, quantity),
            )

        conn.commit()

    cursor.execute("""
        SELECT stock.item_id, items.name, stock.quantity
        FROM stock
        JOIN items ON stock.item_id = items.id
        WHERE stock.is_deleted = 0
        ORDER BY stock.quantity ASC
    """)
    rows = cursor.fetchall()

    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()

    conn.close()

    return render_template("index.html", stock_dict=rows, items=items)


# =========================
# 削除済み一覧ページ
# =========================
@app.route("/deleted")
def deleted():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT stock.item_id, items.name, stock.quantity
        FROM stock
        JOIN items ON stock.item_id = items.id
        WHERE stock.is_deleted = 1
        ORDER BY stock.quantity ASC
    """)
    rows = cursor.fetchall()

    conn.close()

    return render_template("deleted.html", stock_dict=rows)


# =========================
# 復元処理
# =========================
@app.route("/restore/<int:item_id>")
def restore(item_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE stock SET is_deleted = 0 WHERE item_id = ?", (item_id,))

    conn.commit()
    conn.close()

    return redirect("/deleted")


# =========================
# 削除（論理削除）
# =========================
@app.route("/delete/<int:item_id>")
def delete(item_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE stock SET is_deleted = 1 WHERE item_id = ?", (item_id,))

    conn.commit()
    conn.close()

    return redirect("/")


# =========================
# 編集
# =========================
@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit(item_id):

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        quantity = int(request.form["quantity"])

        cursor.execute(
            "UPDATE stock SET quantity = ? WHERE item_id = ?",
            (quantity, item_id),
        )

        conn.commit()
        conn.close()

        return redirect("/")

    cursor.execute(
        """
        SELECT items.name, stock.quantity
        FROM stock
        JOIN items ON stock.item_id = items.id
        WHERE stock.item_id = ?
    """,
        (item_id,),
    )

    item = cursor.fetchone()

    conn.close()

    return render_template("edit.html", item=item, item_id=item_id)


# =========================
# 起動
# =========================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
