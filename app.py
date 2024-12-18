from flask import Flask, request, jsonify, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db, SucTuruGenel, CezaTuru, EgitimDurumu, IlKisiSayisi, InfazDavet, IsDurumu, MedeniDurum, UyrukCinsiyet, YerlesimYeri, Yas
import traceback
from flask_migrate import Migrate
from sqlalchemy import func, text, distinct
from config import Config
from math import ceil  # get_paginated_data fonksiyonu için gerekli

app = Flask(__name__)
app.config.from_object(Config)

# CORS ayarlarını güncelle
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Güvenlik başlıklarını ekle
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

db.init_app(app)
migrate = Migrate(app, db)

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
def get_filtered_data(tablo):
    try:
        # Model haritası
        model_map = {
            'ceza_turu': CezaTuru,
            'egitim_durumu': EgitimDurumu,
            'il_kisi_sayisi': IlKisiSayisi,
            'infaza_davet_sekli': InfazDavet,
            'is_durumu': IsDurumu,
            'medeni_durum': MedeniDurum,
            'suc_turu_genel': SucTuruGenel,
            'uyruk_ve_cinsiyet': UyrukCinsiyet,
            'yas': Yas,
            'yerlesim_yeri': YerlesimYeri
        }
        
        model = model_map.get(tablo)
        if not model:
            return jsonify({'success': False, 'error': 'Geçersiz tablo adı'}), 400
            
        # Base query
        query = db.session.query(model)
        
        # URL'den gelen tüm filtreleri uygula
        for key, value in request.args.items():
            if value and hasattr(model, key):
                query = query.filter(getattr(model, key) == value)
        
        # Sonuçları al
        results = query.all()
        
        # Sonuçları JSON'a dönüştür
        data = []
        for row in results:
            item = {}
            for column in row.__table__.columns:
                value = getattr(row, column.name)
                # Integer değerleri düzgün formatla
                if isinstance(value, int):
                    item[column.name] = int(value)
                else:
                    item[column.name] = value
            data.append(item)
        
        print(f"Filtreler: {request.args}")
        print(f"Bulunan sonuç sayısı: {len(data)}")
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(data)
        })
        
    except Exception as e:
        print(f"Veri getirme hatası: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Veriler getirilirken bir hata oluştu: {str(e)}'
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
            {'id': 'infaza_davet_sekli', 'ad': 'İnfaza Davet Şekli'},
            {'id': 'is_durumu', 'ad': 'İş Durumu'},
            {'id': 'medeni_durum', 'ad': 'Medeni Durum'},
            {'id': 'suc_turu_genel', 'ad': 'Suç Türü'},
            {'id': 'uyruk_ve_cinsiyet', 'ad': 'Uyruk ve Cinsiyet'},
            {'id': 'yas', 'ad': 'Yaş'},
            {'id': 'yerlesim_yeri', 'ad': 'Yerleşim Yeri'}
        ]
        return jsonify(tablolar)
    except Exception as e:
        print(f"Hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

def format_column_name(column_name):
    """Kolon isimlerini düzgün formata çevirir"""
    replacements = {
        'suc_turu': 'Suç Türü',
        'egitim_durumu': 'Eğitim Durumu',
        'cinsiyet': 'Cinsiyet',
        'il': 'İl',
        'yil': 'Yıl',
        'yas': 'Yaş',
        'infaza_davet_sekli': 'İnfaza Davet Şekli',
        'is_durumu': 'İş Durumu',
        'medeni_durum': 'Medeni Durum',
        'yerlesim_yeri': 'Yerleşim Yeri',
        'yerlesim_yeri_ulke': 'Yerleşim Yeri (Ülke)',
        'uyruk': 'Uyruk',
        'ceza_turu': 'Ceza Türü'
    }
    return replacements.get(column_name, column_name.replace('_', ' ').title())

@app.route('/api/<tablo>/kolonlar')
def get_tablo_kolonlari(tablo):
    """Seçilen tablonun filtrelenebilir kolonlarını döndürür"""
    try:
        kolon_map = {
            'ceza_turu': ['ceza_turu', 'cinsiyet', 'yil'],
            'egitim_durumu': ['suc_turu', 'egitim_durumu', 'cinsiyet', 'il', 'yil'],
            'il_kisi_sayisi': ['il', 'yil'],
            'infaza_davet_sekli': ['suc_turu', 'infaza_davet_sekli', 'cinsiyet', 'yil'],
            'is_durumu': ['suc_turu', 'is_durumu', 'cinsiyet', 'il', 'yil'],
            'medeni_durum': ['suc_turu', 'medeni_durum', 'cinsiyet', 'il'],
            'suc_turu_genel': ['suc_turu', 'il', 'yil'],
            'uyruk_ve_cinsiyet': ['uyruk', 'cinsiyet', 'il', 'yil'],
            'yas': ['yas', 'cinsiyet', 'il', 'yil'],
            'yerlesim_yeri': ['yerlesim_yeri_ulke', 'cinsiyet', 'yerlesim_yeri', 'yil']
        }
        
        kolonlar = kolon_map.get(tablo, [])
        formatted_kolonlar = []
        for kolon in kolonlar:
            if kolon == 'yil':
                formatted_kolonlar.append('Yıl')
            elif kolon == 'ceza_turu':
                formatted_kolonlar.append('Ceza Türü')
            else:
                formatted_kolonlar.append(format_column_name(kolon))
        
        print(f"Tablo: {tablo}, Kolonlar: {kolonlar}, Formatlanmış: {formatted_kolonlar}")  # Debug log
        return jsonify(formatted_kolonlar)
    except Exception as e:
        print(f"Hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/<tablo>/unique-values/<column>')
def get_unique_values(tablo, column):
    try:
        print(f"İstenen tablo: {tablo}, kolon: {column}")
        
        model_map = {
            'ceza_turu': CezaTuru,
            'egitim_durumu': EgitimDurumu,
            'il_kisi_sayisi': IlKisiSayisi,
            'infaza_davet_sekli': InfazDavet,
            'is_durumu': IsDurumu,
            'medeni_durum': MedeniDurum,
            'suc_turu_genel': SucTuruGenel,
            'uyruk_ve_cinsiyet': UyrukCinsiyet,
            'yas': Yas,
            'yerlesim_yeri': YerlesimYeri
        }
        
        model = model_map.get(tablo)
        if not model:
            return jsonify({'error': 'Geçersiz tablo adı'}), 400
            
        # Yıl kolonu için özel sorgu
        if column == 'yil':
            try:
                # Direkt SQL sorgusu ile dene
                sql_query = f"""
                SELECT DISTINCT yil 
                FROM {model.__tablename__}
                WHERE yil IS NOT NULL 
                ORDER BY yil;
                """
                result = db.session.execute(sql_query)
                values = [row[0] for row in result if row[0] is not None]
                
                if not values:
                    # Eğer 'yil' çalışmazsa 'yıl' ile dene
                    sql_query = f"""
                    SELECT DISTINCT "yıl" as yil 
                    FROM {model.__tablename__}
                    WHERE "yıl" IS NOT NULL 
                    ORDER BY "yıl";
                    """
                    result = db.session.execute(sql_query)
                    values = [row[0] for row in result if row[0] is not None]
                
                values.sort(key=lambda x: int(x) if str(x).isdigit() else x)
                print(f"Yıl değerleri ({tablo}): {values}")
                return jsonify(values)
                
            except Exception as e:
                print(f"SQL sorgusu başarısız: {str(e)}")
                # SQL başarısız olursa ORM ile dene
                values = db.session.query(getattr(model, column))\
                    .distinct()\
                    .filter(getattr(model, column).isnot(None))\
                    .order_by(getattr(model, column))\
                    .all()
                
                unique_values = [value[0] for value in values if value[0] is not None]
                unique_values.sort(key=lambda x: int(x) if str(x).isdigit() else x)
                return jsonify(unique_values)
        
        # Diğer kolonlar için normal işlem
        if not hasattr(model, column):
            return jsonify({'error': f'Geçersiz kolon adı: {column}'}), 400
            
        values = db.session.query(getattr(model, column))\
            .distinct()\
            .filter(getattr(model, column).isnot(None))\
            .order_by(getattr(model, column))\
            .all()
            
        unique_values = [value[0] for value in values if value[0] is not None]
        unique_values.sort()
        print(f"Döndürülen değerler ({column}): {unique_values}")
        
        return jsonify(unique_values)
        
    except Exception as e:
        print(f"Benzersiz değerler alınırken hata: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    db.session.rollback()
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500

@app.route('/api/ceza_turu/veriler')
def get_ceza_turu_verileri():
    """Ceza türü verilerini filtreleyerek döndürür"""
    try:
        # Filtre parametrelerini al
        ceza_turu = request.args.get('ceza_turu')  # ceza_turu_id yerine ceza_turu kullanıyoruz
        cinsiyet = request.args.get('cinsiyet')
        yil = request.args.get('yıl')
        
        # Base query
        query = db.session.query(
            CezaTuru.ceza_turu,
            CezaTuru.cinsiyet,
            CezaTuru.yıl,
            func.sum(CezaTuru.kisi_sayisi).label('kisi_sayisi')
        )
        
        # Filtreleri uygula
        if ceza_turu:
            query = query.filter(CezaTuru.ceza_turu == ceza_turu)
        if cinsiyet:
            query = query.filter(CezaTuru.cinsiyet == cinsiyet)
        if yil:
            query = query.filter(CezaTuru.yıl == yil)
        
        # Gruplama
        query = query.group_by(
            CezaTuru.ceza_turu,
            CezaTuru.cinsiyet,
            CezaTuru.yıl
        ).order_by(CezaTuru.yıl)  # Yıla göre sırala
        
        # Sonuçları al
        results = query.all()
        
        # Sonuçları JSON formatına dönüştür
        data = [{
            'ceza_turu': row.ceza_turu,
            'cinsiyet': row.cinsiyet,
            'yil': row.yıl,
            'kisi_sayisi': int(row.kisi_sayisi)
        } for row in results]
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(data)
        })
        
    except Exception as e:
        print(f"Sorgu hatası: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Sorgu yapılırken bir hata oluştu: {str(e)}'
        }), 500

