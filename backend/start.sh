#!/bin/bash

# Abilita il debug per mostrare i comandi eseguiti (opzionale)
set -e

# Attiva l'ambiente virtuale (se usi venv)
# source venv/bin/activate  # Rimuovi il commento se usi un virtualenv

# Avvia FastAPI con Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload