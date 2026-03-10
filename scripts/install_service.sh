#!/bin/bash

# Script d'installation du service smart-downloads-organizer
# Doit être exécuté avec les privilèges root

set -e

# Variables de configuration
SERVICE_NAME="smart-downloads-organizer"
INSTALL_DIR="/opt/$SERVICE_NAME"
SERVICE_USER="smartdo"
SERVICE_GROUP="smartdo"
VENV_DIR="$INSTALL_DIR/venv"
CONFIG_DIR="/etc/$SERVICE_NAME"
LOG_DIR="/var/log/$SERVICE_NAME"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages d'erreur et quitter
error_exit() {
    echo -e "${RED}Erreur: $1${NC}" >&2
    exit 1
}

# Fonction pour afficher les messages d'information
info_msg() {
    echo -e "${GREEN}Info: $1${NC}"
}

# Fonction pour afficher les messages d'avertissement
warning_msg() {
    echo -e "${YELLOW}Avertissement: $1${NC}"
}

# Vérifier que le script est exécuté en root
if [[ $EUID -ne 0 ]]; then
   error_exit "Ce script doit être exécuté en tant que root (utilisez sudo)"
fi

# Vérifier si systemd est disponible
if ! command -v systemctl &> /dev/null; then
    error_exit "systemd n'est pas installé sur ce système"
fi

# Arrêter le service s'il est déjà en cours d'exécution
if systemctl is-active --quiet $SERVICE_NAME; then
    info_msg "Arrêt du service $SERVICE_NAME..."
    systemctl stop $SERVICE_NAME
fi

# Désactiver le service s'il existe
if systemctl is-enabled --quiet $SERVICE_NAME 2>/dev/null; then
    info_msg "Désactivation du service $SERVICE_NAME..."
    systemctl disable $SERVICE_NAME
fi

# Créer l'utilisateur et le groupe du service s'ils n'existent pas
if ! getent group $SERVICE_GROUP > /dev/null; then
    info_msg "Création du groupe $SERVICE_GROUP..."
    groupadd --system $SERVICE_GROUP
fi

if ! id -u $SERVICE_USER > /dev/null 2>&1; then
    info_msg "Création de l'utilisateur $SERVICE_USER..."
    useradd --system --no-create-home --shell /bin/false -g $SERVICE_GROUP $SERVICE_USER
fi

# Créer les répertoires nécessaires
info_msg "Création des répertoires..."
mkdir -p $INSTALL_DIR
mkdir -p $CONFIG_DIR
mkdir -p $LOG_DIR
mkdir -p $INSTALL_DIR/database
mkdir -p $INSTALL_DIR/logs
mkdir -p $INSTALL_DIR/config
mkdir -p $INSTALL_DIR/utils
mkdir -p $INSTALL_DIR/models
mkdir -p $INSTALL_DIR/static/css
mkdir -p $INSTALL_DIR/templates
mkdir -p $INSTALL_DIR/scripts
mkdir -p $INSTALL_DIR/docs

# Copier les fichiers du projet
info_msg "Copie des fichiers du projet..."
cp -f organizer.py $INSTALL_DIR/
cp -f config.json $INSTALL_DIR/
cp -f web_interface.py $INSTALL_DIR/
cp -f run.py $INSTALL_DIR/
cp -f setup.py $INSTALL_DIR/
cp -f requirements.txt $INSTALL_DIR/
cp -f README.md $INSTALL_DIR/
cp -f .gitignore $INSTALL_DIR/
cp -f test_classifier.py $INSTALL_DIR/
cp -f test_file_handler.py $INSTALL_DIR/
cp -f test_web_interface.py $INSTALL_DIR/
cp -f test_integration.py $INSTALL_DIR/