@app.route('/api/egitim_durumu/veriler')
def get_egitim_durumu_verileri():
    """Eğitim durumu verilerini filtreleyerek döndürür"""
    try:
        # Filtre parametrelerini al
        suc_turu = request.args.get('suc_turu')
        egitim_durumu = request.args.get('egitim_durumu')
        cinsiyet = request.args.get('cinsiyet')
        il = request.args.get('il')
        yil = request.args.get('yil')
        
        print(f"Gelen il parametresi: {il}")  # Debug için
        
        # Base query
        query = db.session.query(
            EgitimDurumu.suc_turu,
            EgitimDurumu.egitim_durumu,
            EgitimDurumu.cinsiyet,
            EgitimDurumu.il,
            EgitimDurumu.il_id,  # il_id'yi de ekleyelim
            EgitimDurumu.yil,
            func.sum(EgitimDurumu.kisi_sayisi).label('kisi_sayisi')
        )
        
        # Filtreleri uygula
        if suc_turu:
            query = query.filter(EgitimDurumu.suc_turu == suc_turu)
        if egitim_durumu:
            query = query.filter(EgitimDurumu.egitim_durumu == egitim_durumu)
        if cinsiyet:
            query = query.filter(EgitimDurumu.cinsiyet == cinsiyet)
        if il:
            # İl filtresini hem il adı hem de il_id için kontrol et
            try:
                il_id = int(il)
                query = query.filter(EgitimDurumu.il_id == il_id)
            except ValueError:
                query = query.filter(EgitimDurumu.il == il)
        if yil:
            query = query.filter(EgitimDurumu.yil == yil)
        
        # Gruplama
        query = query.group_by(
            EgitimDurumu.suc_turu,
            EgitimDurumu.egitim_durumu,
            EgitimDurumu.cinsiyet,
            EgitimDurumu.il,
            EgitimDurumu.il_id,
            EgitimDurumu.yil
        ).order_by(
            EgitimDurumu.yil,
            EgitimDurumu.il
        )  # Yıl ve ile göre sırala
        
        print(f"SQL Sorgusu: {query}")  # Debug için
        
        # Sonuçları al
        results = query.all()
        
        # Sonuçları JSON formatına dönüştür
        data = [{
            'suc_turu': row.suc_turu,
            'egitim_durumu': row.egitim_durumu,
            'cinsiyet': row.cinsiyet,
            'il': row.il,
            'yil': row.yil,
            'kisi_sayisi': int(row.kisi_sayisi)
        } for row in results]
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(data)
        })
        
    except Exception as e:
        print(f"Sorgu hatası: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Sorgu yapılırken bir hata oluştu: {str(e)}'
        }), 500

