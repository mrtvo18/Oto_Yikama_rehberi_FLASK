from orm_db import *
kullanici = {}

# Giriş işlemlerinin yer alacak olduğu işlemler
#giriş karşılama sayfası
@app.route('/', methods=['GET', 'POST'])
@app.route('/')
def index():
    isyerleri = Isyeri.query.filter_by(isyeri_durum=0).all()
    return render_template('index.html',isyerleri=isyerleri)

# Giriş işlemlerinin yer alacak olduğu işlemler
#giriş karşılama sayfası
@app.route('/yonetim', methods=['GET', 'POST'])
@app.route('/yonetim')
def yonetim():
    if request.method == 'POST':
        tc = request.form.get('tcno')
        sifre = request.form.get('sifre')

        if True:

            user = Yonetici.query.filter_by(yonetici_tc=tc, yonetici_sifre=sifre).first()
            if user.yonetici_durum == 0:
                session['yonetici'] = user.yonetici_id
                kullanici['yonetici'] = user
                return redirect(url_for('yonetici_sayfasi'))
            else:
                return render_template('yonetim.html', mesaj="Giriş Yapmak İstediğiniz Kullanıcı Aktif Değil")
        else:
            return render_template('yonetim.html', mesaj="Hatalı giriş Yapmaktasınız")
    else:
        return render_template('yonetim.html', mesaj="Hoş Geldiniz")



#çıkış işlemleri sayfası
@app.route('/cikis')
def cikis():
    session.clear()
    kullanici.clear()

    return redirect(url_for('index'))


#Aşağıdaki ilk bölümde yöneticilerin yapabilecek olduğu iş ve işlemlerin sayfa erişimleri yer almaktadır

#yönetici sayfası işlemleri
@app.route('/yonetici_sayfasi', methods=['GET', 'POST'])
@app.route('/yonetici_sayfasi')
def yonetici_sayfasi():
    try:
        isyerleri = Isyeri.query.all()
        return render_template("yonetici.html",yonetici=kullanici['yonetici'],isyerleri=isyerleri)
    except:
        return render_template('index.html', mesaj="Hoş Geldiniz")


# Personel İşlemleri Aşağıda Bölümde Yer Alacaktır

# personel ekleme işlemleri
@app.route('/personel_ekle', methods=['GET', 'POST'])
@app.route('/personel_ekle')
def personel_ekle():
    try:
        if request.method == 'POST':
            try:
                bilgiler = request.form.to_dict()
                yeni_personel = Yonetici(yonetici_adi_soyadi=bilgiler['yonetici_adi_soyadi'], yonetici_tc=bilgiler['yonetici_tc'],
                                 yonetici_sifre=bilgiler['yonetici_sifre'], yonetici_email=bilgiler['yonetici_email'],
                                 yonetici_tel=bilgiler['yonetici_tel'], yonetici_durum=int(bilgiler['yonetici_durum']),
                                )
                dbsession.add(yeni_personel)
                dbsession.commit()
                return render_template("personel_ekle.html", yonetici=kullanici['yonetici'], mesaj="Başarı")
            except:
                return render_template("personel_ekle.html", yonetici=kullanici['yonetici'] , mesaj="Başarısızlık")
        else:

            return render_template("personel_ekle.html", yonetici=kullanici['yonetici'])
    except:
        return render_template("personel_ekle.html", yonetici=kullanici['yonetici'])

# personel güncelleme ve silme işlemleri
@app.route('/personel_guncelle_sil/<int:id>')
@app.route('/personel_guncelle_sil')
def personel_guncelle_sil(id=0):
    if id == 0:
        personeller = Yonetici.query.all()
        return render_template("personel_guncelle_sil.html", yonetici=kullanici['yonetici'], personeller=personeller)
    else:
        return redirect(url_for('personel_guncelle_sil'))


@app.route('/personel_guncelle/<int:id>')
@app.route('/personel_guncelle', methods=['GET', 'POST'])
def personel_guncelle(id=0):
    if id != 0:
        personel = Yonetici.query.filter_by(yonetici_id=id).first()
        return render_template("personel_guncelle.html", yonetici=kullanici['yonetici'], personel=personel)
    elif request.method == 'POST':
        bilgiler = request.form.to_dict()
        bilgiler['yonetici_durum']=int(bilgiler['yonetici_durum'])
        dbsession.query(Yonetici).filter(Yonetici.yonetici_id==bilgiler['yonetici_id']).update(bilgiler)
        dbsession.commit()
        return redirect(url_for('personel_guncelle_sil'))
    else:
        return redirect(url_for('personel_guncelle'))

