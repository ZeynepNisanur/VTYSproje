from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db, SucTuruGenel, CezaTuru, EgitimDurumu, IlKisiSayisi, InfazDavet, IsDurumu, IsDurumuCinsiyet, MedeniDurum, UyrukCinsiyet, YerlesimYeri, Yas
import traceback
from flask_migrate import Migrate
from sqlalchemy import func, text
from config import Config
from math import ceil  # get_paginated_data fonksiyonu için gerekli

app = Flask(__name__)
app.config.from_object(Config)

# CORS ayarlarını güncelle
CORS(app, supports_credentials=True)

# Güvenlik başlıklarını ekle
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

db.init_app(app)
migrate = Migrate(app, db)

# Veritabanı tablolarını oluşturmak için context manager
def create_tables():
    with app.app_context():
        # Mevcut tabloları kontrol et, yoksa oluştur
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # Sadece olmayan tabloları oluştur
        db.create_all()
        print("Veritabanı tabloları kontrol edildi!")

# Ana sayfa route'u
@app.route('/')
def index():
    return render_template('index.html')

# Veritabanı bağlantı testi
@app.route('/test-db')
def test_db():
    try:
        result = db.session.execute(text('SELECT 1')).scalar()
        return jsonify({
            'status': 'success',
            'message': f'Veritabanı bağlantısı başarılı! Test sonucu: {result}'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Bağlantı hatası: {str(e)}'
        }), 500

# Sayfalama ve filtreleme için yardımcı fonksiyon
def get_paginated_data(model, page=1, per_page=10, **filters):
    try:
        query = model.query
        
        # Filtreleri uygula
        for key, value in filters.items():
            if value and hasattr(model, key):
                query = query.filter(getattr(model, key) == value)
        
        # Toplam kayıt sayısı
        total_items = query.count()
        total_pages = ceil(total_items / per_page)
        
        # Sayfalama
        items = query.offset((page-1) * per_page).limit(per_page).all()
        
        return {
            'items': items,
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page
        }
    except Exception as e:
        print(f"Hata: {str(e)}")
        return None

# Örnek endpoint - sayfalı veri çekme
@app.route('/api/<tablo>/veriler')
def get_tablo_verileri(tablo):
    """Seçilen tablonun verilerini döndürür"""
    try:
        # Tablo sınıfını seç
        model_map = {
            'ceza_turu': CezaTuru,
            'egitim_durumu': EgitimDurumu,
            'il_kisi_sayisi': IlKisiSayisi,
            'infaz_davet': InfazDavet,
            'is_durumu': IsDurumu,
            'is_durumu_cinsiyet': IsDurumuCinsiyet,
            'medeni_durum': MedeniDurum,
            'suc_turu_genel': SucTuruGenel,
            'uyruk_cinsiyet': UyrukCinsiyet,
            'yerlesim_yeri': YerlesimYeri,
            'yas': Yas
        }
        
        model = model_map.get(tablo)
        if not model:
            return jsonify({'error': 'Geçersiz tablo adı'}), 400

        # Sorgu oluştur
        query = model.query

        # Filtreleri uygula
        for key, value in request.args.items():
            if value and hasattr(model, key) and key != 'kisi_sayisi':
                query = query.filter(getattr(model, key) == value)

        # Verileri çek
        results = query.all()

        # Sonuçları JSON formatına dönüştür
        data = []
        for item in results:
            row = {}
            for column in item.__table__.columns:
                row[column.name] = getattr(item, column.name)
            data.append(row)

        return jsonify({
            'success': True,
            'data': data,
            'total': len(data)
        })

    except Exception as e:
        print(f"Sorgu hatası: {str(e)}")  # Hata ayıklama için
        traceback.print_exc()  # Detaylı hata bilgisi
        return jsonify({
            'success': False,
            'error': f'Sorgu yapılırken bir hata oluştu: {str(e)}'
        }), 500

# Diğer route'lar buraya gelecek...

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Sayfa bulunamadı'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Veritabanı işlemlerini geri al
    return jsonify({'error': 'Sunucu hatası'}), 500