@app.route('/api/il_kisi_sayisi/veriler')
def get_il_kisi_sayisi_verileri():
    """İl ve kişi sayısı verilerini filtreleyerek döndürür"""
    try:
        # Filtre parametrelerini al
        il = request.args.get('il')
        yil = request.args.get('yil')
        
        print(f"Gelen parametreler - il: {il}, yıl: {yil}")  # Debug için
        
        # Base query
        query = db.session.query(
            IlKisiSayisi.il,
            IlKisiSayisi.il_id,
            IlKisiSayisi.yil,
            func.sum(IlKisiSayisi.kisi_sayisi).label('kisi_sayisi')
        )
        
        # Filtreleri uygula
        if il:
            # İl filtresini hem il adı hem de il_id için kontrol et
            try:
                il_id = int(il)
                query = query.filter(IlKisiSayisi.il_id == il_id)
            except ValueError:
                query = query.filter(IlKisiSayisi.il == il)
        if yil:
            query = query.filter(IlKisiSayisi.yil == yil)
        
        # Gruplama
        query = query.group_by(
            IlKisiSayisi.il,
            IlKisiSayisi.il_id,
            IlKisiSayisi.yil
        ).order_by(
            IlKisiSayisi.yil,
            IlKisiSayisi.il
        )  # Yıl ve ile göre sırala
        
        print(f"SQL Sorgusu: {query}")  # Debug için
        
        # Sonuçları al
        results = query.all()
        
        # Sonuçları JSON formatına dönüştür
        data = [{
            'il': row.il,
            'yil': row.yil,
            'kisi_sayisi': int(row.kisi_sayisi)
        } for row in results]
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(data)
        })
        
    except Exception as e:
        print(f"Sorgu hatası: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Sorgu yapılırken bir hata oluştu: {str(e)}'
        }), 500

