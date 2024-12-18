from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class CezaTuru(db.Model):
    __tablename__ = 'ceza_turu'
    id = db.Column(db.Integer, primary_key=True)
    ceza_turu_id = db.Column(db.Integer)
    ceza_turu = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    yil = db.Column('yil', db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class EgitimDurumu(db.Model):
    __tablename__ = 'egitim_durumu'
    id = db.Column(db.Integer, primary_key=True)
    suc_turu_id = db.Column(db.Integer)
    suc_turu = db.Column(db.String)
    egitim_durumu_id = db.Column(db.Integer)
    egitim_durumu = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    il = db.Column(db.String)
    il_id = db.Column(db.Integer)
    yil = db.Column('yil', db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class IlKisiSayisi(db.Model):
    __tablename__ = 'il_ve_kisi_sayisi'
    id = db.Column(db.Integer, primary_key=True)
    il = db.Column(db.String)
    il_id = db.Column(db.Integer)
    yil = db.Column('yil', db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class InfazDavet(db.Model):
    __tablename__ = 'infaza_davet_sekli'
    id = db.Column(db.Integer, primary_key=True)
    suc_turu_id = db.Column(db.Integer)
    suc_turu = db.Column(db.String)
    infaza_davet_id = db.Column(db.Integer)
    infaza_davet_sekli = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    yil = db.Column('yil', db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class IsDurumu(db.Model):
    __tablename__ = 'is_durumu'
    id = db.Column(db.Integer, primary_key=True)
    suc_turu_id = db.Column(db.Integer)
    suc_turu = db.Column(db.String)
    is_durumu_id = db.Column(db.Integer)
    is_durumu = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    il = db.Column(db.String)
    il_id = db.Column(db.Integer)
    kisi_sayisi = db.Column(db.Integer)
    yil = db.Column('yil', db.Integer)

class MedeniDurum(db.Model):
    __tablename__ = 'medeni_durum'
    id = db.Column(db.Integer, primary_key=True)
    suc_turu_id = db.Column(db.Integer)
    suc_turu = db.Column(db.String)
    medeni_durum_id = db.Column(db.Integer)
    medeni_durum = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    il = db.Column(db.String)
    il_id = db.Column(db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class SucTuruGenel(db.Model):
    __tablename__ = 'suc_turu_genel'
    id = db.Column(db.Integer, primary_key=True)
    suc_turu_id = db.Column(db.Integer)
    suc_turu = db.Column(db.String)
    il = db.Column(db.String)
    il_id = db.Column(db.Integer)
    yil = db.Column('yil', db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class UyrukCinsiyet(db.Model):
    __tablename__ = 'uyruk_ve_cinsiyet'
    id = db.Column(db.Integer, primary_key=True)
    uyruk = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    il = db.Column(db.String)
    il_id = db.Column(db.Integer)
    yil = db.Column('yil', db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class Yas(db.Model):
    __tablename__ = 'yas'
    yas = db.Column(db.Integer, primary_key=True)
    cinsiyet = db.Column(db.String)
    il = db.Column(db.String)
    il_id = db.Column(db.Integer)
    yil = db.Column('yil', db.Integer)
    kisi_sayisi = db.Column(db.Integer)

class YerlesimYeri(db.Model):
    __tablename__ = 'yerlesim_yeri'
    id = db.Column(db.Integer, primary_key=True)
    yerlesim_yeri_ulke = db.Column(db.String)
    cinsiyet = db.Column(db.String)
    yerlesim_yeri = db.Column(db.String)
    yerlesim_yeri_id = db.Column(db.Integer)
    yil = db.Column('yil', db.Integer)
    kisi_sayisi = db.Column(db.Integer)