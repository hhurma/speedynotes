#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Syntax Highlighting Test Dosyası
Bu dosya Python syntax highlighting özelliğini test eder
"""

import os
import sys
import asyncio
from datetime import datetime

# Sınıf tanımı
class TestSinifi:
    """Test sınıfı"""
    
    def __init__(self, isim):
        self.isim = isim
        self.sayi = 42
        self.pi = 3.14159
        self.hex_sayi = 0xFF
        self.binary_sayi = 0b1010
    
    @property
    def bilgi(self):
        return f"İsim: {self.isim}, Sayı: {self.sayi}"
    
    @staticmethod
    def statik_metod():
        """Statik metod örneği"""
        return "Bu bir statik metod"

# Fonksiyon tanımları
def merhaba(ad="Dünya"):
    """Merhaba fonksiyonu"""
    print(f"Merhaba {ad}!")
    return True

async def asenkron_fonksiyon():
    """Asenkron fonksiyon örneği"""
    await asyncio.sleep(1)
    return "Asenkron işlem tamamlandı"

def hesapla(a, b):
    """Matematiksel işlemler"""
    toplam = a + b
    fark = a - b
    carpim = a * b
    bolum = a / b if b != 0 else None
    return {'toplam': toplam, 'fark': fark, 'carpim': carpim, 'bolum': bolum}

# Değişkenler ve veri tipleri
metin = "Bu bir string"
tek_tirnak = 'Tek tırnak string'
cok_satirli = """
Bu çok satırlı
bir string örneği
"""

liste = [1, 2, 3, "dört", True, None]
sozluk = {"anahtar": "değer", "sayı": 123}
demet = (1, 2, 3)
kume = {1, 2, 3, 4, 5}

# Kontrol yapıları
if __name__ == "__main__":
    print("Bu dosya direkt çalıştırılıyor")
    
    # For döngüsü
    for i in range(5):
        if i == 2:
            continue
        elif i == 4:
            break
        print(f"Döngü: {i}")
    
    # While döngüsü
    sayac = 0
    while sayac < 3:
        print(f"Sayaç: {sayac}")
        sayac += 1
    
    # Try-except
    try:
        sonuc = 10 / 0
    except ZeroDivisionError as e:
        print(f"Hata: {e}")
    finally:
        print("İşlem tamamlandı")
    
    # List comprehension
    kareler = [x**2 for x in range(10) if x % 2 == 0]
    print(f"Çift sayıların kareleri: {kareler}")
    
    # Lambda fonksiyon
    kare_al = lambda x: x**2
    print(f"5'in karesi: {kare_al(5)}")
    
    # Test sınıfını kullan
    test_obj = TestSinifi("Python")
    print(test_obj.bilgi)
    print(TestSinifi.statik_metod())
    
    # Built-in fonksiyonlar
    print(f"Listenin uzunluğu: {len(liste)}")
    print(f"Maksimum: {max([1, 5, 3, 9, 2])}")
    print(f"Minimum: {min([1, 5, 3, 9, 2])}")
    
    # Global ve nonlocal
    global_degisken = "Global"
    
    def dis_fonksiyon():
        yerel = "Yerel"
        
        def ic_fonksiyon():
            nonlocal yerel
            yerel = "Değiştirildi"
        
        ic_fonksiyon()
        return yerel
    
    print(f"Değişken: {dis_fonksiyon()}")
    
    # Operatörler
    print(f"Mantıksal: {True and False or not True}")
    print(f"Kimlik: {'a' is not 'b'}")
    print(f"Üyelik: {'a' in 'abc'}")
    
    # Çeşitli yorumlar
    # Bu tek satırlık yorum
    # Bu da başka bir yorum
    
    merhaba("Syntax Highlighting")
    print("Test tamamlandı!")
