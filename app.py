from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db, SucTuruGenel, CezaTuru, EgitimDurumu, IlKisiSayisi, InfazDavet, IsDurumu, MedeniDurum, UyrukCinsiyet, YerlesimYeri, Yas
import traceback
from flask_migrate import Migrate
from sqlalchemy import func, text
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
def get_tablo_verileri(tablo):
    """Seçilen tablonun verilerini döndürür"""
    try:
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

        # Sorgu oluştur
        query = db.session.query(model)

        # Filtreleri uygula
        for key, value in request.args.items():
            if value and hasattr(model, key) and key != 'kisi_sayisi':
                query = query.filter(getattr(model, key) == value)

        # Gruplandırma için kullanılacak sütunları belirle
        group_columns = [column.name for column in model.__table__.columns 
                        if column.name not in ['id', 'kisi_sayisi']]
        
        # Sorguyu gruplandır ve kisi_sayisi toplamını al
        query = db.session.query(
            *[getattr(model, col) for col in group_columns],
            func.sum(model.kisi_sayisi).label('kisi_sayisi')
        ).filter(*[getattr(model, key) == value for key, value in request.args.items() if value and hasattr(model, key) and key != 'kisi_sayisi']) \
         .group_by(*[getattr(model, col) for col in group_columns])

        results = query.all()

        # Sonuçları JSON formatına dönüştür
        data = []
        for item in results:
            row = {}
            for i, col in enumerate(group_columns):
                row[col] = getattr(item, col)
            row['kisi_sayisi'] = int(item.kisi_sayisi)  # Decimal'i int'e çevir
            data.append(row)

        # Sonuçları sırala (örneğin yıla göre)
        if 'yıl' in group_columns:
            data.sort(key=lambda x: x['yıl'])

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
            {'id': 'suc_turu_genel', 'ad': 'Suç Türü Genel'},
            {'id': 'uyruk_ve_cinsiyet', 'ad': 'Uyruk ve Cinsiyet'},
            {'id': 'yas', 'ad': 'Yaş'},
            {'id': 'yerlesim_yeri', 'ad': 'Yerleşim Yeri'}
        ]
        print("Gönderilen tablolar:", tablolar)  # Debug için
        return jsonify(tablolar)
    except Exception as e:
        print(f"Hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/<tablo>/kolonlar')
def get_tablo_kolonlari(tablo):
    """Seçilen tablonun filtrelenebilir kolonlarını döndürür"""
    try:
        kolon_map = {
            'ceza_turu': ['ceza_turu', 'cinsiyet', 'yıl'],
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
        
        return jsonify(kolon_map.get(tablo, []))
    except Exception as e:
        print(f"Hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/<tablo>/unique-values/<column>')
def get_unique_values(tablo, column):
    """Herhangi bir tablo için benzersiz değerleri döndürür"""
    try:
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
            
        if not hasattr(model, column):
            return jsonify({'error': 'Geçersiz kolon adı'}), 400
            
        values = db.session.query(getattr(model, column))\
            .distinct()\
            .filter(getattr(model, column).isnot(None))\
            .order_by(getattr(model, column))\
            .all()
            
        unique_values = [value[0] for value in values if value[0] is not None]
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
    return jsonify([
        'suc_turu',
        'is_durumu',
        'cinsiyet',
        'yil'
    ])

@app.route('/api/is_durumu/unique-values/<column>')
def get_is_durumu_unique_values(column):
    """İş durumu tablosu için benzersiz değerleri döndürür"""
    try:
        print(f"İstenen kolon: {column}")  # Debug için
        
        # Sorguyu basitleştirelim
        if hasattr(IsDurumu, column):
            values = db.session.query(getattr(IsDurumu, column))\
                .distinct()\
                .filter(getattr(IsDurumu, column).isnot(None))\
                .order_by(getattr(IsDurumu, column))\
                .all()
            
            print(f"Veritabanından gelen {column} değerleri:", values)
            
            # None olmayan değerleri liste haline getir
            unique_values = [value[0] for value in values if value[0] is not None]
            print(f"İşlenmiş benzersiz değerler ({column}):", unique_values)
            
            return jsonify(unique_values)
        else:
            return jsonify({'error': f'Geçersiz kolon adı: {column}'}), 400
            
    except Exception as e:
        print(f"Hata detayı ({column}):", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002) 

