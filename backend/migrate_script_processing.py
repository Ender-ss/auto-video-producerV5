#!/usr/bin/env python3
"""
🔄 Migração do Banco de Dados - Script Processing
Adiciona campos necessários para a nova etapa de processamento de roteiro
"""

import sqlite3
import os
import sys
from datetime import datetime

def migrate_database():
    """Executar migração para adicionar campos do script processing"""
    
    print("🔄 MIGRAÇÃO DO BANCO DE DADOS - SCRIPT PROCESSING")
    print("=" * 60)
    
    # Verificar se o banco existe
    db_path = 'instance/auto_video_producer.db'
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado em:", db_path)
        return False
    
    # Fazer backup do banco
    backup_path = f'instance/backup_before_script_processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível criar backup: {e}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n📋 Verificando estrutura atual da tabela pipeline...")
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(pipeline)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'script_processing_results' in columns:
            print("✅ Coluna 'script_processing_results' já existe!")
            return True
        
        print("\n🔧 Adicionando nova coluna 'script_processing_results'...")
        
        # Adicionar nova coluna
        cursor.execute("""
            ALTER TABLE pipeline 
            ADD COLUMN script_processing_results TEXT
        """)
        
        conn.commit()
        print("✅ Coluna 'script_processing_results' adicionada com sucesso!")
        
        # Verificar se a migração foi bem-sucedida
        cursor.execute("PRAGMA table_info(pipeline)")
        columns_after = [column[1] for column in cursor.fetchall()]
        
        if 'script_processing_results' in columns_after:
            print("✅ Migração verificada com sucesso!")
            
            # Mostrar estatísticas
            cursor.execute("SELECT COUNT(*) FROM pipeline")
            total_pipelines = cursor.fetchone()[0]
            print(f"📊 Total de pipelines na base: {total_pipelines}")
            
            print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 60)
            print("📋 Próximos passos:")
            print("1. Reinicie o backend: python app.py")
            print("2. Teste a nova funcionalidade de script processing")
            print("3. Monitore os logs para verificar se tudo está funcionando")
            
            return True
        else:
            print("❌ Erro: Coluna não foi adicionada corretamente")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def verify_migration():
    """Verificar se a migração foi aplicada corretamente"""
    
    db_path = 'instance/auto_video_producer.db'
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(pipeline)")
        columns = [column[1] for column in cursor.fetchall()]
        
        required_columns = [
            'script_processing_results'
        ]
        
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"❌ Colunas faltando: {missing_columns}")
            return False
        else:
            print("✅ Todas as colunas necessárias estão presentes")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar migração: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_migration()
    else:
        migrate_database()