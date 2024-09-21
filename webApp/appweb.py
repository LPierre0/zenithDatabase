from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

def get_data(lvl_min, lvl_max, item_type, rarity, number_results=10):
    print(os.getcwd())
    print(os.path.exists('db/zenithDatabase.sqlite'))
    conn = sqlite3.connect('db/zenithDatabase.sqlite')  # Update with your database path
    c = conn.cursor()
    text_rarity = f"AND item.rarity = '{rarity}'" if rarity != 'None' else ''
    
    request = f'''
        SELECT item.name, item.rarity, item.img, COUNT(*) AS count
        FROM build
        JOIN item ON item.url = build.{item_type}_url
        WHERE item.lvl >= {lvl_min} AND item.lvl <= {lvl_max} {text_rarity}
        GROUP BY item.name, item.rarity
        ORDER BY count DESC
        LIMIT {number_results};
    '''
    print(request)
    c.execute(request)
    data = c.fetchall()
    print(data)
    conn.close()
    return data

@app.route('/get_items', methods=['GET'])
def get_items():
    lvl_min = request.args.get('lvl_min', type=int)
    lvl_max = request.args.get('lvl_max', type=int)
    item_type = request.args.get('item_type')
    rarity = request.args.get('rarity')
    number_results = request.args.get('number_results', default=10, type=int)

    print(f"DEBUG: lvl_min={lvl_min}, lvl_max={lvl_max}, item_type={item_type}, rarity={rarity}, number_results={number_results}")
    data = get_data(lvl_min, lvl_max, item_type, rarity, number_results)
    print(data)
    # Convert data to a list of dictionaries for better structure
    items = [{'name': name, 'rarity': rarity, 'img': img, 'count': count} for name, rarity, img, count in data]
    
    return items


if __name__ == '__main__':
    app.run(debug=True)