#personel silme işlemi yapmak için aşağıdaki kod bloğu
@app.route('/personel_sil/<int:sil>')
def personel_sil(sil=0):
    if sil != 0:
        dbsession.query(Yonetici).filter(Yonetici.yonetici_id == sil).delete()
        dbsession.commit()
        return redirect(url_for('personel_guncelle_sil'))
    else:
        return redirect(url_for('personel_guncelle_sil'))

def uzanti_kontrol(dosyaadi):
   return '.' in dosyaadi and \
   dosyaadi.rsplit('.', 1)[1].lower() in UZANTILAR


# Yönetici Firma İşlemleri

# Yönetici Firma ekleme işlemleri
@app.route('/yonetici_firma_ekle', methods=['GET', 'POST'])
@app.route('/yonetici_firma_ekle')
def yonetici_firma_ekle():
    if request.method == 'POST':
        bilgiler = request.form.to_dict()
        resimler=[]
        resimler.append(request.files['dosya01'])
        resimler.append(request.files['dosya02'])
        resimler.append(request.files['dosya03'])
        resimler.append(request.files['dosya04'])
        resimler.append(request.files['dosya05'])
        i = 1
        for dosya in resimler:
            if dosya and uzanti_kontrol(dosya.filename):
                dosyaadi = secure_filename(dosya.filename)
                dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], dosyaadi))
                dosya_yolu = app.config['UPLOAD_FOLDER'] + "/" + dosyaadi
                deger = "isyeri_foto_0"+str(i)
                bilgiler[deger] = dosya_yolu
                i+=1
        if True:
            yonetici = kullanici['yonetici']
            yeni_isyeri = Isyeri(isyeri_adi=bilgiler['isyeri_adi'],
                               isyeri_adresi=bilgiler['isyeri_adresi'],
                               isyeri_telefon=bilgiler['isyeri_telefon'],
                               isyeri_websitesi=bilgiler['isyeri_websitesi'],
                               isyeri_aciklama=bilgiler['isyeri_aciklama'],
                               isyeri_semt_id=int(bilgiler['isyeri_semt_id']),
                               isyeri_foto_01=bilgiler['isyeri_foto_01'],
                               isyeri_foto_02=bilgiler['isyeri_foto_02'],
                               isyeri_foto_03=bilgiler['isyeri_foto_03'],
                               isyeri_foto_04=bilgiler['isyeri_foto_04'],
                               isyeri_foto_05=bilgiler['isyeri_foto_05'],
                               isyeri_durum=0,
                               isyeri_yonetici_id=yonetici.yonetici_id,
                                       )
            dbsession.add(yeni_isyeri)
            dbsession.commit()
            return render_template("yonetici_firma_ekle.html", yonetici=kullanici['yonetici'], mesaj="Başarı")
        else:
            return render_template("yonetici_firma_ekle.html", yonetici=kullanici['yonetici'], mesaj="Başarısızlık")
    else:
        semtler = Semt.query.all()
        return render_template("yonetici_firma_ekle.html", yonetici=kullanici['yonetici'], semtler=semtler)

 # Firma güncelleme ve silme işlemleri

@app.route('/yonetici_firma_guncelle_sil/<int:id>')
@app.route('/yonetici_firma_guncelle_sil')
def yonetici_firma_guncelle_sil(id=0):
    if id == 0:
        isyerleri = Isyeri.query.all()
        return render_template("yonetici_firma_guncelle_sil.html", yonetici=kullanici['yonetici'], isyerleri=isyerleri)
    else:
        dbsession.query(Isyeri).filter(Isyeri.isyeri_id== id).delete()
        dbsession.commit()
        return redirect(url_for('yonetici_firma_guncelle_sil'))
#

