from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import os
import warnings

# Untuk pengolahan data
from zipfile import ZipFile
from pathlib import Path

# Untuk visualisasi data
import seaborn as sns
import matplotlib.pyplot as plt

# %matplotlib inline
sns.set_palette('Set1')
sns.set()

# Untuk pemodelan // DISACTIVE oneDNN
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Untuk menghilangkan warnings saat plotting seaborn
warnings.filterwarnings('ignore')

# Initialize Flask app
app = Flask(__name__)

# Fungsi untuk memuat dataset yang ada
def load_datasets():
    try:
        rating = pd.read_csv('D:/code/Data Mining/tourism_rating.csv')
        place = pd.read_csv('D:/code/Data Mining/tourism_with_id.csv')
        user = pd.read_csv('D:/code/Data Mining/user.csv')
        return rating, place, user
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None, None, None

# New
from flask import Flask, render_template, url_for

app = Flask(__name__, static_folder='static')
# EndNew

# Rute untuk menampilkan halaman index
@app.route('/')
def home():
    rating, place, user = load_datasets()
    
    if place is not None:
        # Filter tempat wisata hanya untuk Bandung
        bandung_places = place[place['City'] == 'Bandung']
        
        # Ambil hanya nama tempat wisata di Bandung
        tempat_wisata_bandung = bandung_places['Place_Name'].tolist()

        # Variable data yang diperlukan
        tempat_wisata = place['Place_Name'].tolist()
        
        # Drop kolom yang tidak diperlukan 
        place = place.drop(['Unnamed: 11','Unnamed: 12'], axis=1)
        
        # Hitung jumlah rating per Place_Id
        rating_count = rating['Place_Id'].value_counts().reset_index()
        rating_count.columns = ['Place_Id', 'Total_Rating'] 

        # Gabungkan dengan tempat wisata (place)
        merged_df = place.merge(rating_count, on='Place_Id', how='left')

        # Filter hanya untuk lokasi tertentu (misalnya Bandung)
        bandung_places = merged_df[merged_df['City'] == 'Bandung']

        # Urutkan berdasarkan Total_Rating terbesar
        sorted_bandung_places = bandung_places.sort_values(by='Total_Rating', ascending=False)

        # Modifikasi nama kolom agar lebih mudah dibaca
        sorted_bandung_places = sorted_bandung_places.rename(columns={
            'Place_Id': 'ID Tempat',
            'Place_Name': 'Nama Tempat',
            'City': 'Kota',
            'Total_Rating': 'Jumlah Rating'
        })
         
        # Hapus kolom 'ID Tempat' hanya untuk tabel yang akan ditampilkan di HTML
        sorted_bandung_places_for_html = sorted_bandung_places.drop(columns=['ID Tempat'])

        # Reset index agar tidak ada index tambahan dari DataFrame
        sorted_bandung_places_for_html = sorted_bandung_places.drop(columns=['ID Tempat']).reset_index(drop=True)
        
        # Tambahkan kolom "No" dengan nomor urut dimulai dari 1
        sorted_bandung_places_for_html.insert(0, 'No', range(1, len(sorted_bandung_places_for_html) + 1))
        
        # Convert ke HTML table tanpa 'ID Tempat'
        place_preview = sorted_bandung_places_for_html[['No', 'Nama Tempat', 'Kota', 'Jumlah Rating']].head(10).to_html(classes='table table-hover table-bordered table-striped text-center table-rounded ', index=False,header=True)
        
        # Menampilkan index
        return render_template('index.html', place_preview=place_preview, tempat_wisata=tempat_wisata_bandung)
    
    else:
        return "Error loading datasets"
    
# rute get data
@app.route('/get_place_data')
def get_place_data():
    destination = request.args.get('destination')
    rating, place, user = load_datasets()
    
    if place is not None:
        # Filter tempat wisata berdasarkan pilihan
        selected_place = place[place['Place_Name'] == destination]
        
        # Hitung jumlah rating per Place_Id
        rating_count = rating['Place_Id'].value_counts().reset_index()
        rating_count.columns = ['Place_Id', 'Total_Rating'] 

        # Gabungkan dengan tempat wisata (place)
        merged_df = selected_place.merge(rating_count, on='Place_Id', how='left')

        # Modifikasi nama kolom agar lebih mudah dibaca
        merged_df = merged_df.rename(columns={
            'Place_Id': 'ID Tempat',
            'Place_Name': 'Nama Tempat',
            'City': 'Kota',
            'Total_Rating': 'Jumlah Rating',
            'Description': 'Deskripsi',
            'Price': 'Harga'  
        })

        # Hapus kolom 'ID Tempat' hanya untuk tampilan HTML
        merged_df_for_html = merged_df.drop(columns=['ID Tempat']).reset_index(drop=True)

        # Tambahkan kolom "No" dengan nomor urut dimulai dari 1
        merged_df_for_html.insert(0, 'No', range(1, len(merged_df_for_html) + 1))

        # Memastikan hanya kolom harga yang memiliki kelas 'price'
        merged_df_for_html['Harga'] = merged_df_for_html['Harga'].apply(lambda x: f'<span class="price">{x}</span>')

        # Convert DataFrame ke HTML
        place_preview = merged_df_for_html[['No', 'Nama Tempat', 'Kota', 'Jumlah Rating', 'Deskripsi', 'Harga']].to_html(
            classes='table table-hover table-bordered table-striped text-center table-rounded',
            index=False,
            escape=False  
        )

        return place_preview
    else:
        return "Error loading datasets"


if name == 'main':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