# Copier les répertoires
cp -rf utils/* $INSTALL_DIR/utils/ 2>/dev/null || true
cp -rf models/* $INSTALL_DIR/models/ 2>/dev/null || true
cp -rf templates/* $INSTALL_DIR/templates/ 2>/dev/null || true
cp -rf static/* $INSTALL_DIR/static/ 2>/dev/null || true
cp -rf scripts/* $INSTALL_DIR/scripts/ 2>/dev/null || true
cp -rf docs/* $INSTALL_DIR/docs/ 2>/dev/null || true
cp -rf config/* $INSTALL_DIR/config/ 2>/dev/null || true

# Copier la base de données si elle existe
if [ -f "database/schema.sql" ]; then
    cp -f database/schema.sql $INSTALL_DIR/database/
fi
if [ -f "database/db_manager.py" ]; then
    cp -f database/db_manager.py $INSTALL_DIR/database/
fi

# Créer un environnement virtuel Python
info_msg "Création de l'environnement virtuel Python..."
if [ -d "$VENV_DIR" ]; then
    warning_msg "L'environnement virtuel existe déjà, suppression..."
    rm -rf $VENV_DIR
fi
python3 -m venv $VENV_DIR

# Activer l'environnement virtuel et installer les dépendances
info_msg "Installation des dépendances Python..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r $INSTALL_DIR/requirements.txt
deactivate

# Copier la configuration par défaut si elle n'existe pas
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    info_msg "Copie de la configuration par défaut..."
    cp $INSTALL_DIR/config.json $CONFIG_DIR/
fi

# Créer le fichier de service systemd
info_msg "Création du fichier de service systemd..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Smart Downloads Organizer Daemon
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=5
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$INSTALL_DIR
Environment="PYTHONPATH=$INSTALL_DIR"
Environment="CONFIG_PATH=$CONFIG_DIR/config.json"
ExecStart=$VENV_DIR/bin/python $INSTALL_DIR/organizer.py
StandardOutput=append:$LOG_DIR/service.log
StandardError=append:$LOG_DIR/error.log

[Install]
WantedBy=multi-user.target
EOF

# Créer le fichier de service web interface
info_msg "Création du fichier de service web interface..."
cat > /etc/systemd/system/$SERVICE_NAME-web.service << EOF
[Unit]
Description=Smart Downloads Organizer Web Interface
After=network.target
Wants=$SERVICE_NAME.service
After=$SERVICE_NAME.service

[Service]
Type=simple
Restart=always
RestartSec=5
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$INSTALL_DIR
Environment="PYTHONPATH=$INSTALL_DIR"
Environment="CONFIG_PATH=$CONFIG_DIR/config.json"
ExecStart=$VENV_DIR/bin/python $INSTALL_DIR/web_interface.py
StandardOutput=append:$LOG_DIR/web_service.log
StandardError=append:$LOG_DIR/web_error.log

[Install]
WantedBy=multi-user.target
EOF

# Définir les permissions
info_msg "Configuration des permissions..."
chown -R $SERVICE_USER:$SERVICE_GROUP $INSTALL_DIR
chown -R $SERVICE_USER:$SERVICE_GROUP $CONFIG_DIR
chown -R $SERVICE_USER:$SERVICE_GROUP $LOG_DIR
chmod 755 $INSTALL_DIR
chmod 755 $LOG_DIR
chmod 644 $CONFIG_DIR/config.json
chmod 755 $INSTALL_DIR/organizer.py
chmod 755 $INSTALL_DIR/web_interface.py
chmod 755 $INSTALL_DIR/run.py

# Recharger systemd
info_msg "Rechargement de systemd..."
systemctl daemon-reload

# Activer et démarrer les services
info_msg "Activation des services..."
systemctl enable $SERVICE_NAME
systemctl enable $SERVICE_NAME-web

info_msg "Démarrage des services..."
systemctl start $SERVICE_NAME
systemctl start $SERVICE_NAME-web

# Vérifier l'état des services
sleep 2
if systemctl is-active --quiet $SERVICE_NAME; then
    info_msg "Service principal $SERVICE_NAME démarré avec succès"
else
    warning_msg "Le service principal $SERVICE_NAME n'a pas démarré correctement"
    systemctl status $SERVICE_NAME --no-pager
fi

if systemctl is-active --quiet $SERVICE_NAME-web; then
    info_msg "Service web $SERVICE_NAME-web démarré avec succès"
else
    warning_msg "Le service web $SERVICE_NAME-web n'a pas démarré correctement"
    systemctl status $SERVICE_NAME-web --no-pager
fi

# Afficher les informations de configuration
echo ""
info_msg "Installation terminée avec succès !"
echo ""
echo "Informations d'installation:"
echo "  Répertoire d'installation: $INSTALL_DIR"
echo "  Configuration: $CONFIG_DIR/config.json"
echo "  Journaux: $LOG_DIR/"
echo "  Utilisateur du service: $SERVICE_USER"
echo ""
echo "Commandes utiles:"
echo "  Voir le statut du service: sudo systemctl status $SERVICE_NAME"
echo "  Voir les journaux: sudo journalctl -u $SERVICE_NAME -f"
echo "  Redémarrer le service: sudo systemctl restart $SERVICE_NAME"
echo "  Arrêter le service: sudo systemctl stop $SERVICE_NAME"
echo ""
echo "L'interface web est accessible sur: http://localhost:5000"
echo ""