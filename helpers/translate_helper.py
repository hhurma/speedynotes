import os

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'


def gemini_translate(text, target_lang='tr'):
    """
    Google Gemini API ile metni belirtilen dile çevirir.
    """
    try:
        import requests  # Lazy import, paket eksikse uygulama çökmesin
    except Exception:
        return "Çeviri özelliği için 'requests' paketi gerekli (pakette yer almıyor)."
    if not GEMINI_API_KEY:
        raise RuntimeError('GEMINI_API_KEY ortam değişkeni tanımlı değil.')
    headers = {"Content-Type": "application/json"}
    prompt = f'Çevir: {text}\nHedef dil: {target_lang}'
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    params = {"key": GEMINI_API_KEY}
    response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data, timeout=20)
    response.raise_for_status()
    result = response.json()
    try:
        raw = result['candidates'][0]['content']['parts'][0]['text']
        # Başında veya sonunda açıklama varsa temizle
        temiz = raw.strip()
        for prefix in [
            'Here is the translation:',
            'İşte çeviri:',
            'Translation:',
            'Çeviri:',
            'Elbette,',
            'Tabii ki,',
            'Sure,',
            'Of course,',
        ]:
            if temiz.lower().startswith(prefix.lower()):
                temiz = temiz[len(prefix):].lstrip(': .\n')
        return temiz.strip()
    except Exception:
        return "Çeviri başarısız."

def is_text_turkish(text):
    """
    Metnin Türkçe olup olmadığını basitçe kontrol eder.
    """
    turkce_karakterler = set("çğıöşüÇĞİÖŞÜ")
    if any(c in turkce_karakterler for c in text):
        return True
    # Türkçe'ye özgü bazı kelimelerle de kontrol edelim
    turkce_kelimeler = ["ve", "bir", "bu", "ile", "ama", "gibi", "için", "çok", "daha", "değil"]
    kelime_kucuk = text.lower()
    if any(k in kelime_kucuk for k in turkce_kelimeler):
        return True
    return False 