from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SucTuruGenel(db.Model):
    __tablename__ = 'suc_turu_genel'
    
    id = db.Column(db.Integer, primary_key=True)
    il = db.Column(db.String)
    ilce = db.Column(db.String)
    suc_turu = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    yas = db.Column(db.Integer)
    egitim_durumu = db.Column(db.String)
    medeni_durum = db.Column(db.String)
    meslek = db.Column(db.String)
    sayi = db.Column(db.Integer)
    # diğer gerekli alanları ekleyin 

class CezaTuru(db.Model):
    __tablename__ = 'ceza_turu'
    id = db.Column(db.Integer, primary_key=True)
    ceza_turu = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    yil = db.Column(db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class EgitimDurumu(db.Model):
    __tablename__ = 'egitim_durumu'
    id = db.Column(db.Integer, primary_key=True)
    egitim_durumu = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    yil = db.Column(db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class IlKisiSayisi(db.Model):
    __tablename__ = 'il_kisi_sayisi'
    id = db.Column(db.Integer, primary_key=True)
    il = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    yil = db.Column(db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class InfazDavet(db.Model):
    __tablename__ = 'infaz_davet'
    id = db.Column(db.Integer, primary_key=True)
    infaz_sekli = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    yil = db.Column(db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class IsDurumu(db.Model):
    __tablename__ = 'is_durumu'
    id = db.Column(db.Integer, primary_key=True)
    is_durumu = db.Column(db.String)
    yil = db.Column(db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class IsDurumuCinsiyet(db.Model):
    __tablename__ = 'is_durumu_cinsiyet'
    id = db.Column(db.Integer, primary_key=True)
    is_durumu = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    yil = db.Column(db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class MedeniDurum(db.Model):
    __tablename__ = 'medeni_durum'
    id = db.Column(db.Integer, primary_key=True)
    medeni_durum = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    yil = db.Column(db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class UyrukCinsiyet(db.Model):
    __tablename__ = 'uyruk_cinsiyet'
    id = db.Column(db.Integer, primary_key=True)
    uyruk = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    yil = db.Column(db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class YerlesimYeri(db.Model):
    __tablename__ = 'yerlesim_yeri'
    id = db.Column(db.Integer, primary_key=True)
    yerlesim_yeri_ulke = db.Column(db.String(100))
    cinsiyet = db.Column(db.String(50))
    yerlesim_yeri = db.Column(db.String(100))
    yerlesim_yeri_id = db.Column(db.Integer)
    yil = db.Column(db.SmallInteger)
    kisi_sayisi = db.Column(db.Integer)

class Yas(db.Model):
    __tablename__ = 'yas'
    
    id = db.Column(db.Integer, primary_key=True)
    yas = db.Column(db.Integer)
    cinsiyet = db.Column(db.String)
    il = db.Column(db.String)
    il_ID = db.Column(db.Integer)
    yil = db.Column(db.Integer)
    kisi_sayisi = db.Column(db.Integer)