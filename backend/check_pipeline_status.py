from app import app, Pipeline, db

# Carregar todos os pipelines
try:
    with app.app_context():
        # Verificar pipeline específica que falhou no log
        pipeline_id = "c3bc9381-28a3-4876-b6fe-5275d8c31540"
        pipeline = Pipeline.query.filter_by(id=pipeline_id).first()
        
        if pipeline:
            print(f"Pipeline {pipeline_id} encontrada!")
            print(f"Status: {pipeline.status}")
            print(f"Erro: {pipeline.error_message or 'Nenhum'}")
            print(f"Data de início: {pipeline.started_at}")
            print(f"Data de conclusão: {pipeline.completed_at or 'Não concluída'}")
            print(f"Progresso: {pipeline.progress}%")
        else:
            print(f"Pipeline {pipeline_id} não encontrada no banco de dados.")
            
        # Verificar pipelines recentes para comparação
        print("\nÚltimos 5 pipelines:")
        recent_pipelines = Pipeline.query.order_by(Pipeline.started_at.desc()).limit(5).all()
        for p in recent_pipelines:
            print(f"ID: {p.id}, Status: {p.status}, Iniciado em: {p.started_at}, Erro: {p.error_message or 'Nenhum'}")
            
except Exception as e:
    print(f"Erro ao consultar pipelines: {str(e)}")