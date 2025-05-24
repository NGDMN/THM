import React, { useState, useEffect } from 'react';

const API_BASE = 'https://thm-pg0z.onrender.com';

const ApiDebugDashboard = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState({
    api: 'checking',
    database: 'checking',
    endpoints: 0,
    totalEndpoints: 0
  });
  const [testResults, setTestResults] = useState({});

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = {
      id: Date.now(),
      timestamp,
      message,
      type
    };
    setLogs(prev => [...prev.slice(-49), logEntry]);
  };

  const clearLogs = () => setLogs([]);

  const testEndpoint = async (endpoint, description) => {
    try {
      addLog(`🔍 Testando ${description}: ${endpoint}`, 'info');
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000);
      
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      clearTimeout(timeoutId);
      
      const responseText = await response.text();
      let responseData = null;
      
      try {
        responseData = JSON.parse(responseText);
      } catch (e) {
        responseData = responseText;
      }
      
      const result = {
        endpoint,
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        data: responseData,
        headers: Object.fromEntries(response.headers.entries()),
        responseTime: Date.now()
      };
      
      if (response.ok) {
        addLog(`✅ ${description}: ${response.status} OK`, 'success');
        if (Array.isArray(responseData)) {
          addLog(`   📊 Retornou ${responseData.length} itens`, 'info');
        } else if (typeof responseData === 'object' && responseData !== null) {
          addLog(`   📋 Objeto com ${Object.keys(responseData).length} propriedades`, 'info');
        }
      } else {
        addLog(`❌ ${description}: ${response.status} ${response.statusText}`, 'error');
        if (responseText) {
          addLog(`   📄 Erro: ${responseText.substring(0, 200)}${responseText.length > 200 ? '...' : ''}`, 'error');
        }
      }
      
      setTestResults(prev => ({
        ...prev,
        [endpoint]: result
      }));
      
      return result;
      
    } catch (error) {
      const errorResult = {
        endpoint,
        error: error.message,
        ok: false,
        status: 0
      };
      
      if (error.name === 'AbortError') {
        addLog(`⏰ ${description}: Requisição excedeu o tempo limite (15s)`, 'error');
      } else {
        addLog(`❌ ${description}: ${error.message}`, 'error');
      }
      
      setTestResults(prev => ({
        ...prev,
        [endpoint]: errorResult
      }));
      
      return errorResult;
    }
  };

  const testAllEndpoints = async () => {
    setLoading(true);
    addLog('🚀 Iniciando teste completo de endpoints...', 'info');
    
    const endpoints = [
      { path: '/', description: 'Status da API' },
      { path: '/test-db', description: 'Conexão com Banco' },
      { path: '/municipios', description: 'Dados de Municípios' },
      { path: '/debug/tabelas', description: 'Estrutura das Tabelas' },
      { path: '/debug/historico', description: 'Debug de Dados Históricos' },
      { path: '/debug/openweather', description: 'Configuração OpenWeather' },
      { path: '/previsao/alertas', description: 'Alertas Meteorológicos' },
      { path: '/historico/chuvas?cidade=Rio de Janeiro&estado=RJ', description: 'Histórico de Chuvas' },
      { path: '/previsao/chuvas?cidade=Rio de Janeiro&estado=RJ', description: 'Previsão de Chuvas' }
    ];

    let successCount = 0;
    
    for (const { path, description } of endpoints) {
      const result = await testEndpoint(path, description);
      if (result.ok) successCount++;
      await new Promise(resolve => setTimeout(resolve, 500)); // Rate limiting
    }
    
    setSystemStatus(prev => ({
      ...prev,
      endpoints: successCount,
      totalEndpoints: endpoints.length,
      api: successCount > 0 ? (successCount === endpoints.length ? 'online' : 'partial') : 'offline'
    }));
    
    addLog(`🎯 Teste completo: ${successCount}/${endpoints.length} endpoints funcionando`, 
           successCount === endpoints.length ? 'success' : 'warning');
    
    setLoading(false);
  };

  const testDatabaseConnection = async () => {
    setLoading(true);
    addLog('🗄️ Testando conexão com PostgreSQL...', 'info');
    
    const result = await testEndpoint('/test-db', 'Teste de Banco');
    
    if (result.ok && result.data) {
      setSystemStatus(prev => ({ ...prev, database: result.data.success ? 'online' : 'offline' }));
      
      if (result.data.database_config) {
        const config = result.data.database_config;
        addLog(`📊 Config DB: ${config.host}:${config.port}/${config.database}`, 'info');
        addLog(`👤 Usuário: ${config.user}`, 'info');
      }
    } else {
      setSystemStatus(prev => ({ ...prev, database: 'offline' }));
    }
    
    setLoading(false);
  };

  const populateTestData = async () => {
    setLoading(true);
    addLog('📥 Populando banco com dados de teste...', 'info');
    
    try {
      const response = await fetch(`${API_BASE}/admin/popular-dados-teste`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      
      if (response.ok) {
        addLog('✅ Dados de teste inseridos com sucesso', 'success');
        addLog(`📝 ${data.mensagem || 'Dados inseridos'}`, 'info');
        
        // Atualizar dados do sistema
        await testEndpoint('/debug/historico', 'Atualização de Dados Históricos');
      } else {
        addLog(`❌ Falha ao popular dados: ${data.erro || 'Erro desconhecido'}`, 'error');
      }
      
    } catch (error) {
      addLog(`❌ Erro ao popular dados: ${error.message}`, 'error');
    }
    
    setLoading(false);
  };

  const runFullDiagnostic = async () => {
    clearLogs();
    setLoading(true);
    addLog('🔧 Iniciando diagnóstico completo do sistema...', 'info');
    
    await testDatabaseConnection();
    await new Promise(resolve => setTimeout(resolve, 1000));
    await testAllEndpoints();
    
    addLog('🎯 Diagnóstico completo finalizado', 'success');
    setLoading(false);
  };

  const getStatusBadge = (status) => {
    const badges = {
      online: { text: 'Online', class: 'bg-green-100 text-green-800' },
      offline: { text: 'Offline', class: 'bg-red-100 text-red-800' },
      partial: { text: 'Parcial', class: 'bg-yellow-100 text-yellow-800' },
      checking: { text: 'Verificando...', class: 'bg-gray-100 text-gray-800' }
    };
    
    const badge = badges[status] || badges.checking;
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badge.class}`}>
        {badge.text}
      </span>
    );
  };

  const getLogIcon = (type) => {
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️'
    };
    return icons[type] || icons.info;
  };

  useEffect(() => {
    // Executar diagnóstico ao montar
    setTimeout(runFullDiagnostic, 1000);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Cabeçalho */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                🛠️ Dashboard de Debug da API
              </h1>
              <p className="text-gray-600">
                Sistema de Previsão de Alagamentos - Diagnóstico Completo
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">API Base</p>
              <p className="font-mono text-sm">{API_BASE}</p>
            </div>
          </div>
        </div>

        {/* Cards de Status */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Status da API</p>
                <p className="text-2xl font-bold text-gray-900">
                  {systemStatus.endpoints}/{systemStatus.totalEndpoints}
                </p>
              </div>
              <div>
                {getStatusBadge(systemStatus.api)}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Banco de Dados</p>
                <p className="text-2xl font-bold text-gray-900">PostgreSQL</p>
              </div>
              <div>
                {getStatusBadge(systemStatus.database)}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Endpoints</p>
                <p className="text-2xl font-bold text-gray-900">
                  {Math.round((systemStatus.endpoints / Math.max(systemStatus.totalEndpoints, 1)) * 100)}%
                </p>
              </div>
              <div className="text-2xl">
                📡
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Última Verificação</p>
                <p className="text-sm font-bold text-gray-900">
                  {new Date().toLocaleTimeString()}
                </p>
              </div>
              <div className="text-2xl">
                🕐
              </div>
            </div>
          </div>
        </div>

        {/* Painel de Controle */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">🎮 Painel de Controle</h2>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={runFullDiagnostic}
              disabled={loading}
              className={`px-4 py-2 rounded-lg font-medium ${
                loading 
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {loading ? '⏳ Executando...' : '🔧 Diagnóstico Completo'}
            </button>
            
            <button
              onClick={testDatabaseConnection}
              disabled={loading}
              className={`px-4 py-2 rounded-lg font-medium ${
                loading 
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                  : 'bg-green-600 text-white hover:bg-green-700'
              }`}
            >
              🗄️ Testar Banco
            </button>
            
            <button
              onClick={testAllEndpoints}
              disabled={loading}
              className={`px-4 py-2 rounded-lg font-medium ${
                loading 
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                  : 'bg-purple-600 text-white hover:bg-purple-700'
              }`}
            >
              🌐 Testar Todos Endpoints
            </button>
            
            <button
              onClick={populateTestData}
              disabled={loading}
              className={`px-4 py-2 rounded-lg font-medium ${
                loading 
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                  : 'bg-orange-600 text-white hover:bg-orange-700'
              }`}
            >
              📥 Popular Dados Teste
            </button>
            
            <button
              onClick={clearLogs}
              className="px-4 py-2 rounded-lg font-medium bg-gray-600 text-white hover:bg-gray-700"
            >
              🗑️ Limpar Logs
            </button>
          </div>
        </div>

        {/* Grid de Resultados */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Resultados dos Endpoints */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">📊 Resultados dos Endpoints</h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {Object.entries(testResults).map(([endpoint, result]) => (
                <div key={endpoint} className={`p-3 rounded-lg border-l-4 ${
                  result.ok ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'
                }`}>
                  <div className="flex items-center justify-between">
                    <code className="text-sm font-mono text-gray-800">{endpoint}</code>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      result.ok ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {result.status || 'ERRO'}
                    </span>
                  </div>
                  {result.error && (
                    <p className="text-sm text-red-600 mt-1">{result.error}</p>
                  )}
                  {result.data && typeof result.data === 'object' && !Array.isArray(result.data) && (
                    <p className="text-sm text-gray-600 mt-1">
                      Objeto com {Object.keys(result.data).length} propriedades
                    </p>
                  )}
                  {Array.isArray(result.data) && (
                    <p className="text-sm text-gray-600 mt-1">
                      Array com {result.data.length} itens
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Logs em Tempo Real */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">📋 Logs em Tempo Real</h2>
              <span className="text-sm text-gray-500">{logs.length} entradas</span>
            </div>
            <div className="bg-gray-900 rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm">
              {logs.length === 0 ? (
                <div className="text-gray-400 text-center py-8">
                  Nenhum log ainda. Execute um diagnóstico para começar...
                </div>
              ) : (
                logs.map(log => (
                  <div key={log.id} className="flex items-start gap-2 py-1 border-b border-gray-700 last:border-b-0">
                    <span className="text-gray-400 text-xs mt-0.5 flex-shrink-0">
                      {log.timestamp}
                    </span>
                    <span className="flex-shrink-0">
                      {getLogIcon(log.type)}
                    </span>
                    <span className={`${
                      log.type === 'error' ? 'text-red-400' :
                      log.type === 'success' ? 'text-green-400' :
                      log.type === 'warning' ? 'text-yellow-400' :
                      'text-gray-300'
                    }`}>
                      {log.message}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Análise Rápida de Problemas */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">⚠️ Problemas Comuns & Soluções</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-red-50 rounded-lg border-l-4 border-red-500">
              <h3 className="font-semibold text-red-800 mb-2">Erro 500 (Servidor)</h3>
              <p className="text-sm text-red-700">
                Geralmente indica erro no Python. Verifique os logs do servidor para detalhes.
              </p>
            </div>
            
            <div className="p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
              <h3 className="font-semibold text-yellow-800 mb-2">Problemas de Conexão DB</h3>
              <p className="text-sm text-yellow-700">
                Verifique credenciais PostgreSQL e conectividade. Confirme se o banco está ativo no Render.
              </p>
            </div>
            
            <div className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
              <h3 className="font-semibold text-blue-800 mb-2">Respostas Vazias ({})</h3>
              <p className="text-sm text-blue-700">
                Pode indicar dados ausentes ou endpoints mal configurados. Verifique as tabelas.
              </p>
            </div>
            
            <div className="p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
              <h3 className="font-semibold text-green-800 mb-2">Problemas com PowerShell curl</h3>
              <p className="text-sm text-green-700">
                Use `Invoke-RestMethod` ou instale o curl adequado. Aliases do PowerShell podem causar conflitos.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ApiDebugDashboard; 