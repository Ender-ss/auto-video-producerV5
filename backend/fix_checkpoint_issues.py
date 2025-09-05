#!/usr/bin/env python3
"""
Script para verificar e corrigir checkpoints com importações incorretas
"""

import os
import sys
import json
import sqlite3
from pathlib import Path

def fix_checkpoints():
    """Corrigir checkpoints com importações incorretas"""
    
    # Caminho do banco de dados
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'auto_video_producer.db')
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado")
        return
    
    print("🔍 Verificando banco de dados...")
    
    # Conectar ao banco
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Buscar pipelines com problemas
        cursor.execute("""
            SELECT pipeline_id, display_name, status, config_json, error_message 
            FROM pipeline 
            WHERE status IN ('queued', 'processing', 'paused') 
            AND error_message LIKE '%generate_storyteller_script%'
        """)
        
        problematic_pipelines = cursor.fetchall()
        
        if not problematic_pipelines:
            print("✅ Nenhum pipeline problemático encontrado")
            
            # Verificar todos os pipelines pendentes
            cursor.execute("""
                SELECT pipeline_id, display_name, status, config_json 
                FROM pipeline 
                WHERE status IN ('queued', 'processing', 'paused')
            """)
            
            pending_pipelines = cursor.fetchall()
            if pending_pipelines:
                print(f"📊 Pipelines pendentes encontrados: {len(pending_pipelines)}")
                for pipeline in pending_pipelines:
                    pipeline_id, display_name, status, config_json = pipeline
                    print(f"   - {display_name} ({pipeline_id[:8]}...): {status}")
                    
                    # Verificar config_json
                    try:
                        config = json.loads(config_json) if config_json else {}
                        scripts_config = config.get('scripts', {})
                        if 'storyteller' in str(scripts_config).lower():
                            print(f"     ⚠️  Config contém storyteller: {scripts_config}")
                    except:
                        pass
            
        else:
            print(f"❌ Encontrados {len(problematic_pipelines)} pipelines com problemas")
            
            for pipeline in problematic_pipelines:
                pipeline_id, display_name, status, config_json, error_message = pipeline
                print(f"   - {display_name} ({pipeline_id[:8]}...): {status}")
                print(f"     Erro: {error_message[:100]}...")
                
                # Cancelar ou resetar pipeline
                cursor.execute("""
                    UPDATE pipeline 
                    SET status = 'failed', 
                        error_message = 'Pipeline cancelado devido a erro de importação antiga'
                    WHERE pipeline_id = ?
                """, (pipeline_id,))
                
                print(f"     ✅ Pipeline {pipeline_id[:8]}... cancelado")
        
        conn.commit()
        
        # Verificar arquivos de checkpoint
        checkpoint_dir = os.path.join(os.path.dirname(__file__), 'checkpoints')
        if os.path.exists(checkpoint_dir):
            print(f"\n🔍 Verificando checkpoints...")
            for root, dirs, files in os.walk(checkpoint_dir):
                for file in files:
                    if file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if 'generate_storyteller_script' in content and 'routes.storyteller' in content:
                                    print(f"     ❌ Checkpoint problemático: {file_path}")
                                    # Renomear arquivo problemático
                                    backup_path = file_path + '.backup'
                                    os.rename(file_path, backup_path)
                                    print(f"     ✅ Arquivo renomeado para: {backup_path}")
                        except Exception as e:
                            print(f"     ⚠️ Erro ao verificar {file_path}: {e}")
        
        print("\n✅ Verificação concluída!")
        
    except Exception as e:
        print(f"❌ Erro durante a verificação: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_checkpoints()