@app.route('/api/il_kisi_sayisi/unique-values/<column>')
def get_il_kisi_sayisi_unique_values(column):
    """İl ve kişi sayısı tablosu için benzersiz değerleri döndürür"""
    try:
        if column == 'il':
            # İlleri al ve sırala
            values = db.session.query(IlKisiSayisi.il)\
                .distinct()\
                .order_by(IlKisiSayisi.il)\
                .all()
            # Tuple'dan değerleri çıkar
            unique_values = [value[0] for value in values if value[0]]
            
        elif column == 'yil':
            # Yılları al ve sırala
            values = db.session.query(IlKisiSayisi.yil)\
                .distinct()\
                .order_by(IlKisiSayisi.yil)\
                .all()
            # Tuple'dan değerleri çıkar
            unique_values = [value[0] for value in values if value[0]]
        else:
            return jsonify({'error': 'Geçersiz kolon adı'}), 400

        print(f"Benzersiz {column} değerleri:", unique_values)  # Debug için
        return jsonify(unique_values)
        
    except Exception as e:
        print(f"Hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/infaza_davet_sekli/veriler')
def get_infaza_davet_verileri():
    """İnfaza davet şekli verilerini filtreleyerek döndürür"""
    try:
        # Filtre parametrelerini al
        suc_turu = request.args.get('suc_turu')
        infaza_davet_sekli = request.args.get('infaza_davet_sekli')
        cinsiyet = request.args.get('cinsiyet')
        yil = request.args.get('yil')
        
        # Base query
        query = db.session.query(
            InfazDavet.suc_turu,
            InfazDavet.infaza_davet_sekli,
            InfazDavet.cinsiyet,
            InfazDavet.yil,
            func.sum(InfazDavet.kisi_sayisi).label('kisi_sayisi')
        )
        
        # Filtreleri uygula
        if suc_turu:
            query = query.filter(InfazDavet.suc_turu == suc_turu)
        if infaza_davet_sekli:
            query = query.filter(InfazDavet.infaza_davet_sekli == infaza_davet_sekli)
        if cinsiyet:
            query = query.filter(InfazDavet.cinsiyet == cinsiyet)
        if yil:
            query = query.filter(InfazDavet.yil == yil)
        
        # Gruplama
        query = query.group_by(
            InfazDavet.suc_turu,
            InfazDavet.infaza_davet_sekli,
            InfazDavet.cinsiyet,
            InfazDavet.yil
        ).order_by(
            InfazDavet.yil,
            InfazDavet.suc_turu
        )
        
        results = query.all()
        
        data = [{
            'suc_turu': row.suc_turu,
            'infaza_davet_sekli': row.infaza_davet_sekli,
            'cinsiyet': row.cinsiyet,
            'yil': row.yil,
            'kisi_sayisi': int(row.kisi_sayisi)
        } for row in results]
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(data)
        })
        
    except Exception as e:
        print(f"Sorgu hatası: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Sorgu yapılırken bir hata oluştu: {str(e)}'
        }), 500

