#!/bin/bash

# Script de désinstallation du service smart-downloads-organizer
# Usage : sudo ./scripts/uninstall_service.sh

set -e

SERVICE_NAME="smart-downloads-organizer"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
VENV_PATH="/opt/smart-downloads-organizer/venv"
INSTALL_DIR="/opt/smart-downloads-organizer"

# Vérification des privilèges root
if [ "$EUID" -ne 0 ]; then
    echo "Ce script doit être exécuté avec les privilèges root (sudo)."
    exit 1
fi

echo "========================================="
echo "Désinstallation de $SERVICE_NAME"
echo "========================================="

# Arrêt et désactivation du service
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "Arrêt du service en cours..."
    systemctl stop $SERVICE_NAME
fi

if systemctl is-enabled --quiet $SERVICE_NAME; then
    echo "Désactivation du service..."
    systemctl disable $SERVICE_NAME
fi

# Suppression du fichier de service systemd
if [ -f "$SERVICE_FILE" ]; then
    echo "Suppression du fichier de service : $SERVICE_FILE"
    rm -f "$SERVICE_FILE"
fi

# Rechargement du daemon systemd
echo "Rechargement du daemon systemd..."
systemctl daemon-reload
systemctl reset-failed

# Suppression de l'environnement virtuel
if [ -d "$VENV_PATH" ]; then
    echo "Suppression de l'environnement virtuel..."
    rm -rf "$VENV_PATH"
fi

# Suppression du répertoire d'installation
if [ -d "$INSTALL_DIR" ]; then
    echo "Suppression du répertoire d'installation..."
    rm -rf "$INSTALL_DIR"
fi

# Suppression des logs système
if [ -f "/var/log/smart-downloads-organizer.log" ]; then
    echo "Suppression des logs système..."
    rm -f "/var/log/smart-downloads-organizer.log"
fi

# Suppression des utilisateurs/groupe créés (si applicables)
if getent group sdo-organizer > /dev/null 2>&1; then
    echo "Suppression du groupe sdo-organizer..."
    groupdel sdo-organizer 2>/dev/null || true
fi

if id sdo-user > /dev/null 2>&1; then
    echo "Suppression de l'utilisateur sdo-user..."
    userdel sdo-user 2>/dev/null || true
fi

echo "========================================="
echo "Désinstallation terminée avec succès !"
echo "========================================="
echo ""
echo "Remarques :"
echo "1. Les fichiers de configuration personnels dans ~/.config/smart-downloads-organizer/"
echo "   et les logs dans ~/.cache/smart-downloads-organizer/ n'ont pas été supprimés."
echo "2. Pour supprimer complètement toutes les traces :"
echo "   rm -rf ~/.config/smart-downloads-organizer/"
echo "   rm -rf ~/.cache/smart-downloads-organizer/"
echo "========================================="