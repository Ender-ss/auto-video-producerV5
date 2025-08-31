#!/usr/bin/env python3
"""
Script para verificar pipelines de teste que estão em aguardo
"""

from app import app, Pipeline, db
import json
from datetime import datetime, timedelta

def check_test_pipelines():
    with app.app_context():
        # Verificar pipelines em estados de teste
        test_statuses = ['queued', 'processing', 'paused']
        pipelines = Pipeline.query.filter(Pipeline.status.in_(test_statuses)).all()
        
        print(f'🔍 PIPELINES EM TESTE ENCONTRADAS: {len(pipelines)}')
        print('=' * 50)
        
        test_pipelines = []
        for p in pipelines:
            print(f'ID: {p.pipeline_id[:8]}...')
            print(f'Display Name: {p.display_name}')
            print(f'Status: {p.status}')
            print(f'Título: {p.title}')
            print(f'Iniciado em: {p.started_at}')
            print(f'Canal: {p.channel_url or "N/A"}')
            
            # Verificar se é pipeline de teste (sem canal ou com títulos de teste)
            is_test = (
                not p.channel_url or
                'test' in (p.title or '').lower() or
                'exemplo' in (p.title or '').lower() or
                'demo' in (p.title or '').lower()
            )
            
            if is_test:
                test_pipelines.append(p)
                print('   ⚠️  MARCADO COMO TESTE')
            
            print('-' * 30)
        
        # Verificar também todas as pipelines por status
        print(f'\n📊 ESTATÍSTICAS GERAIS:')
        from sqlalchemy import func
        status_counts = db.session.query(Pipeline.status, func.count(Pipeline.id)).group_by(Pipeline.status).all()
        for status, count in status_counts:
            print(f'{status}: {count} pipelines')
        
        # Verificar pipelines muito antigas em estado pendente
        cutoff_date = datetime.utcnow() - timedelta(hours=2)
        old_pending = Pipeline.query.filter(
            Pipeline.status.in_(['queued', 'processing']),
            Pipeline.started_at < cutoff_date
        ).all()
        
        print(f'\n⏰ PIPELINES ANTIGAS EM AGUARDO (>{2}h):')
        for p in old_pending:
            hours_old = (datetime.utcnow() - p.started_at).total_seconds() / 3600
            print(f'  {p.display_name} - {p.status} - {hours_old:.1f}h atrás')
        
        return test_pipelines, old_pending

def cleanup_test_pipelines(test_pipelines):
    """Limpar pipelines de teste se confirmado"""
    if not test_pipelines:
        print("✅ Nenhuma pipeline de teste encontrada para limpar")
        return
    
    print(f"\n🗑️  PIPELINES DE TESTE IDENTIFICADAS PARA LIMPEZA:")
    for p in test_pipelines:
        print(f"  - {p.display_name} ({p.status})")
    
    # Perguntar confirmação (descomentarr se quiser automático)
    # for p in test_pipelines:
    #     p.status = 'cancelled'
    #     db.session.commit()
    # print(f"✅ {len(test_pipelines)} pipelines de teste foram canceladas")

if __name__ == '__main__':
    test_pipelines, old_pipelines = check_test_pipelines()
    cleanup_test_pipelines(test_pipelines)