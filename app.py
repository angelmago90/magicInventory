from flask import Flask, render_template, request, redirect, url_for
import requests
import sqlite3

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cartas = buscar_carta(nombre)
        if cartas:
            return render_template('buscar_carta.html', cartas=cartas)
        else:
            mensaje = "No se encontraron cartas."
            return render_template('buscar_carta.html', mensaje=mensaje)
    return render_template('buscar_carta.html')

@app.route('/mi-coleccion', methods=['GET', 'POST'])
def mi_coleccion():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cartas = buscar_carta_en_coleccion(nombre)
    else:
        cartas = obtener_cartas_guardadas()
    return render_template('mi_coleccion.html', cartas=cartas)

@app.route('/guardar', methods=['POST'])
def guardar():
    ids_de_cartas = request.form.getlist('carta_id[]')
    
    conn = sqlite3.connect('mtg_cards.db')
    cursor = conn.cursor()

    for carta_id in ids_de_cartas:
        cantidad = int(request.form.get(f'cantidad_{carta_id}', 1))
        name = request.form.get(f'name_{carta_id}', 'Unknown')
        set_name = request.form.get(f'set_name_{carta_id}', 'Unknown')
        rarity = request.form.get(f'rarity_{carta_id}', 'Unknown')
        colors = request.form.get(f'colors_{carta_id}', '')

        # Intenta insertar o actualizar la carta en la base de datos
        cursor.execute("""
            INSERT INTO cards (name, rarity, set_name, colors, quantity) 
            VALUES (?, ?, ?, ?, ?) 
            ON CONFLICT(id) DO UPDATE SET 
                name=excluded.name, 
                rarity=excluded.rarity, 
                set_name=excluded.set_name, 
                colors=excluded.colors, 
                quantity=quantity + excluded.quantity;
            """, (name, rarity, set_name, colors, cantidad))

    conn.commit()
    conn.close()
    return redirect(url_for('mi_coleccion'))

def buscar_carta(nombre):
    url = "https://api.scryfall.com/cards/search"
    query = {"q": f"name:'{nombre}'"}
    response = requests.get(url, params=query)
    
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Error: {response.status_code}")
        return []

def obtener_cartas_guardadas():
    conn = sqlite3.connect('mtg_cards.db') 
    c = conn.cursor()
    c.execute('SELECT * FROM cards')
    cartas = c.fetchall()
    conn.close()
    return cartas

def buscar_carta_en_coleccion(nombre):
    conn = sqlite3.connect('mtg_cards.db')
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE name LIKE ?", ('%' + nombre + '%',))
    cartas = c.fetchall()
    conn.close()
    return cartas

if __name__ == '__main__':
    app.run(debug=True)
