from flask import Flask, request, jsonify, render_template
from gameAnalysis import *

gameAnalyzer = Main()
gameAnalyzer.updateInvalidEntries()
app = Flask(__name__)


def saveProcess():
    data = request.json['entries']
    for d in data:
        if d['text'] != '':
            savedData[d['section']].update({d['key']: d['text']})
    gameAnalyzer.export()


@app.route('/get_dropdowns')
def get_dropdowns():
    return jsonify({
        "prompts": list(savedData["Prompts"].keys()),
        "files": list(savedData["Files Descriptions"].keys()),
        "games": list(savedData["Game Descriptions"].keys())
    })


@app.route('/get_text', methods=['POST'])
def get_text():
    data = request.json
    section = data['section']
    key = data['key']
    return jsonify({"text": savedData[section][key] if key != '' else ''})


@app.route('/save_all', methods=['POST'])
def save():
    saveProcess()
    return ''


@app.route('/can_query')
def can_query():
    can_query = not any(e == {'': ''} for e in gameAnalyzer.selectedData.values())
    return jsonify({"can_query": can_query})


@app.route('/query_ai', methods=['POST'])
def query_ai():
    # saveProcess()
    gameAnalyzer.saveResponse()
    return jsonify({"result": "AI Queried; saved response"})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/delete_entry', methods=['POST'])
def delete_entry():
    data = request.json
    section = data['section']
    key = data['key']
    if key in savedData[section]:
        savedData[section].pop(key)
        gameAnalyzer.export()
        return ''
    return jsonify({"result": f'Entry "{key}" not found in {section}.'})


@app.route('/get_status', methods=['POST'])
def get_status():
    data = request.json
    section = data['section']
    key = data['key']
    gameAnalyzer.selectedData[section] = {key: '' if not key else savedData[section][key]}
    entryContents = list(gameAnalyzer.selectedData[section].values())[0]
    errorInfo = ""
    if section == "Prompts":
        for p in promptReplacements.values():
            if p not in entryContents:
                errorInfo += f"{p}, "
    if errorInfo:
        errorInfo = errorInfo[:-2]
        errorInfo = f"MISSING: {errorInfo}"
    if not entryContents:
        errorInfo = f"EMPTY CONTENTS! {errorInfo}"
    return jsonify({"status": errorInfo})


@app.route('/get_latest_response')
def get_latest_response():
    folders = [f for f in os.listdir('templates/responses') if f.startswith('response--')]
    if not folders:
        return jsonify({"folder": ""})
    latest = sorted(folders)[-1]
    return jsonify({"folder": latest})


if __name__ == '__main__':
    app.run(debug=True)
