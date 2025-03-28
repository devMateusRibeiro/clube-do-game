# app.py
from flask import Flask, render_template, request, jsonify
import requests
import random
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv('RAWG_API_KEY')
BASE_URL = 'https://api.rawg.io/api/games'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/descobrir')
def descobrir():
    return render_template('descobrir.html')

@app.route('/buscar', methods=['POST'])
def buscar_jogo():
    platform = request.form.get('platform', '')
    year_from = request.form.get('year_from', '')
    year_to = request.form.get('year_to', '')
    genre = request.form.get('genre', '')
    rating = request.form.get('rating', '')

    params = {
        'key': API_KEY,
        'page_size': 20,
    }

    if platform:
        params['platforms'] = platform
    if genre:
        params['genres'] = genre
    if year_from or year_to:
        from_year = year_from if year_from else '1900'
        to_year = year_to if year_to else '2025'
        params['dates'] = f"{from_year}-01-01,{to_year}-12-31"
    if rating:
        params['metacritic'] = f"{rating},100"

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if not data.get('results'):
        return jsonify({'erro': 'Nenhum jogo encontrado.'})

    jogo = random.choice(data['results'])
    slug = jogo.get('slug')
    jogo_id = jogo.get('id')

    screenshots = []
    desenvolvedora = 'Desconhecida'

    if jogo_id:
        detalhes_url = f"{BASE_URL}/{jogo_id}?key={API_KEY}"
        detalhes_resp = requests.get(detalhes_url).json()
        if detalhes_resp.get('developers'):
            desenvolvedora = detalhes_resp['developers'][0]['name']

        screenshots_url = f"{BASE_URL}/{jogo_id}/screenshots?key={API_KEY}"
        screenshots_resp = requests.get(screenshots_url).json()
        screenshots = [img['image'] for img in screenshots_resp.get('results', [])[:4]]

    return jsonify({
        'nome': jogo['name'],
        'imagem': jogo.get('background_image'),
        'nota': jogo.get('metacritic') if jogo.get('metacritic') is not None else 'SEM NOTA',
        'data': jogo['released'],
        'generos': [g['name'] for g in jogo['genres']],
        'plataformas': [p['platform']['name'] for p in jogo['platforms']],
        'slug': slug or '',
        'screenshots': screenshots,
        'desenvolvedora': desenvolvedora
    })

@app.route('/plataformas')
def plataformas():
    url = f"https://api.rawg.io/api/platforms?key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    plataformas = [{'id': p['id'], 'name': p['name']} for p in data.get('results', [])]
    return jsonify(plataformas)

@app.route('/generos')
def generos():
    url = f"https://api.rawg.io/api/genres?key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    generos = [{'slug': g['slug'], 'name': g['name']} for g in data.get('results', [])]
    return jsonify(generos)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)