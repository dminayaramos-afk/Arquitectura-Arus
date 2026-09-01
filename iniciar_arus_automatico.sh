#!/bin/bash
echo "[ARUS] Limpiando procesos anteriores de Ollama..."
sudo pkill -9 ollama 2>/dev/null
sleep 1

echo "[ARUS] Iniciando Ollama optimizado para CPU y RAM..."
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_VULKAN=0
export CUDA_VISIBLE_DEVICES=""
ollama serve > /dev/null 2>&1 &
sleep 2

echo "[ARUS] Lanzando la interfaz de ARUS..."
python3 run.py
