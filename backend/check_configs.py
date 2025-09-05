#!/usr/bin/env python3
"""
Script simples para verificar configurações de pipelines
"""

import sqlite3
import json
import os

def check_configs():
    """Verificar configurações de pipelines pendentes"""
    
    db_path = 'instance/auto_video_producer.db'
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Buscar configurações de pipelines pendentes
        cursor.execute("SELECT pipeline_id, display_name, config_json FROM pipeline WHERE status IN ('queued', 'processing', 'paused')")
        pipelines = cursor.fetchall()
        
        print(f"📊 Encontrados {len(pipelines)} pipelines pendentes")
        
        for pipeline_id, display_name, config_json in pipelines:
            try:
                config = json.loads(config_json) if config_json else {}
                scripts_config = config.get('scripts', {})
                system = scripts_config.get('system', 'traditional')
                
                print(f"\n📋 Pipeline: {display_name}")
                print(f"   ID: {pipeline_id[:8]}...")
                print(f"   Sistema: {system}")
                
                # Verificar se tem storyteller
                config_str = json.dumps(config, indent=2)
                if 'storyteller' in config_str.lower():
                    print(f"   ⚠️  Contém storyteller na configuração")
                    print(f"   Scripts config: {json.dumps(scripts_config, indent=2)}")
                
            except Exception as e:
                print(f"   ❌ Erro ao processar: {e}")
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_configs()