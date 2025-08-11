from flask import Flask, request, Response
import requests, os

app = Flask(__name__)
BINANCE_BASE = "https://api.binance.com"

@app.get("/")
def health():
    return "OK"

# Proxy anything under /binance/... → https://api.binance.com/...
@app.route("/binance/<path:subpath>", methods=["GET", "OPTIONS"])
def binance_proxy(subpath):
    # CORS preflight
    if request.method == "OPTIONS":
        return _cors(Response(status=204))

    upstream = f"{BINANCE_BASE}/{subpath}"
    if request.query_string:
        upstream += "?" + request.query_string.decode("utf-8")

    try:
        r = requests.get(
            upstream,
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
            timeout=15,
        )
        out = Response(r.content, status=r.status_code,
                       mimetype=r.headers.get("Content-Type", "application/json"))
        return _cors(out)
    except requests.RequestException as e:
        return _cors(Response(f'{{"error":"upstream failed","detail":"{e}"}}',
                              status=502, mimetype="application/json"))

def _cors(resp: Response):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    return resp

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # DO App Platform sets $PORT
    app.run(host="0.0.0.0", port=port)