@app.route('/api/infaza_davet_sekli/unique-values/<column>')
def get_infaza_davet_unique_values(column):
    try:
        print(f"İstenen kolon için sorgu başlıyor: {column}")  # Debug log
        
        # Sorgu oluştur
        query = None
        if hasattr(InfazDavet, column):
            query = db.session.query(getattr(InfazDavet, column))\
                .distinct()\
                .filter(getattr(InfazDavet, column).isnot(None))\
                .order_by(getattr(InfazDavet, column))
                
            print(f"SQL Sorgusu: {query}")  # Debug log
            
            values = query.all()
            print(f"Sorgu sonuçları: {values}")  # Debug log
            
            unique_values = [value[0] for value in values if value[0]]
            print(f"İşlenmiş sonuçlar: {unique_values}")  # Debug log
            
            return jsonify(unique_values)
        else:
            print(f"Hata: {column} kolonu bulunamadı")  # Debug log
            return jsonify({'error': f'Geçersiz kolon adı: {column}'}), 400
            
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/is_durumu/veriler')
def get_is_durumu_verileri():
    """İş durumu verilerini filtreleyerek döndürür"""
    try:
        # Filtre parametrelerini al
        suc_turu = request.args.get('suc_turu')
        is_durumu = request.args.get('is_durumu')
        cinsiyet = request.args.get('cinsiyet')
        yil = request.args.get('yil')
        
        # Base query
        query = db.session.query(
            IsDurumu.suc_turu,
            IsDurumu.is_durumu,
            IsDurumu.cinsiyet,
            IsDurumu.yil,
            func.sum(IsDurumu.kisi_sayisi).label('kisi_sayisi')
        )
        
        # Filtreleri uygula
        if suc_turu:
            query = query.filter(IsDurumu.suc_turu == suc_turu)
        if is_durumu:
            query = query.filter(IsDurumu.is_durumu == is_durumu)
        if cinsiyet:
            query = query.filter(IsDurumu.cinsiyet == cinsiyet)
        if yil:
            query = query.filter(IsDurumu.yil == yil)
        
        # Gruplama
        query = query.group_by(
            IsDurumu.suc_turu,
            IsDurumu.is_durumu,
            IsDurumu.cinsiyet,
            IsDurumu.yil
        ).order_by(
            IsDurumu.yil,
            IsDurumu.suc_turu
        )
        
        results = query.all()
        
        data = [{
            'suc_turu': row.suc_turu,
            'is_durumu': row.is_durumu,
            'cinsiyet': row.cinsiyet,
            'yil': row.yil,
            'kisi_sayisi': int(row.kisi_sayisi)
        } for row in results]
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(data)
        })
        
    except Exception as e:
        print(f"Sorgu hatası: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Sorgu yapılırken bir hata oluştu: {str(e)}'
        }), 500

