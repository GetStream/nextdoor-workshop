#!/bin/bash

FLASK_APP_DIR="."
DESTINATION_IP="10.23.139.205"

if [ ! -d "$FLASK_APP_DIR" ]; then
    echo "Error: Flask app directory '$FLASK_APP_DIR' not found."
    exit 1
fi

TEMP_DIR="$(mktemp -d)"

ZIP_FILE="$TEMP_DIR/flaskapp.zip"
zip -r "$ZIP_FILE" . -x "venv/*" -x ".idea/*" -x ".git/*"  -x "bin/*" -x "lib/*" -x "__pycache__/*"

scp "$ZIP_FILE" "$DESTINATION_IP:/tmp/"

ssh "$DESTINATION_IP" << EOF
    sudo mkdir -p /srv/flaskapp
    sudo chown -R `whoami`: /srv/flaskapp
    unzip -o "/tmp/flaskapp.zip" -d "/srv/flaskapp/"
    rm "/tmp/flaskapp.zip"

    cd /srv/flaskapp
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate

    pip install -r requirements.txt

    deactivate

    sudo supervisorctl restart flaskapp
EOF

rm -rf "$TEMP_DIR"

echo "Deployment completed!"
