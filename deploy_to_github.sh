#!/bin/bash
# deploy_to_github.sh
# Script para subir cambios del SIEG mapa global a GitHub

# Variables
REPO_DIR="/home/miguelc/sieg-mapa-global"
REPO_URL="https://github.com/mcasrom/sieg-mapa-global.git"
GIT_USER="mcasrom"
GIT_EMAIL="mcasrom@gmail.com"

# Entrar en el repo
cd "$REPO_DIR" || { echo "No se encuentra $REPO_DIR"; exit 1; }

# Config git usuario local
git config user.name "$GIT_USER"
git config user.email "$GIT_EMAIL"

# Añadir todos los cambios
git add .

# Commit con fecha y hora
COMMIT_MSG="Actualización automática SIEG $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$COMMIT_MSG"

# Push usando token guardado (assume ya autenticado)
git push origin main || { echo "Error subiendo al repositorio"; exit 1; }

echo "✅ Cambios subidos correctamente al GitHub"
