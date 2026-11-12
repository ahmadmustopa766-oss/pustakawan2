from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import get_db_connection

app = Flask(__name__)
# Secret key digunakan untuk session dan flash message
app.secret_key = 'rahasia_luar_angkasa'


# ==========================================
# ROUTE: INDEX & LOGIN
# ==========================================
@app.route('/')
def index():
    # Jika sudah login, arahkan ke dashboard sesuai role
    if 'user_id' in session:
        if session['role'] == 'pustakawan':
            return redirect(url_for('pustakawan'))
        else:
            return redirect(url_for('peminjam'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()

        if user:
            # Simpan data user ke dalam session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']

            return redirect(url_for('index'))
        else:
            flash('Username atau password salah!', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ==========================================
# ROUTE: PUSTAKAWAN (ADMIN)
# ==========================================
@app.route('/pustakawan', methods=['GET', 'POST'])
def pustakawan():
    # Proteksi: Hanya pustakawan yang bisa masuk
    if 'user_id' not in session or session['role'] != 'pustakawan':
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Logika untuk menambah buku baru
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        stock = request.form['stock']
        conn.execute('INSERT INTO books (title, author, stock) VALUES (?, ?, ?)', (title, author, stock))
        conn.commit()
        flash('Buku berhasil ditambahkan ke stasiun ruang angkasa!', 'success')
        return redirect(url_for('pustakawan'))

    # Ambil data buku dan data peminjaman
    books = conn.execute('SELECT * FROM books').fetchall()
    borrowings = conn.execute('''
                              SELECT borrowings.id, users.username, books.title, borrowings.status
                              FROM borrowings
                                       JOIN users ON borrowings.user_id = users.id
                                       JOIN books ON borrowings.book_id = books.id
                              ''').fetchall()
    conn.close()

    return render_template('pustakawan.html', books=books, borrowings=borrowings)


@app.route('/kembalikan/<int:borrow_id>')
def kembalikan(borrow_id):
    if 'user_id' not in session or session['role'] != 'pustakawan':
        return redirect(url_for('login'))

    conn = get_db_connection()
    borrowing = conn.execute('SELECT book_id, status FROM borrowings WHERE id = ?', (borrow_id,)).fetchone()

    if borrowing and borrowing['status'] == 'dipinjam':
        # Ubah status transaksi menjadi dikembalikan
        conn.execute('UPDATE borrowings SET status = "dikembalikan" WHERE id = ?', (borrow_id,))
        # Kembalikan stok buku + 1
        conn.execute('UPDATE books SET stock = stock + 1 WHERE id = ?', (borrowing['book_id'],))
        conn.commit()
        flash('Buku telah kembali ke markas!', 'success')
    conn.close()
    return redirect(url_for('pustakawan'))


# ==========================================
# ROUTE: PEMINJAM (USER)
# ==========================================
@app.route('/peminjam')
def peminjam():
    # Proteksi: Hanya peminjam yang bisa masuk
    if 'user_id' not in session or session['role'] != 'peminjam':
        return redirect(url_for('login'))

    conn = get_db_connection()
    # Hanya tampilkan buku yang stoknya masih ada
    books = conn.execute('SELECT * FROM books WHERE stock > 0').fetchall()
    # Tampilkan riwayat peminjaman user ini saja
    my_borrowings = conn.execute('''
                                 SELECT borrowings.id, books.title, borrowings.status
                                 FROM borrowings
                                          JOIN books ON borrowings.book_id = books.id
                                 WHERE borrowings.user_id = ?
                                 ''', (session['user_id'],)).fetchall()
    conn.close()

    return render_template('peminjam.html', books=books, borrowings=my_borrowings)


@app.route('/pinjam/<int:book_id>')
def pinjam(book_id):
    if 'user_id' not in session or session['role'] != 'peminjam':
        return redirect(url_for('login'))

    conn = get_db_connection()
    book = conn.execute('SELECT stock FROM books WHERE id = ?', (book_id,)).fetchone()

    if book and book['stock'] > 0:
        # Kurangi stok buku - 1
        conn.execute('UPDATE books SET stock = stock - 1 WHERE id = ?', (book_id,))
        # Catat peminjaman
        conn.execute('INSERT INTO borrowings (user_id, book_id, status) VALUES (?, ?, ?)',
                     (session['user_id'], book_id, 'dipinjam'))
        conn.commit()
        flash('Buku berhasil dipinjam untuk eksplorasi!', 'success')
    else:
        flash('Stok buku habis!', 'error')

    conn.close()
    return redirect(url_for('peminjam'))


if __name__ == '__main__':
    # Jalankan server Flask pada mode debug
    app.run(debug=True)