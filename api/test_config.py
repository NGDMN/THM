# test_config.py
# Execute este arquivo para testar as configurações
import sys
import os

def test_config():
    """Testa todas as configurações do sistema"""
    print("🔧 TESTE DE CONFIGURAÇÕES DO SISTEMA")
    print("=" * 50)
    
    try:
        # Tenta importar o módulo config
        from config import config
        print("✅ Módulo config importado com sucesso")
        print()
        
        # Teste de validação completa
        print("📊 EXECUTANDO VALIDAÇÕES...")
        print("-" * 30)
        validations = config.validate_all()
        
        # Status geral
        status_icon = "✅" if validations['overall_status'] == 'success' else "⚠️" 
        print(f"{status_icon} Status Geral: {validations['overall_status'].upper()}")
        print()
        
        # Detalhes por seção
        sections = {
            'database': '🗄️ Banco de Dados',
            'api': '🌐 APIs Externas',
            'app': '📱 Aplicação',
            'cache': '💾 Cache',
            'weather': '🌤️ Meteorologia'
        }
        
        for section_key, section_name in sections.items():
            if section_key in validations:
                section_data = validations[section_key]
                status = "✅" if section_data.get('valid', True) else "❌"
                print(f"{status} {section_name}")
                
                # Mostra configurações
                if 'config' in section_data:
                    for key, value in section_data['config'].items():
                        print(f"   {key}: {value}")
                
                # Mostra problemas se houver
                if section_data.get('issues'):
                    for issue in section_data['issues']:
                        print(f"   ⚠️ {issue}")
                print()
        
        # Teste de configurações específicas
        print("🔍 TESTE DE CONFIGURAÇÕES ESPECÍFICAS")
        print("-" * 40)
        
        # Database
        print(f"🗄️ Database: {config.database.DB_NAME}")
        print(f"   Host: {config.database.DB_HOST}:{config.database.DB_PORT}")
        print(f"   Usuário: {config.database.DB_USER}")
        print()
        
        # APIs
        api_status = '✅' if config.api.OPENWEATHER_API_KEY else '❌'
        print(f"🌤️ OpenWeather API: {api_status}")
        if config.api.OPENWEATHER_API_KEY:
            key_preview = config.api.OPENWEATHER_API_KEY[:8] + "..." if len(config.api.OPENWEATHER_API_KEY) > 8 else config.api.OPENWEATHER_API_KEY
            print(f"   Chave: {key_preview}")
        print(f"   Timeout: {config.api.REQUEST_TIMEOUT}s")
        print(f"   Max Retries: {config.api.MAX_RETRIES}")
        print()
        
        # App
        print(f"🏠 Estados suportados: {len(config.app.ESTADOS_SUPORTADOS)}")
        print(f"   Lista: {', '.join(config.app.ESTADOS_SUPORTADOS[:5])}...")
        print(f"🔧 Modo debug: {config.app.DEBUG}")
        print(f"📝 Log level: {config.app.LOG_LEVEL}")
        print()
        
        # Cache
        cache_status = '✅' if config.cache.ENABLE_CACHE else '❌'
        print(f"💾 Cache habilitado: {cache_status}")
        print(f"   TTL: {config.cache.CACHE_TTL}s ({config.cache.CACHE_TTL//60} min)")
        print(f"   Tamanho máximo: {config.cache.CACHE_SIZE}")
        print()
        
        # Weather
        print(f"🌡️ Alertas de temperatura: {config.weather.ALERT_TEMPERATURE_MIN}°C - {config.weather.ALERT_TEMPERATURE_MAX}°C")
        print(f"💧 Alertas de umidade: {config.weather.ALERT_HUMIDITY_MIN}% - {config.weather.ALERT_HUMIDITY_MAX}%")
        print(f"🔄 Intervalo de atualização: {config.weather.UPDATE_INTERVAL}s ({config.weather.UPDATE_INTERVAL//60} min)")
        print()
        
        # Teste de cidades principais
        print("🏙️ CIDADES PRINCIPAIS CONFIGURADAS")
        print("-" * 35)
        for estado, cidades in list(config.app.CIDADES_PRINCIPAIS.items())[:3]:
            print(f"{estado}: {', '.join(cidades)}")
        print(f"... e mais {len(config.app.CIDADES_PRINCIPAIS) - 3} estados")
        print()
        
        # Verificações de arquivos
        print("📁 VERIFICAÇÃO DE ARQUIVOS")
        print("-" * 25)
        files_to_check = ['.env', 'config.py', 'test_config.py']
        for filename in files_to_check:
            exists = os.path.exists(filename)
            status = "✅" if exists else "❌"
            print(f"{status} {filename}")
        print()
        
        # Resumo final
        print("📋 RESUMO FINAL")
        print("-" * 15)
        if validations['overall_status'] == 'success':
            print("🎉 Sistema configurado corretamente!")
            print("✅ Pronto para uso em desenvolvimento")
            if not config.app.DEBUG:
                print("🚀 Configurado para produção")
        else:
            print("⚠️ Configuração precisa de ajustes:")
            if 'failed_sections' in validations:
                print(f"   Seções com problemas: {', '.join(validations['failed_sections'])}")
            print("💡 Verifique o arquivo .env e ajuste as configurações necessárias")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("\n💡 SOLUÇÕES POSSÍVEIS:")
        print("1. Certifique-se de estar na pasta correta (onde está o config.py)")
        print("2. Verifique se o arquivo .env está na mesma pasta")
        print("3. Instale as dependências: pip install psycopg2-binary python-dotenv")
        print("4. Verifique se o arquivo config.py não tem erros de sintaxe")
        
    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        print(f"   Tipo do erro: {type(e).__name__}")
        print("\n💡 Verifique:")
        print("- Se todas as variáveis de ambiente estão corretas")
        print("- Se os valores no .env são válidos")
        print("- Se não há caracteres especiais mal formatados")

def create_sample_env():
    """Cria um arquivo .env de exemplo se não existir"""
    if not os.path.exists('.env'):
        print("📝 Criando arquivo .env de exemplo...")
        try:
            from config import config
            env_content = config.get_env_template()
            with open('.env.example', 'w', encoding='utf-8') as f:
                f.write(env_content)
            print("✅ Arquivo .env.example criado!")
            print("💡 Renomeie para .env e configure suas credenciais")
        except Exception as e:
            print(f"❌ Erro ao criar .env.example: {e}")

if __name__ == "__main__":
    # Executa os testes
    test_config()
    
    # Oferece criar arquivo .env de exemplo
    print("\n" + "="*50)
    create_sample_env()
    
    print("\n🎯 COMO USAR:")
    print("1. Execute: python test_config.py")
    print("2. Configure o arquivo .env com suas credenciais")
    print("3. Execute novamente para validar")
    print("4. Use: python -c \"from config import config; print(config.validate_all())\"")
    
    input("\n📱 Pressione Enter para finalizar...")