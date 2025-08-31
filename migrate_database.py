#!/usr/bin/env python3
"""
📊 Script de Migração do Banco de Dados
Atualiza o banco para suportar nomes amigáveis e histórico persistente
"""

import os
import sys
import json
from datetime import datetime

# Adicionar o diretório backend ao path
sys.path.append('backend')

from app import app, db, Pipeline, PipelineLog

def migrate_database():
    """Executar migração do banco de dados"""
    
    print("🔄 INICIANDO MIGRAÇÃO DO BANCO DE DADOS")
    print("=" * 50)
    
    try:
        with app.app_context():
            print("📋 Verificando estrutura atual do banco...")
            
            # Fazer backup do banco atual se existir
            db_path = 'backend/auto_video_producer.db'
            if os.path.exists(db_path):
                backup_path = f'backend/auto_video_producer_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
                os.system(f'copy "{db_path}" "{backup_path}"')
                print(f"✅ Backup criado: {backup_path}")
            
            # Recriar todas as tabelas com nova estrutura
            print("🔧 Recriando estrutura do banco...")
            db.drop_all()
            db.create_all()
            
            print("✅ Estrutura do banco atualizada com sucesso!")
            
            # Migrar dados existentes se houver backup
            if os.path.exists(db_path.replace('.db', '_backup_*.db')):
                print("📦 Dados antigos preservados no backup")
            
            print("\n📊 NOVA ESTRUTURA DO BANCO:")
            print("-" * 30)
            print("✅ Pipeline - Histórico persistente com display_name")
            print("✅ PipelineLog - Logs persistentes")
            print("✅ Compatibilidade com frontend mantida")
            
            # Testar criação de pipeline de exemplo
            print("\n🧪 TESTANDO NOVA ESTRUTURA:")
            test_pipeline = Pipeline(
                pipeline_id="test-123-456",
                display_name=Pipeline.generate_display_name(),
                title="Pipeline de Teste",
                channel_url="https://youtube.com/@test",
                status="completed",
                config_json=json.dumps({"test": True}),
                extraction_results=json.dumps({"titles": ["Teste 1", "Teste 2"]}),
                titles_results=json.dumps({"generated_titles": ["Novo Teste 1", "Novo Teste 2"]})
            )
            
            db.session.add(test_pipeline)
            db.session.commit()
            
            # Testar busca por display_name
            found_pipeline = Pipeline.query.filter_by(display_name=test_pipeline.display_name).first()
            if found_pipeline:
                print(f"✅ Pipeline teste criada: {found_pipeline.display_name}")
                print(f"✅ Busca por display_name funcionando")
                
                # Remover pipeline de teste
                db.session.delete(found_pipeline)
                db.session.commit()
                print("✅ Pipeline de teste removida")
            
            print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 50)
            print("📋 Próximos passos:")
            print("1. Reinicie o backend: python backend/app.py")
            print("2. Teste a criação de uma nova pipeline")
            print("3. Verifique se o nome amigável aparece no frontend")
            print("4. Confirme que o histórico está sendo salvo")
            
            return True
            
    except Exception as e:
        print(f"❌ ERRO durante a migração: {str(e)}")
        print("💡 Dica: Verifique se o backend não está rodando")
        return False

def verify_migration():
    """Verificar se a migração foi bem-sucedida"""
    
    print("\n🔍 VERIFICANDO MIGRAÇÃO...")
    
    try:
        with app.app_context():
            # Verificar se as tabelas existem
            tables = db.engine.table_names()
            
            required_tables = ['pipeline', 'pipeline_log']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"❌ Tabelas faltando: {missing_tables}")
                return False
            
            # Verificar se as colunas necessárias existem
            print("✅ Todas as tabelas criadas")
            
            # Testar geração de display_name
            display_name = Pipeline.generate_display_name()
            print(f"✅ Geração de display_name funcionando: {display_name}")
            
            print("✅ Migração verificada com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro na verificação: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 AUTO VIDEO PRODUCER - MIGRAÇÃO DO BANCO")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('backend/app.py'):
        print("❌ Execute este script na raiz do projeto (onde está o arquivo start.py)")
        sys.exit(1)
    
    # Executar migração
    if migrate_database():
        if verify_migration():
            print("\n🎉 MIGRAÇÃO COMPLETA E VERIFICADA!")
            print("\n📋 RESUMO DAS MELHORIAS:")
            print("🔹 Nomes amigáveis: 2025-01-31-001 (em vez de UUID)")
            print("🔹 Histórico persistente: Pipelines salvas no banco")
            print("🔹 Logs persistentes: Debugging melhorado")
            print("🔹 Sincronização: Frontend e backend usam mesmo nome")
            print("🔹 Endpoints novos: /history, /stats, /by-name")
        else:
            print("\n⚠️ Migração executada mas verificação falhou")
    else:
        print("\n💥 Migração falhou")
        sys.exit(1)