import os
from flask import Flask
from flask_cors import CORS
from flask_sslify import SSLify
from marketinsights.server.portfoliomgr import api

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024  # 64 MB
api.init_app(app)
# SSLify(app)
# CORS(app)

# When running this app on the local machine, default to 8080
port = int(os.getenv('PORT', 8080))

# run
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)  # deploy with debug=False
