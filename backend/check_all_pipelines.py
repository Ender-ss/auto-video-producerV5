from app import app, Pipeline, db

# Script completo para verificar pipelines
try:
    with app.app_context():
        # 1. Verificar total de pipelines no banco
        total_pipelines = db.session.query(Pipeline).count()
        print(f"Total de pipelines no banco de dados: {total_pipelines}")
        
        if total_pipelines == 0:
            print("Nenhum pipeline encontrado no banco de dados.")
        else:
            # 2. Verificar pipelines com status de erro
            error_pipelines = Pipeline.query.filter(Pipeline.status == 'error').all()
            print(f"\nPipelines com status de erro: {len(error_pipelines)}")
            for p in error_pipelines:
                print(f"- ID: {p.id}, Status: {p.status}, Erro: {p.error_message or 'Nenhum'}")
                print(f"  Iniciado em: {p.started_at}, Progresso: {p.progress}%")
                
            # 3. Verificar pipelines recentes (todos os status)
            recent_pipelines = Pipeline.query.order_by(Pipeline.started_at.desc()).limit(10).all()
            print(f"\nÚltimos 10 pipelines:")
            for p in recent_pipelines:
                print(f"- ID: {p.id}, Status: {p.status}, Iniciado em: {p.started_at}")
                print(f"  Erro: {p.error_message or 'Nenhum'}, Progresso: {p.progress}%")
        
        # 4. Verificar colunas da tabela Pipeline
        print("\nEstrutura da tabela Pipeline:")
        columns = Pipeline.__table__.columns.keys()
        for col in columns:
            print(f"- {col}")
            
except Exception as e:
    print(f"Erro ao consultar pipelines: {str(e)}")