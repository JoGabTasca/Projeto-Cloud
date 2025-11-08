# WSGI entrypoint for Azure Web App
# Este arquivo deve estar na pasta backend junto com api.py

from api import app

if __name__ == "__main__":
    # Local debug fallback
    app.run(host="0.0.0.0", port=5000, debug=True)