@app.route('/api/tablolar')
def get_tablolar():
    """Mevcut tüm tabloların listesini döndürür"""
    try:
        tablolar = [
            {'id': 'ceza_turu', 'ad': 'Ceza Türü'},
            {'id': 'egitim_durumu', 'ad': 'Eğitim Durumu'},
            {'id': 'il_kisi_sayisi', 'ad': 'İl ve Kişi Sayısı'},
            {'id': 'infaz_davet', 'ad': 'İnfaza Davet Şekli'},
            {'id': 'is_durumu', 'ad': 'İş Durumu'},
            {'id': 'is_durumu_cinsiyet', 'ad': 'İş Durumu ve Cinsiyet'},
            {'id': 'medeni_durum', 'ad': 'Medeni Durum'},
            {'id': 'suc_turu_genel', 'ad': 'Suç Türü Genel'},
            {'id': 'uyruk_cinsiyet', 'ad': 'Uyruk ve Cinsiyet'},
            {'id': 'yerlesim_yeri', 'ad': 'Yerleşim Yeri'},
            {'id': 'yas', 'ad': 'Yaş'}
        ]
        return jsonify(tablolar)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/<tablo>/kolonlar')
def get_tablo_kolonlari(tablo):
    """Seçilen tablonun kolonlarını döndürür"""
    try:
        # Tablo sınıfını seç
        model_map = {
            'ceza_turu': CezaTuru,
            'egitim_durumu': EgitimDurumu,
            'il_kisi_sayisi': IlKisiSayisi,
            'infaz_davet': InfazDavet,
            'is_durumu': IsDurumu,
            'is_durumu_cinsiyet': IsDurumuCinsiyet,
            'medeni_durum': MedeniDurum,
            'suc_turu_genel': SucTuruGenel,
            'uyruk_cinsiyet': UyrukCinsiyet,
            'yerlesim_yeri': YerlesimYeri,
            'yas': Yas
        }
        
        model = model_map.get(tablo)
        if not model:
            return jsonify({'error': 'Geçersiz tablo adı'}), 400
            
        # Tablo kolonlarını al
        kolonlar = [column.name for column in model.__table__.columns]
        return jsonify(kolonlar)
        
    except Exception as e:
        print(f"Hata: {str(e)}")  # Hata ayıklama için
        return jsonify({'error': str(e)}), 500

@app.route('/api/<tablo>/unique-values/<kolon>')
def get_unique_values(tablo, kolon):
    """Belirli bir kolonun benzersiz değerlerini döndürür"""
    try:
        # Tablo sınıfını seç
        model_map = {
            'ceza_turu': CezaTuru,
            'egitim_durumu': EgitimDurumu,
            'il_kisi_sayisi': IlKisiSayisi,
            'infaz_davet': InfazDavet,
            'is_durumu': IsDurumu,
            'is_durumu_cinsiyet': IsDurumuCinsiyet,
            'medeni_durum': MedeniDurum,
            'suc_turu_genel': SucTuruGenel,
            'uyruk_cinsiyet': UyrukCinsiyet,
            'yerlesim_yeri': YerlesimYeri,
            'yas': Yas
        }
        
        model = model_map.get(tablo)
        if not model:
            return jsonify({'error': 'Geçersiz tablo adı'}), 400
            
        if not hasattr(model, kolon):
            return jsonify({'error': 'Geçersiz kolon adı'}), 400
            
        # Kolonun benzersiz değerlerini al
        unique_values = db.session.query(getattr(model, kolon)).distinct().order_by(getattr(model, kolon)).all()
        # Tek boyutlu listeye çevir
        unique_values = [value[0] for value in unique_values if value[0] is not None]
        
        return jsonify(unique_values)
        
    except Exception as e:
        print(f"Hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    db.session.rollback()
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500

if __name__ == '__main__':
    create_tables()  # Tabloları oluştur
    app.run(debug=True, host='127.0.0.1', port=5001) 

