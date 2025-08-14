#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir o problema de timeout no yt-dlp
Identificamos que o problema está no processamento das entradas após a extração
"""

import signal
import time
from contextlib import contextmanager

@contextmanager
def timeout_context(seconds):
    """Context manager para timeout"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operação excedeu {seconds} segundos")
    
    # Configurar o sinal de timeout
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Restaurar o handler anterior e cancelar o alarme
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def process_entries_safely(entries, max_results=5, timeout_per_entry=2):
    """Processar entradas com timeout por entrada"""
    videos = []
    processed_count = 0
    
    print(f"📊 Processando {len(entries)} entradas (max: {max_results})...")
    
    for i, entry in enumerate(entries):
        if processed_count >= max_results:
            break
            
        if not entry:  # Pular entradas vazias
            print(f"  ⚠️ Entrada {i+1} vazia, pulando...")
            continue
        
        try:
            print(f"  🔄 Processando entrada {i+1}/{len(entries)}...")
            
            # Usar timeout para cada entrada
            with timeout_context(timeout_per_entry):
                # Processar dados do vídeo
                processed_video = {
                    'video_id': entry.get('id', ''),
                    'title': entry.get('title', ''),
                    'description': (entry.get('description', '') or '')[:500],  # Limitar descrição
                    'thumbnail': entry.get('thumbnail', ''),
                    'duration': str(entry.get('duration', 0)) + 's' if entry.get('duration') else '',
                    'views': entry.get('view_count', 0) or 0,
                    'likes': entry.get('like_count', 0) or 0,
                    'published_at': entry.get('upload_date', ''),
                    'url': entry.get('webpage_url', f"https://youtube.com/watch?v={entry.get('id', '')}")
                }
                
                videos.append(processed_video)
                processed_count += 1
                print(f"  ✅ Entrada {i+1} processada: {processed_video.get('title', 'Sem título')[:50]}...")
                
        except TimeoutError:
            print(f"  ⏰ Timeout na entrada {i+1}, pulando...")
            continue
        except Exception as e:
            print(f"  ❌ Erro na entrada {i+1}: {str(e)[:100]}...")
            continue
    
    print(f"📊 Processamento concluído: {len(videos)} vídeos processados")
    return videos

if __name__ == "__main__":
    print("🔧 Script de correção do timeout do yt-dlp")
    print("Este script contém funções para corrigir o problema de timeout")
    print("Aplique as correções no arquivo automations.py")