@app.route('/api/is_durumu/kolonlar')
def get_is_durumu_kolonlari():
    """İş durumu tablosunun filtrelenebilir kolonlarını döndürür"""
    try:
        kolonlar = ['suc_turu', 'is_durumu', 'cinsiyet', 'il', 'yil']
        formatted_kolonlar = []
        for kolon in kolonlar:
            if kolon == 'suc_turu':
                formatted_kolonlar.append('Suç Türü')
            elif kolon == 'is_durumu':
                formatted_kolonlar.append('İş Durumu')
            elif kolon == 'cinsiyet':
                formatted_kolonlar.append('Cinsiyet')
            elif kolon == 'il':
                formatted_kolonlar.append('İl')
            elif kolon == 'yil':
                formatted_kolonlar.append('Yıl')
        
        print(f"İş durumu kolonları: {formatted_kolonlar}")  # Debug log
        return jsonify(formatted_kolonlar)
    except Exception as e:
        print(f"Hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/is_durumu/unique-values/<column>')
def get_is_durumu_unique_values(column):
    """İş durumu tablosu için benzersiz değerleri döndürür"""
    try:
        print(f"İstenen kolon: {column}")  # Debug için
        
        # Özel durum: Yıl kolonu için
        if column == 'yil':
            values = db.session.query(IsDurumu.yil)\
                .distinct()\
                .filter(IsDurumu.yil.isnot(None))\
                .order_by(IsDurumu.yil)\
                .all()
            
            unique_values = [value[0] for value in values if value[0] is not None]
            unique_values.sort(key=lambda x: int(x) if str(x).isdigit() else x)
            print(f"Yıl değerleri: {unique_values}")
            return jsonify(unique_values)
        
        # Diğer kolonlar için normal işlem
        if hasattr(IsDurumu, column):
            values = db.session.query(getattr(IsDurumu, column))\
                .distinct()\
                .filter(getattr(IsDurumu, column).isnot(None))\
                .order_by(getattr(IsDurumu, column))\
                .all()
            
            unique_values = [value[0] for value in values if value[0] is not None]
            unique_values.sort()
            print(f"İşlenmiş benzersiz değerler ({column}): {unique_values}")
            
            return jsonify(unique_values)
        else:
            return jsonify({'error': f'Geçersiz kolon adı: {column}'}), 400
            
    except Exception as e:
        print(f"Hata detayı ({column}):", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/veri-analizi/')
def veri_analizi():
    try:
        return render_template('veri_analizi.html')
    except Exception as e:
        print(f"Veri analizi sayfası yüklenirken hata: {str(e)}")
        return f"Hata: {str(e)}", 500

@app.route('/api/dashboard/summary')
def get_dashboard_summary():
    try:
        # Toplam kişi sayısı
        total_people = db.session.query(func.sum(SucTuruGenel.kisi_sayisi)).scalar() or 0
        
        # Toplam il sayısı
        total_cities = db.session.query(func.count(distinct(SucTuruGenel.il))).scalar() or 0
        
        # Yıl aralığı
        min_year = db.session.query(func.min(SucTuruGenel.yil)).scalar() or 0
        max_year = db.session.query(func.max(SucTuruGenel.yil)).scalar() or 0
        
        # Toplam suç kategorisi
        total_categories = db.session.query(func.count(distinct(SucTuruGenel.suc_turu))).scalar() or 0
        
        return jsonify({
            'total_people': int(total_people),
            'total_cities': total_cities,
            'min_year': min_year,
            'max_year': max_year,
            'total_categories': total_categories
        })
        
    except Exception as e:
        print(f"Dashboard özeti alınırken hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Diğer dashboard API endpoint'leri
@app.route('/api/dashboard/yearly-distribution')
def get_yearly_distribution():
    try:
        # Yıllara göre toplam suç sayısı
        results = db.session.query(
            SucTuruGenel.yil,
            func.sum(SucTuruGenel.kisi_sayisi).label('total')
        ).group_by(SucTuruGenel.yil)\
         .order_by(SucTuruGenel.yil)\
         .all()
        
        return jsonify({
            'labels': [str(r.yil) for r in results],
            'values': [int(r.total) for r in results]
        })
    except Exception as e:
        print(f"Yıllık dağılım alınırken hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/cities-distribution')
def get_cities_distribution():
    try:
        # İllere göre toplam suç sayısı (ilk 10)
        results = db.session.query(
            SucTuruGenel.il,
            func.sum(SucTuruGenel.kisi_sayisi).label('total')
        ).group_by(SucTuruGenel.il)\
         .order_by(func.sum(SucTuruGenel.kisi_sayisi).desc())\
         .limit(10)\
         .all()
        
        return jsonify({
            'labels': [r.il for r in results],
            'values': [int(r.total) for r in results]
        })
    except Exception as e:
        print(f"İl dağılımı alınırken hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/gender-distribution')
def get_gender_distribution():
    try:
        # Cinsiyete göre toplam suç sayısı
        results = db.session.query(
            EgitimDurumu.cinsiyet,
            func.sum(EgitimDurumu.kisi_sayisi).label('total')
        ).group_by(EgitimDurumu.cinsiyet)\
         .all()
        
        return jsonify({
            'labels': [r.cinsiyet for r in results],
            'values': [int(r.total) for r in results]
        })
    except Exception as e:
        print(f"Cinsiyet dağılımı alınırken hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/education-distribution')
def get_education_distribution():
    try:
        # Eğitim durumuna göre toplam suç sayısı
        results = db.session.query(
            EgitimDurumu.egitim_durumu,
            func.sum(EgitimDurumu.kisi_sayisi).label('total')
        ).group_by(EgitimDurumu.egitim_durumu)\
         .order_by(func.sum(EgitimDurumu.kisi_sayisi).desc())\
         .all()
        
        return jsonify({
            'labels': [r.egitim_durumu for r in results],
            'values': [int(r.total) for r in results]
        })
    except Exception as e:
        print(f"Eğitim durumu dağılımı alınırken hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/yas/unique-values/<column>')
def get_yas_unique_values(column):
    """Yaş tablosu için benzersiz değerleri döndürür"""
    try:
        print(f"Yaş tablosu için istenen kolon: {column}")  # Debug log
        
        if column == 'yas':
            # Yaş değerlerini al
            values = db.session.query(Yas.yas)\
                .distinct()\
                .filter(Yas.yas.isnot(None))\
                .order_by(Yas.yas)\
                .all()
            
            unique_values = [value[0] for value in values if value[0] is not None]
            print(f"Yaş değerleri: {unique_values}")  # Debug log
            return jsonify(unique_values)
            
        elif column in ['cinsiyet', 'il', 'yil']:
            # Diğer kolonlar için
            values = db.session.query(getattr(Yas, column))\
                .distinct()\
                .filter(getattr(Yas, column).isnot(None))\
                .order_by(getattr(Yas, column))\
                .all()
                
            unique_values = [value[0] for value in values if value[0] is not None]
            print(f"{column} değerleri: {unique_values}")  # Debug log
            return jsonify(unique_values)
        else:
            return jsonify({'error': f'Geçersiz kolon adı: {column}'}), 400
            
    except Exception as e:
        print(f"Yaş değerleri alınırken hata: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-columns')
def check_columns():
    try:
        sql_query = """
        SELECT table_name, column_name 
        FROM information_schema.columns 
        WHERE column_name LIKE '%y_l%' 
        OR column_name LIKE '%yil%'
        """
        result = db.session.execute(sql_query)
        columns = [(row[0], row[1]) for row in result]
        return jsonify(columns)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/grafikler')
def grafikler():
    return render_template('grafikler.html')

@app.route('/api/<tablo>/grafik-veriler')
def get_grafik_veriler(tablo):
    try:
        # Model haritası
        model_map = {
            'ceza_turu': CezaTuru,
            'egitim_durumu': EgitimDurumu,
            'il_kisi_sayisi': IlKisiSayisi,
            'infaza_davet_sekli': InfazDavet,
            'is_durumu': IsDurumu,
            'medeni_durum': MedeniDurum,
            'suc_turu_genel': SucTuruGenel,
            'uyruk_ve_cinsiyet': UyrukCinsiyet,
            'yas': Yas,
            'yerlesim_yeri': YerlesimYeri
        }
        
        model = model_map.get(tablo)
        if not model:
            return jsonify({'success': False, 'error': 'Geçersiz tablo adı'}), 400
            
        # Base query
        query = db.session.query(model)
        
        # URL'den gelen tüm filtreleri uygula
        for key, value in request.args.items():
            if value and hasattr(model, key):
                query = query.filter(getattr(model, key) == value)
        
        # Sonuçları al
        results = query.all()
        
        # Sonuçları JSON'a dönüştür
        data = []
        for row in results:
            item = {}
            for column in row.__table__.columns:
                value = getattr(row, column.name)
                # Integer değerleri düzgün formatla
                if isinstance(value, int):
                    item[column.name] = int(value)
                else:
                    item[column.name] = value
            data.append(item)
        
        print(f"Filtreler: {request.args}")
        print(f"Bulunan sonuç sayısı: {len(data)}")
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(data)
        })
        
    except Exception as e:
        print(f"Grafik verileri alınırken hata: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Veriler getirilirken bir hata oluştu: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002) 

