#!/usr/bin/env python3
"""
🔍 Análise dos Logs da Pipeline
Busca logs específicos da pipeline para entender problemas
"""

import json
import requests
import time

def get_pipeline_logs():
    """Buscar logs detalhados da pipeline"""
    
    print("📝 ANÁLISE DOS LOGS DA PIPELINE")
    print("=" * 50)
    
    try:
        pipeline_id = "7688c518-1ef8-4bdb-928b-35921b55d5b9"
        
        # 1. Buscar logs da pipeline específica
        print(f"📋 Buscando logs da pipeline: {pipeline_id}")
        response = requests.get(f'http://localhost:5000/api/pipeline/logs/{pipeline_id}')
        
        if response.status_code != 200:
            print(f"❌ ERRO: Falha ao buscar logs: {response.status_code}")
            # Tentar buscar através do status
            status_response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
            if status_response.status_code == 200:
                status_result = status_response.json()
                if status_result.get('success') and status_result.get('data'):
                    pipeline_data = status_result['data']
                    logs = pipeline_data.get('logs', [])
                    if logs:
                        print(f"📊 Logs encontrados no status: {len(logs)}")
                        print("\n📋 LOGS DA PIPELINE:")
                        for log in logs[-20:]:  # Últimos 20 logs
                            timestamp = log.get('timestamp', 'N/A')
                            level = log.get('level', 'INFO')
                            message = log.get('message', 'N/A')
                            print(f"   [{timestamp}] [{level.upper()}] {message}")
                    else:
                        print("⚠️ Nenhum log encontrado no status")
                else:
                    print("❌ Erro ao acessar dados do status")
            return False
            
        result = response.json()
        
        if not result.get('success'):
            print(f"❌ ERRO: {result.get('error', 'Erro desconhecido')}")
            return False
            
        logs_data = result.get('data', {})
        logs = logs_data.get('logs', [])
        
        if not logs:
            print("⚠️ Nenhum log encontrado para esta pipeline")
            
            # Tentar buscar logs do sistema
            print("\n🔍 Buscando logs do sistema...")
            system_response = requests.get('http://localhost:5000/api/system/logs')
            if system_response.status_code == 200:
                system_result = system_response.json()
                if system_result.get('success'):
                    system_logs = system_result.get('data', {}).get('logs', [])
                    
                    # Filtrar logs relacionados à pipeline
                    pipeline_logs = []
                    for log in system_logs:
                        message = log.get('message', '').lower()
                        if pipeline_id.lower() in message or 'pipeline' in message:
                            pipeline_logs.append(log)
                    
                    if pipeline_logs:
                        print(f"📊 Logs do sistema relacionados à pipeline: {len(pipeline_logs)}")
                        print("\n📋 LOGS DO SISTEMA:")
                        for log in pipeline_logs[-10:]:
                            timestamp = log.get('timestamp', 'N/A')
                            level = log.get('level', 'INFO')
                            message = log.get('message', 'N/A')
                            source = log.get('source', 'N/A')
                            print(f"   [{timestamp}] [{level.upper()}] [{source}] {message}")
                    else:
                        print("⚠️ Nenhum log do sistema relacionado à pipeline encontrado")
            return False
        
        print(f"📊 Total de logs encontrados: {len(logs)}")
        
        # 2. Analisar logs por nível
        levels_count = {}
        for log in logs:
            level = log.get('level', 'unknown')
            levels_count[level] = levels_count.get(level, 0) + 1
        
        print(f"\n📊 DISTRIBUIÇÃO POR NÍVEL:")
        print("-" * 30)
        for level, count in sorted(levels_count.items()):
            print(f"   {level.upper()}: {count}")
        
        # 3. Mostrar logs mais recentes
        print(f"\n📋 LOGS MAIS RECENTES (últimos 20):")
        print("-" * 30)
        
        recent_logs = logs[-20:] if len(logs) > 20 else logs
        for log in recent_logs:
            timestamp = log.get('timestamp', 'N/A')
            level = log.get('level', 'INFO')
            message = log.get('message', 'N/A')
            step = log.get('step', '')
            
            level_indicator = {
                'error': '❌',
                'warning': '⚠️',
                'info': 'ℹ️',
                'success': '✅'
            }.get(level, 'ℹ️')
            
            step_info = f"[{step}]" if step else ""
            print(f"   {level_indicator} [{timestamp}] {step_info} {message}")
        
        # 4. Procurar por erros específicos
        error_logs = [log for log in logs if log.get('level') == 'error']
        if error_logs:
            print(f"\n❌ ERROS ENCONTRADOS ({len(error_logs)}):")
            print("-" * 30)
            for log in error_logs[-5:]:  # Últimos 5 erros
                timestamp = log.get('timestamp', 'N/A')
                message = log.get('message', 'N/A')
                data = log.get('data', {})
                print(f"   [{timestamp}] {message}")
                if data:
                    print(f"      Dados: {json.dumps(data, indent=6, ensure_ascii=False)}")
        
        # 5. Procurar por warnings
        warning_logs = [log for log in logs if log.get('level') == 'warning']
        if warning_logs:
            print(f"\n⚠️ WARNINGS ENCONTRADOS ({len(warning_logs)}):")
            print("-" * 30)
            for log in warning_logs[-3:]:  # Últimos 3 warnings
                timestamp = log.get('timestamp', 'N/A')
                message = log.get('message', 'N/A')
                print(f"   [{timestamp}] {message}")
        
        # 6. Análise temporal
        if logs:
            first_log = logs[0]
            last_log = logs[-1]
            print(f"\n⏰ ANÁLISE TEMPORAL:")
            print("-" * 30)
            print(f"   Primeiro log: {first_log.get('timestamp', 'N/A')}")
            print(f"   Último log: {last_log.get('timestamp', 'N/A')}")
            
            # Verificar se há atividade recente
            try:
                from datetime import datetime, timedelta
                last_timestamp = datetime.fromisoformat(last_log['timestamp'].replace('Z', '+00:00'))
                now = datetime.now().astimezone()
                
                time_diff = now - last_timestamp
                
                if time_diff.total_seconds() > 300:  # 5 minutos
                    print(f"   ⚠️ Última atividade há {int(time_diff.total_seconds() // 60)} minutos")
                    print("   Possível problema: Pipeline pode estar travada")
                else:
                    print(f"   ✅ Atividade recente: há {int(time_diff.total_seconds())} segundos")
            except:
                print("   ⚠️ Não foi possível analisar timestamp")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao backend.")
        return False
    except Exception as e:
        print(f"❌ ERRO: Exceção durante a análise: {str(e)}")
        return False

if __name__ == "__main__":
    get_pipeline_logs()