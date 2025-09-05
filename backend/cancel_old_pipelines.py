#!/usr/bin/env python3
"""
Script para cancelar pipelines antigos com problemas
"""

import sqlite3
import os

def cancel_old_pipelines():
    """Cancelar pipelines antigos com importações incorretas"""
    
    db_path = 'instance/auto_video_producer.db'
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Cancelar todos os pipelines pendentes
        cursor.execute("""
            UPDATE pipeline 
            SET status = 'cancelled', 
                error_message = 'Pipeline antigo cancelado - usar novo sistema',
                completed_at = datetime('now')
            WHERE status IN ('queued', 'processing', 'paused')
        """)
        
        count = cursor.rowcount
        conn.commit()
        
        print(f"✅ {count} pipelines antigos cancelados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    cancel_old_pipelines()