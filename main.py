from flask import Flask, render_template, request, redirect, url_for, abort
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)

# File untuk menyimpan data
DATA_FILE = 'pastes.json'

def init_data_file():
    """Inisialisasi file data jika belum ada"""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def load_data():
    """Load data dari file JSON"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Pastikan data adalah list
                if isinstance(data, list):
                    return data
                else:
                    return []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_data(data):
    """Simpan data ke file JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving data: {e}")
        return False
    return True

def get_paste_by_id(paste_id):
    """Ambil paste berdasarkan ID"""
    data = load_data()
    for paste in data:
        if paste['id'] == paste_id:
            return paste
    return None

@app.route('/')
def index():
    """Halaman utama menampilkan daftar paste"""
    data = load_data()
    # Pastikan data adalah list
    if not isinstance(data, list):
        data = []
    # Urutkan berdasarkan tanggal terbaru
    data = sorted(data, key=lambda x: x.get('created_at', ''), reverse=True)
    return render_template('index.html', pastes=data)

@app.route('/create', methods=['GET', 'POST'])
def create_paste():
    """Halaman untuk membuat paste baru"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        author = request.form.get('author', 'Anonymous').strip()
        
        if not content:
            return render_template('create.html', error="Konten tidak boleh kosong!")
        
        # Buat paste baru
        paste = {
            'id': str(uuid.uuid4()),
            'title': title if title else 'Untitled',
            'content': content,
            'author': author,
            'created_at': datetime.now().isoformat()
        }
        
        # Simpan ke database
        data = load_data()
        # Pastikan data adalah list
        if not isinstance(data, list):
            data = []
        data.append(paste)
        save_data(data)
        
        return redirect(url_for('view_paste', paste_id=paste['id']))
    
    return render_template('create.html')

@app.route('/paste/<paste_id>')
def view_paste(paste_id):
    """Halaman untuk melihat paste"""
    paste = get_paste_by_id(paste_id)
    if not paste:
        abort(404)
    
    return render_template('view.html', paste=paste)

@app.route('/delete/<paste_id>', methods=['POST'])
def delete_paste(paste_id):
    """Hapus paste"""
    data = load_data()
    # Pastikan data adalah list
    if not isinstance(data, list):
        data = []
    data = [p for p in data if p['id'] != paste_id]
    save_data(data)
    return redirect(url_for('index'))

@app.route('/search')
def search():
    """Halaman pencarian"""
    query = request.args.get('q', '').strip()
    results = []
    
    if query:
        data = load_data()
        # Pastikan data adalah list
        if isinstance(data, list):
            for paste in data:
                if (query.lower() in paste['title'].lower() or 
                    query.lower() in paste['content'].lower() or
                    query.lower() in paste['author'].lower()):
                    results.append(paste)
    
    return render_template('search.html', query=query, results=results)

if __name__ == '__main__':
    # Inisialisasi file data saat aplikasi dimulai
    init_data_file()
    app.run(debug=True)