@app.route('/yonetici_firma_guncelle/<int:id>')
@app.route('/yonetici_firma_guncelle', methods=['GET', 'POST'])
def yonetici_firma_guncelle(id=0):
    if id != 0:
        semtler = Semt.query.all()
        isyeri = Isyeri.query.filter_by(isyeri_id=id).first()
        return render_template("yonetici_firma_guncelle.html", yonetici=kullanici['yonetici'],
                               semtler=semtler,isyeri=isyeri)
    elif request.method == 'POST':
        bilgiler = request.form.to_dict()
        # isyeri = Isyeri.query.filter(Isyeri.isyeri_id == bilgiler['isyeri_id']).first()
        resimler=[]
        resimler.append(request.files['dosya01'])
        resimler.append(request.files['dosya02'])
        resimler.append(request.files['dosya03'])
        resimler.append(request.files['dosya04'])
        resimler.append(request.files['dosya05'])
        i = 1
        for dosya in resimler:
            deger = "isyeri_foto_0" + str(i)
            if dosya and uzanti_kontrol(dosya.filename):
                dosyaadi = secure_filename(dosya.filename)
                dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], dosyaadi))
                dosya_yolu = app.config['UPLOAD_FOLDER'] + "/" + dosyaadi
                bilgiler[deger] = dosya_yolu
            # else:
            #     eski = "isyeri."+deger
            #     dosya_yolu = eval('{}'.format(eski))
            #     print(dosya_yolu)
            #
            #     bilgiler[deger] = dosya_yolu
            i+=1
        bilgiler['isyeri_yonetici_id']=session['yonetici']
        bilgiler['isyeri_durum'] = int(bilgiler['isyeri_durum'])
        if True:
            dbsession.query(Isyeri).filter(Isyeri.isyeri_id == bilgiler['isyeri_id']).update(bilgiler)
            dbsession.commit()

            return render_template("yonetici_firma_guncelle.html", yonetici=kullanici['yonetici'], mesaj="Başarı")
        else:
            return render_template("yonetici_firma_guncelle.html", yonetici=kullanici['yonetici'], mesaj="Başarısızlık")

    else:
        return redirect(url_for('yonetici_firma_guncelle_sil'))


# Yönetici Duyuru İşlemleri

# duyuru listeleme işlemleri yönetici
@app.route('/yonetici_duyuru_listesi')
def yonetici_duyuru_listesi():
    try:
        uye_id = session['yonetici']
        duyurular = Duyuru.query.all()
        return render_template("yonetici_duyuru_listesi.html", yonetici=kullanici['yonetici'], duyurular=duyurular)
    except:
        return render_template("yonetici_duyuru_listesi.html", yonetici=kullanici['yonetici'])

#duyuru ekleme işlemleri
@app.route('/yonetici_duyuru_ekle', methods=['GET', 'POST'])
@app.route('/yonetici_duyuru_ekle')
def yonetici_duyuru_ekle():
    tarih = datetime.today().utcnow()
    tarih = tarih.strftime("%d/%m/%Y")
    try:
        if request.method == 'POST':
            try:
                bilgiler = request.form.to_dict()
                tarih = datetime.strptime(bilgiler['duyuru_tarihi'], '%d/%m/%Y')
                tarih = datetime.date(tarih)
                yeni_duyuru = Duyuru(duyuru_yonetici_id=session['yonetici'],
                                   duyuru_basligi=bilgiler['duyuru_basligi'],
                                   duyuru_tarihi=tarih,
                                   duyuru_aciklama=bilgiler['duyuru_aciklama'])
                dbsession.add(yeni_duyuru)
                dbsession.commit()
                return render_template("yonetici_duyuru_ekle.html", yonetici=kullanici['yonetici'], mesaj="Başarı")
            except:
                return render_template("yonetici_duyuru_ekle.html", yonetici=kullanici['yonetici'] , mesaj="Başarısızlık")
        else:
            return render_template("yonetici_duyuru_ekle.html", yonetici=kullanici['yonetici'], tarih=tarih)
    except:
        return render_template("yonetici_duyuru_ekle.html", yonetici=kullanici['yonetici'], tarih=tarih)


# duyuru güncelleme ve silme işlemleri
@app.route('/yonetici_duyuru_guncelle_sil/<int:id>')
@app.route('/yonetici_duyuru_guncelle_sil')
def yonetici_duyuru_guncelle_sil(id=0):
    if id == 0:
        duyurular = Duyuru.query.all()

        return render_template("yonetici_duyuru_guncelle_sil.html", yonetici=kullanici['yonetici'], duyurular=duyurular)
    else:
        return redirect(url_for('yonetici_duyuru_listesi'))

