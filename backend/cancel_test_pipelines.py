#!/usr/bin/env python3
"""
Script para cancelar pipelines de teste que estão em aguardo
"""

from app import app, Pipeline, db
from datetime import datetime

def cancel_test_pipelines():
    with app.app_context():
        try:
            # Buscar pipelines em estado de teste
            test_statuses = ['queued', 'processing', 'paused']
            pipelines = Pipeline.query.filter(Pipeline.status.in_(test_statuses)).all()
            
            cancelled_count = 0
            test_pipelines = []
            
            for p in pipelines:
                # Verificar se é pipeline de teste
                is_test = (
                    'teste' in (p.title or '').lower() or
                    'test' in (p.title or '').lower() or
                    'exemplo' in (p.title or '').lower() or
                    'demo' in (p.title or '').lower() or
                    p.title == 'Pipeline sem título'  # Pipelines sem título específico
                )
                
                if is_test:
                    test_pipelines.append(p)
            
            print(f"🔍 Encontradas {len(test_pipelines)} pipelines de teste para cancelar:")
            
            for p in test_pipelines:
                print(f"  - {p.display_name}: {p.title} ({p.status})")
            
            if test_pipelines:
                confirm = input(f"\n❓ Cancelar {len(test_pipelines)} pipelines de teste? (s/N): ")
                
                if confirm.lower() in ['s', 'sim', 'y', 'yes']:
                    for p in test_pipelines:
                        p.status = 'cancelled'
                        p.completed_at = datetime.utcnow()
                        cancelled_count += 1
                    
                    db.session.commit()
                    print(f"✅ {cancelled_count} pipelines de teste foram canceladas com sucesso!")
                    
                    # Verificar se ainda existem pipelines aguardando
                    remaining = Pipeline.query.filter(Pipeline.status.in_(['queued', 'processing'])).count()
                    print(f"📊 Pipelines restantes aguardando: {remaining}")
                    
                else:
                    print("❌ Operação cancelada pelo usuário")
            else:
                print("✅ Nenhuma pipeline de teste encontrada")
                
        except Exception as e:
            print(f"❌ Erro ao cancelar pipelines: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    cancel_test_pipelines()