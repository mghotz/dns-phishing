from flask import Flask, jsonify, request
import json
from permutation import main
import asyncio
app = Flask(__name__)

@app.route('/scan', methods=['POST'])
def scan_url():
    data = request.get_json()

    if not data or 'url' not in data:
        return jsonify({'error': 'No url provided'}), 400

    url = data['url']
    similarity = data.get('similarity', 'style')
    similaritycheck = data.get('similaritycheck', False)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def async_wrapper():
        return await main(url, similarity, similaritycheck)

    result = loop.run_until_complete(async_wrapper())
    loop.close()

    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)