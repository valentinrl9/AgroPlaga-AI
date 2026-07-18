#!/usr/bin/env bash
# Ejecutar EN EL VPS (~/AgroPlaga-AI). Trae landing desde rama nexoagro sin cambiar de rama.
set -euo pipefail
cd "$(dirname "$0")/.."
git fetch origin nexoagro
git checkout FETCH_HEAD -- landing/
echo "Landing actualizada:"
ls -la landing/assets/
grep -E 'hero-invernadero|paso-escaneo' landing/index.html || true
echo "Comprueba: https://agroplaga-ai.farm/ (Ctrl+F5)"
