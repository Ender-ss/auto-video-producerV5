#!/usr/bin/env python3

import requests
import json

def check_pipeline_status(pipeline_id):
    try:
        response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
        result = response.json()
        
        if result.get('success'):
            data = result['data']
            
            print(f"Status: {data.get('status')}")
            print(f"Etapa atual: {data.get('current_step')}")
            print(f"Progresso: {data.get('progress', 0)}%")
            
            # Verificar etapa de vídeo especificamente
            video_step = data.get('steps', {}).get('video', {})
            video_status = video_step.get('status')
            video_error = video_step.get('error')
            
            print(f"Status vídeo: {video_status}")
            
            if video_error:
                print(f"Erro vídeo: {video_error}")
                
                # Verificar se é o erro específico que estávamos corrigindo
                if "'module' object is not callable" in video_error:
                    print("❌ ERRO AINDA PRESENTE: 'module' object is not callable")
                    return False
                else:
                    print("✅ ERRO CORRIGIDO: Não é mais 'module' object is not callable")
                    return True
            elif video_status == 'completed':
                print("✅ SUCESSO: Etapa de vídeo completada sem erros")
                return True
            elif video_status == 'processing':
                print("⏳ Etapa de vídeo em processamento...")
                return None  # Ainda processando
            
        else:
            print(f"Erro na resposta: {result}")
            
    except Exception as e:
        print(f"Erro ao verificar status: {str(e)}")
        
    return False

if __name__ == "__main__":
    pipeline_id = "8473a776-5931-42ad-ab8e-2fb95498ef10"
    check_pipeline_status(pipeline_id)