from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat_bot():
    return render_template('chat_bot.html')

@app.route('/api/hello')
def hello_api():
    return {'message': 'Hello from Flask API!', 'status': 'success'}

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