#yönetici bölümü duyuru güncelleme
@app.route('/yonetici_duyuru_guncelle/<int:id>')
@app.route('/yonetici_duyuru_guncelle', methods=['GET', 'POST'])
def yonetici_duyuru_guncelle(id=0):
    if id != 0:
        duyurular = Duyuru.query.filter_by(duyuru_id=id).first()
        return render_template("yonetici_duyuru_guncelle.html", yonetici=kullanici['yonetici'], duyurular=duyurular)
    elif request.method == 'POST':
        bilgiler = request.form.to_dict()
        tarih = datetime.strptime(bilgiler['duyuru_tarihi'], '%Y-%m-%d')
        tarih = datetime.date(tarih)
        dbsession.query(Duyuru).filter(Duyuru.duyuru_id == bilgiler['duyuru_id']).update(
            {Duyuru.duyuru_basligi: bilgiler['duyuru_basligi'],
             Duyuru.duyuru_tarihi: tarih, Duyuru.duyuru_aciklama: bilgiler['duyuru_aciklama']})
        dbsession.commit()
        return redirect(url_for('yonetici_duyuru_guncelle_sil'))
    else:
        return redirect(url_for('yonetici_duyuru_guncelle'))

#yönetici bölümü duyuru goruntuleme
@app.route('/yonetici_duyuru_goruntuleme/<int:id>')
@app.route('/yonetici_duyuru_goruntuleme', methods=['GET', 'POST'])
def yonetici_duyuru_goruntuleme(id=0):
    if id != 0:
        duyurular = Duyuru.query.filter_by(duyuru_id=id).first()
        return render_template("yonetici_duyuru_goruntuleme.html", yonetici=kullanici['yonetici'], duyuru=duyurular)
    else:
        return redirect(url_for('yonetici_duyuru_listesi'))


#yönetici paneli duyuru silme bölümü
@app.route('/yonetici_duyuru_sil/<int:sil>')
def yonetici_duyuru_sil(sil=0):
    if sil != 0:
        dbsession.query(Duyuru).filter(Duyuru.duyuru_id == sil).delete()
        dbsession.commit()
        return redirect(url_for('yonetici_duyuru_guncelle_sil'))





# duyuru listeleme işlemleri yönetici
@app.route('/duyuru_listesi')
def duyuru_listesi():
    try:
        duyurular = Duyuru.query.all()
        return render_template("duyuru_listesi.html",duyurular=duyurular)
    except:
        return render_template("duyuru_listesi.html")


# duyuru goruntuleme
@app.route('/duyuru_goruntuleme/<int:id>')
@app.route('/duyuru_goruntuleme', methods=['GET', 'POST'])
def duyuru_goruntuleme(id=0):
    if id != 0:
        duyurular = Duyuru.query.filter_by(duyuru_id=id).first()
        return render_template("duyuru_goruntuleme.html", duyuru=duyurular)
    else:
        return redirect(url_for('duyurular'))

# Firma ekleme işlemleri
@app.route('/firma_ekle', methods=['GET', 'POST'])
@app.route('/firma_ekle')
def firma_ekle():
    if request.method == 'POST':
        bilgiler = request.form.to_dict()
        resimler=[]
        resimler.append(request.files['dosya01'])
        resimler.append(request.files['dosya02'])
        resimler.append(request.files['dosya03'])
        resimler.append(request.files['dosya04'])
        resimler.append(request.files['dosya05'])
        i = 1
        for dosya in resimler:
            if dosya and uzanti_kontrol(dosya.filename):
                dosyaadi = secure_filename(dosya.filename)
                dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], dosyaadi))
                dosya_yolu = app.config['UPLOAD_FOLDER'] + "/" + dosyaadi
                deger = "isyeri_foto_0"+str(i)
                bilgiler[deger] = dosya_yolu
                i+=1
        if True:
            yeni_isyeri = Isyeri(isyeri_adi=bilgiler['isyeri_adi'],
                               isyeri_adresi=bilgiler['isyeri_adresi'],
                               isyeri_telefon=bilgiler['isyeri_telefon'],
                               isyeri_websitesi=bilgiler['isyeri_websitesi'],
                               isyeri_aciklama=bilgiler['isyeri_aciklama'],
                               isyeri_semt_id=int(bilgiler['isyeri_semt_id']),
                               isyeri_foto_01=bilgiler['isyeri_foto_01'],
                               isyeri_foto_02=bilgiler['isyeri_foto_02'],
                               isyeri_foto_03=bilgiler['isyeri_foto_03'],
                               isyeri_foto_04=bilgiler['isyeri_foto_04'],
                               isyeri_foto_05=bilgiler['isyeri_foto_05'],
                               isyeri_durum=2,
                               isyeri_yonetici_id=0,
                                       )
            dbsession.add(yeni_isyeri)
            dbsession.commit()
            return render_template("firma_ekle.html", mesaj="Başarı ile Talebiniz İletilmiştir")
        else:
            return render_template("firma_ekle.html", mesaj="Başarısızlık Oluştu !!!")
    else:
        semtler = Semt.query.all()
        return render_template("firma_ekle.html", semtler=semtler)

