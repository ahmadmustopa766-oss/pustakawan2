import sqlite3


def init_db():
    # Membuat atau menghubungkan ke file database.db
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 1. Tabel Users
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       password
                       TEXT
                       NOT
                       NULL,
                       role
                       TEXT
                       NOT
                       NULL -- Berisi 'pustakawan' atau 'peminjam'
                   )
                   ''')

    # 2. Tabel Books
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS books
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       title
                       TEXT
                       NOT
                       NULL,
                       author
                       TEXT
                       NOT
                       NULL,
                       stock
                       INTEGER
                       NOT
                       NULL
                   )
                   ''')

    # 3. Tabel Borrowings (Peminjaman)
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS borrowings
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       user_id
                       INTEGER,
                       book_id
                       INTEGER,
                       status
                       TEXT
                       NOT
                       NULL, -- Berisi 'dipinjam' atau 'dikembalikan'
                       FOREIGN
                       KEY
                   (
                       user_id
                   ) REFERENCES users
                   (
                       id
                   ),
                       FOREIGN KEY
                   (
                       book_id
                   ) REFERENCES books
                   (
                       id
                   )
                       )
                   ''')

    # Insert Data Awal (Dummy) jika tabel users masih kosong
    cursor.execute("SELECT * FROM users WHERE username='pustakawan_admin'")
    if not cursor.fetchone():
        # Akun Pustakawan
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES ('pustakawan_admin', 'admin123', 'pustakawan')")
        # Akun Peminjam
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('peminjam_user', 'user123', 'peminjam')")

        # Buku Dummy
        cursor.execute("INSERT INTO books (title, author, stock) VALUES ('Pemrograman Web Modern', 'John Doe', 5)")
        cursor.execute("INSERT INTO books (title, author, stock) VALUES ('Misteri Galaksi', 'Jane Smith', 3)")

    conn.commit()
    conn.close()
    print("Database dan tabel berhasil diinisialisasi!")


def get_db_connection():
    """Fungsi ini akan dipanggil oleh app.py untuk melakukan query"""
    conn = sqlite3.connect('database.db')
    # Row factory agar hasil query bisa diakses menggunakan nama kolom seperti dictionary
    conn.row_factory = sqlite3.Row
    return conn


# Jalankan file ini secara langsung untuk menginisialisasi database
if __name__ == '__main__':
    init_db()