from flask import Flask, request, Response
import requests

app = Flask(__name__)

BINANCE_BASE = "https://api.binance.com"

@app.route("/")
def health():
    return "OK"

# Forward anything under /binance/... to https://api.binance.com/...
@app.route("/binance/<path:subpath>", methods=["GET", "OPTIONS"])
def binance_proxy(subpath):
    # CORS preflight
    if request.method == "OPTIONS":
        return _cors(Response(status=204))

    # Build upstream URL
    upstream = f"{BINANCE_BASE}/{subpath}"
    qs = request.query_string.decode("utf-8")
    if qs:
        upstream = f"{upstream}?{qs}"

    # Forward GET request
    try:
        resp = requests.get(
            upstream,
            headers={
                "User-Agent": "Mozilla/5.0",   # helps avoid 403
                "Accept": "application/json"
            },
            timeout=15,
        )
    except requests.RequestException as e:
        return _cors(Response(f'{{"error":"upstream failed","detail":"{str(e)}"}}', status=502, mimetype="application/json"))

    # Pass through body and status; keep JSON content-type
    out = Response(resp.content, status=resp.status_code, mimetype=resp.headers.get("Content-Type", "application/json"))
    return _cors(out)

def _cors(r: Response):
    r.headers["Access-Control-Allow-Origin"] = "*"
    r.headers["Access-Control-Allow-Methods"] = "GET,OPTIONS"
    r.headers["Access-Control-Allow-Headers"] = "*"
    return r

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