# firma goruntuleme
@app.route('/firma_goruntuleme/<int:id>')
@app.route('/firma_goruntuleme/<int:id>', methods=['GET', 'POST'])
def firma_goruntuleme(id=0):
    try:
        if request.method == 'POST':
            if True:
                bilgiler = request.form.to_dict()
                yeni_yorum = Yorum(yorum_yapan_adi=bilgiler['yorum_yapan_adi'],yorum_aciklama=bilgiler['yorum_aciklama'],
                                   yorum_yapan_eposta=bilgiler['yorum_yapan_eposta'],yorum_isyeri_id=id)
                dbsession.add(yeni_yorum)
                dbsession.commit()
                return render_template("firma_goruntuleme.html", mesaj="Başarı")
            else:
                return render_template("firma_goruntuleme.html", mesaj="Başarısızlık")

        elif id != 0:
            dbsession.query(Isyeri).filter(Isyeri.isyeri_id == id).update(
                {Isyeri.isyeri_goruntulenme_sayisi: Isyeri.isyeri_goruntulenme_sayisi + 1,
                 })
            dbsession.commit()

            isyeri = Isyeri.query.filter_by(isyeri_id=id).first()
            yorumlar = Yorum.query.all()
            return render_template("firma_goruntuleme.html", isyeri=isyeri,yorumlar=yorumlar)
        else:
            return redirect(url_for('index'))
    except:
        return redirect(url_for('index'))

# firma goruntuleme
@app.route('/yonetici_firma_goruntuleme/<int:id>')
@app.route('/yonetici_firma_goruntuleme/<int:id>', methods=['GET', 'POST'])
def yonetici_firma_goruntuleme(id=0):
    try:
        if id != 0:
            isyeri = Isyeri.query.filter_by(isyeri_id=id).first()
            yorumlar = Yorum.query.all()
            return render_template("yonetici_firma_goruntuleme.html", isyeri=isyeri,yorumlar=yorumlar)
        else:
            return redirect(url_for('index'))
    except:
        return redirect(url_for('index'))

# duyuru güncelleme ve silme işlemleri
@app.route('/yonetici_yorum_guncelle_sil/<int:id>')
@app.route('/yonetici_yorum_guncelle_sil')
def yonetici_yorum_guncelle_sil(id=0):
    if id == 0:
        yorumlar = Yorum.query.all()

        return render_template("yonetici_yorum_guncelle_sil.html", yonetici=kullanici['yonetici'], yorumlar=yorumlar)
    else:
        return redirect(url_for('yonetici_yorum_listesi'))

#yönetici bölümü duyuru güncelleme
@app.route('/yonetici_yorum_guncelle/<int:id>')
@app.route('/yonetici_yorum_guncelle', methods=['GET', 'POST'])
def yonetici_yorum_guncelle(id=0):
    if id != 0:
        yorumlar = Yorum.query.filter_by(yorum_id=id).first()
        return render_template("yonetici_yorum_guncelle.html", yonetici=kullanici['yonetici'], yorum=yorumlar)
    elif request.method == 'POST':
        bilgiler = request.form.to_dict()
        dbsession.query(Yorum).filter(Yorum.yorum_id == bilgiler['yorum_id']).update(bilgiler)
        dbsession.commit()
        return redirect(url_for('yonetici_yorum_guncelle_sil'))
    else:
        return redirect(url_for('yonetici_yorum_guncelle'))

#yönetici bölümü yorum goruntuleme
@app.route('/yonetici_yorum_goruntuleme/<int:id>')
@app.route('/yonetici_yorum_goruntuleme', methods=['GET', 'POST'])
def yonetici_yorum_goruntuleme(id=0):
    if id != 0:
        yorumlar = Yorum.query.filter_by(yorum_id=id).first()
        return render_template("yonetici_yorum_goruntuleme.html", yonetici=kullanici['yonetici'], yorum=yorumlar)
    else:
        return redirect(url_for('yonetici_yorum_listesi'))


#yönetici paneli duyuru silme bölümü
@app.route('/yonetici_yorum_sil/<int:sil>')
def yonetici_yorum_sil(sil=0):
    if sil != 0:
        dbsession.query(Yorum).filter(Yorum.yorum_id == sil).delete()
        dbsession.commit()
        return redirect(url_for('yonetici_yorum_guncelle_sil'))

if __name__ == '__main__':
    app.run(debug=True)
