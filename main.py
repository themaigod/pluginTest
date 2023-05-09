import json

import quart
import quart_cors
from quart import request
from reader.pdf_processing import get_all_pdf

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Keep track of paper's. Does not persist if Python session is restarted.
_PAPERS = {}

_PAPERS_CONTENT = {}


@app.post("/papers/<string:username>")
async def add_paper(username):
    request = await quart.request.get_json(force=True)
    if username not in _PAPERS:
        _PAPERS[username] = []
    _PAPERS[username].append(request["paper"])
    return quart.Response(response='OK', status=200)


@app.get("/papers/<string:username>")
async def get_papers(username):
    return quart.Response(response=json.dumps(_PAPERS.get(username, [])), status=200)


@app.delete("/papers/<string:username>")
async def delete_paper(username):
    request = await quart.request.get_json(force=True)
    paper_idx = request["paper_idx"]
    # fail silently, it's a simple plugin
    if 0 <= paper_idx < len(_PAPERS[username]):
        _PAPERS[username].pop(paper_idx)
    return quart.Response(response='OK', status=200)


_idx_input = {}


@app.get("/papersRead/<string:username>")
async def get_papers_read(username):
    if username not in _PAPERS_CONTENT:
        _PAPERS_CONTENT[username] = []
    if username not in _PAPERS:
        _PAPERS[username] = []
    _PAPERS_CONTENT[username].append(_PAPERS_CONTENT['username'][_idx_input.get(username, 0)])
    _PAPERS[username].append(_PAPERS['username'][_idx_input.get(username, 0)])
    _idx_input[username] = (_idx_input.get(username, 0) + 1) % len(_PAPERS['username'])
    return quart.Response(
        response=[json.dumps(_PAPERS.get(username, [])), json.dumps(_PAPERS_CONTENT.get(username, []))], status=200)


@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")


def main():
    _PAPERS["username"], _PAPERS_CONTENT["username"] = get_all_pdf("./pdf")
    print(len(_PAPERS["username"]), len(_PAPERS_CONTENT["username"]))
    app.run(debug=True, host="0.0.0.0", port=5004)


if __name__ == "__main__":
    main()
