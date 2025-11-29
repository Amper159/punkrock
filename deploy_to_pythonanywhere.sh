#!/bin/bash
# 🚀 Automatické nahrání webu na PythonAnywhere

# Lokální cesta k tvému projektu
LOCAL_PATH="/home/ampercz/Punkrockradio/punkrock-1"

# Cílová cesta na PythonAnywhere
REMOTE_USER="Punk77"
REMOTE_HOST="ssh.pythonanywhere.com"
REMOTE_PATH="/home/$REMOTE_USER/punkrock-1/punkrock-1"

# 📦 Nahraje všechny změny (kromě venv a __pycache__)
echo "📤 Nahrávám změny na PythonAnywhere..."
rsync -avz --exclude 'venv' --exclude '__pycache__' $LOCAL_PATH/ $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/

# 🔁 Restartuje webovou aplikaci
echo "🔁 Restart webu..."
ssh $REMOTE_USER@$REMOTE_HOST "touch /var/www/${REMOTE_USER}_pythonanywhere_com_wsgi.py"

echo "✅ Hotovo! Web byl úspěšně nasazen."
