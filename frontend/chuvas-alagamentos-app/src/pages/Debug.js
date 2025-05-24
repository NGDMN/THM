import React, { useEffect, useState } from 'react';
import './Debug.css';

const API_BASE = 'https://thm-pg0z.onrender.com';

function Debug() {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(false);

    const addLog = (message, type = 'info') => {
        const timestamp = new Date().toLocaleTimeString();
        setLogs(prevLogs => [...prevLogs, `[${timestamp}] ${message}`]);
    };

    const updateElement = (id, content, className = '') => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
            if (className) {
                element.className = className;
            }
        }
    };

    const testDatabase = async () => {
        setLoading(true);
        addLog('🧪 Testando conexão PostgreSQL...');
        
        try {
            const response = await fetch(`${API_BASE}/test-db`);
            const data = await response.json();
            
            if (data.success) {
                addLog('✅ PostgreSQL: Conexão bem-sucedida');
                updateElement('dbStatus', 'Online', 'status success');
            } else {
                addLog('❌ PostgreSQL: Falha na conexão');
                updateElement('dbStatus', 'Offline', 'status error');
            }
            
            addLog(`📊 Config DB: ${data.database_config.host}:${data.database_config.port}`);
            
        } catch (error) {
            addLog(`❌ Erro ao testar PostgreSQL: ${error.message}`);
            updateElement('dbStatus', 'Erro', 'status error');
        }
        
        setLoading(false);
    };

    const testEndpoints = async () => {
        const endpoints = [
            '/',
            '/municipios',
            '/previsao/alertas',
            '/test-db',
            '/debug/historico'
        ];
        
        addLog('🌐 Testando endpoints principais...');
        let successCount = 0;
        
        for (const endpoint of endpoints) {
            try {
                const response = await fetch(`${API_BASE}${endpoint}`);
                if (response.ok) {
                    addLog(`✅ ${endpoint}: OK (${response.status})`);
                    successCount++;
                } else {
                    addLog(`❌ ${endpoint}: ${response.status} ${response.statusText}`);
                }
            } catch (error) {
                addLog(`❌ ${endpoint}: ${error.message}`);
            }
        }
        
        updateElement('endpointsCount', `${successCount}/${endpoints.length}`);
        
        if (successCount === endpoints.length) {
            updateElement('apiStatus', 'Online', 'status success');
        } else if (successCount > 0) {
            updateElement('apiStatus', 'Parcial', 'status warning');
        } else {
            updateElement('apiStatus', 'Offline', 'status error');
        }
    };

    const testMunicipies = async () => {
        addLog('🏙️ Testando endpoint de municípios...');
        
        try {
            const response = await fetch(`${API_BASE}/municipios`);
            const data = await response.json();
            
            if (Array.isArray(data)) {
                addLog(`✅ Municípios carregados: ${data.length} registros`);
                updateElement('municipiosCount', data.length);
                
                const rjCount = data.filter(m => m.uf === 'RJ').length;
                const spCount = data.filter(m => m.uf === 'SP').length;
                addLog(`📊 RJ: ${rjCount}, SP: ${spCount}`);
            } else {
                addLog('❌ Dados de municípios inválidos');
            }
            
        } catch (error) {
            addLog(`❌ Erro ao carregar municípios: ${error.message}`);
        }
    };

    const loadSystemData = async () => {
        addLog('📊 Carregando dados do sistema...');
        
        try {
            const response = await fetch(`${API_BASE}/debug/historico`);
            const data = await response.json();
            
            updateElement('chuvasCount', data.chuvas_total || 0);
            updateElement('alagamentosCount', data.alagamentos_total || 0);
            
            addLog(`📈 Dados carregados - Chuvas: ${data.chuvas_total || 0}, Alagamentos: ${data.alagamentos_total || 0}`);
            
            if (data.chuvas_por_municipio && data.chuvas_por_municipio.length > 0) {
                addLog(`🏆 Município com mais registros de chuva: ${data.chuvas_por_municipio[0].municipio}/${data.chuvas_por_municipio[0].estado}`);
            }
            
        } catch (error) {
            addLog(`❌ Erro ao carregar dados do sistema: ${error.message}`);
        }
    };

    const testSpecificEndpoint = async (endpoint) => {
        addLog(`🔍 Testando: ${endpoint}`);
        
        try {
            const response = await fetch(`${API_BASE}${endpoint}`);
            const text = await response.text();
            
            if (response.ok) {
                addLog(`✅ ${endpoint}: ${response.status} OK`);
                
                try {
                    const data = JSON.parse(text);
                    if (Array.isArray(data)) {
                        addLog(`📊 Retornou ${data.length} registros`);
                    } else if (typeof data === 'object') {
                        addLog(`📋 Retornou objeto com ${Object.keys(data).length} propriedades`);
                    }
                } catch (e) {
                    addLog(`📄 Retornou texto (${text.length} chars)`);
                }
            } else {
                addLog(`❌ ${endpoint}: ${response.status} ${response.statusText}`);
                addLog(`📄 Response: ${text.substring(0, 200)}...`);
            }
            
        } catch (error) {
            addLog(`❌ ${endpoint}: ${error.message}`);
        }
    };

    const testTabelas = async () => {
        addLog('📊 Verificando estrutura das tabelas...');
        
        try {
            const response = await fetch(`${API_BASE}/debug/tabelas`);
            const data = await response.json();
            
            if (response.ok) {
                addLog('✅ Estrutura das tabelas carregada');
                
                for (const [tabela, info] of Object.entries(data)) {
                    addLog(`\n📋 Tabela: ${tabela}`);
                    addLog(`   Colunas: ${info.colunas.length}`);
                    addLog(`   Exemplos: ${info.exemplos ? info.exemplos.length : 0} registros`);
                }
            } else {
                addLog(`❌ Erro ao carregar estrutura: ${data.erro}`);
            }
            
        } catch (error) {
            addLog(`❌ Erro ao verificar tabelas: ${error.message}`);
        }
    };

    const popularDadosTeste = async () => {
        addLog('📥 Populando banco com dados de teste...');
        
        try {
            const response = await fetch(`${API_BASE}/admin/popular-dados-teste`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (response.ok) {
                addLog('✅ Dados de teste inseridos com sucesso');
                addLog(`📝 ${data.mensagem}`);
                
                // Recarregar dados do sistema
                await loadSystemData();
            } else {
                addLog(`❌ Erro ao popular dados: ${data.erro}`);
            }
            
        } catch (error) {
            addLog(`❌ Erro ao popular dados: ${error.message}`);
        }
    };

    const testOpenWeather = async () => {
        addLog('🌤️ Verificando configuração OpenWeather...');
        
        try {
            const response = await fetch(`${API_BASE}/debug/openweather`);
            const data = await response.json();
            
            if (data.configurada) {
                addLog(`✅ API Key configurada: ${data.chave_parcial}`);
                addLog(`📡 Teste API: ${data.teste_api ? '✅ OK' : '❌ Falhou'}`);
                
                if (data.teste_api) {
                    addLog('📊 Dados do clima carregados com sucesso');
                } else {
                    addLog(`❌ Erro na API: ${data.erro}`);
                }
            } else {
                addLog('❌ API Key não configurada');
                addLog(`📝 ${data.erro}`);
            }
            
        } catch (error) {
            addLog(`❌ Erro ao verificar OpenWeather: ${error.message}`);
        }
    };

    const runFullDiagnostic = async () => {
        addLog('🚀 Iniciando diagnóstico completo...');
        updateElement('lastCheck', new Date().toLocaleString());
        
        await testDatabase();
        await testEndpoints();
        await testMunicipies();
        await loadSystemData();
        
        // Identificar problemas
        const issues = [];
        
        if (document.getElementById('dbStatus').textContent !== 'Online') {
            issues.push('🔴 Banco PostgreSQL offline ou com problemas');
        }
        
        if (document.getElementById('apiStatus').textContent === 'Offline') {
            issues.push('🔴 API completamente inacessível');
        } else if (document.getElementById('apiStatus').textContent === 'Parcial') {
            issues.push('🟡 Alguns endpoints da API não funcionam');
        }
        
        const municipiosCount = parseInt(document.getElementById('municipiosCount').textContent) || 0;
        if (municipiosCount === 0) {
            issues.push('🔴 Nenhum município carregado');
        } else if (municipiosCount < 500) {
            issues.push('🟡 Poucos municípios carregados (esperado ~700+)');
        }
        
        const chuvasCount = parseInt(document.getElementById('chuvasCount').textContent) || 0;
        const alagamentosCount = parseInt(document.getElementById('alagamentosCount').textContent) || 0;
        
        if (chuvasCount === 0) {
            issues.push('🔴 Nenhum dado histórico de chuvas');
        }
        
        if (alagamentosCount === 0) {
            issues.push('🔴 Nenhum dado histórico de alagamentos');
        }
        
        // Atualizar lista de problemas
        const issuesList = document.getElementById('issuesList');
        if (issues.length === 0) {
            issuesList.innerHTML = '<li>✅ Nenhum problema crítico identificado</li>';
            document.getElementById('issuesCard').className = 'card success';
        } else {
            issuesList.innerHTML = issues.map(issue => `<li>${issue}</li>`).join('');
            document.getElementById('issuesCard').className = 'card error';
        }
        
        addLog(`🎯 Diagnóstico concluído. ${issues.length} problemas encontrados.`);
    };

    useEffect(() => {
        setTimeout(runFullDiagnostic, 1000);
    }, []);

    return (
        <div className="container">
            <div className="header">
                <h1>🛠️ Debug Dashboard - Sistema THM</h1>
                <p>Diagnóstico completo do sistema de previsão de alagamentos</p>
            </div>

            <div className="grid">
                {/* Status Geral */}
                <div className="card" id="statusCard">
                    <h3><span className="icon">🔍</span> Status Geral do Sistema</h3>
                    <div className="metric">
                        <span>API Status:</span>
                        <span className="status" id="apiStatus">Verificando...</span>
                    </div>
                    <div className="metric">
                        <span>Banco PostgreSQL:</span>
                        <span className="status" id="dbStatus">Verificando...</span>
                    </div>
                    <div className="metric">
                        <span>Endpoints Funcionais:</span>
                        <span className="metric-value" id="endpointsCount">-/-</span>
                    </div>
                    <div className="metric">
                        <span>Última Verificação:</span>
                        <span className="metric-value" id="lastCheck">-</span>
                    </div>
                </div>

                {/* Teste de Conexões */}
                <div className="card">
                    <h3><span className="icon">🔗</span> Teste de Conexões</h3>
                    <button className="test-button" onClick={testDatabase} disabled={loading}>
                        <span id="dbTestIcon">{loading ? '⌛' : '🗄️'}</span> Testar PostgreSQL
                    </button>
                    <button className="test-button" onClick={testEndpoints} disabled={loading}>
                        <span id="endpointsTestIcon">🌐</span> Testar Endpoints
                    </button>
                    <button className="test-button" onClick={testMunicipies} disabled={loading}>
                        <span id="municipiesTestIcon">🏙️</span> Testar Municípios
                    </button>
                    <div className="log-output" id="connectionLogs" style={{ display: logs.length > 0 ? 'block' : 'none' }}>
                        {logs.slice(-20).map((log, index) => (
                            <div key={index}>{log}</div>
                        ))}
                    </div>
                </div>

                {/* Dados do Sistema */}
                <div className="card">
                    <h3><span className="icon">📊</span> Dados do Sistema</h3>
                    <div className="metric">
                        <span>Municípios Carregados:</span>
                        <span className="metric-value" id="municipiosCount">-</span>
                    </div>
                    <div className="metric">
                        <span>Registros de Chuvas:</span>
                        <span className="metric-value" id="chuvasCount">-</span>
                    </div>
                    <div className="metric">
                        <span>Registros de Alagamentos:</span>
                        <span className="metric-value" id="alagamentosCount">-</span>
                    </div>
                    <button className="test-button" onClick={loadSystemData} disabled={loading}>
                        📈 Carregar Dados
                    </button>
                </div>

                {/* Problemas Identificados */}
                <div className="card error" id="issuesCard">
                    <h3><span className="icon">⚠️</span> Problemas Identificados</h3>
                    <ul className="issues-list" id="issuesList">
                        <li>🔍 Verificando problemas...</li>
                    </ul>
                </div>
            </div>

            {/* Testes Detalhados */}
            <div className="card">
                <h3><span className="icon">🧪</span> Testes Detalhados</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px', marginBottom: '20px' }}>
                    <button className="test-button" onClick={() => testSpecificEndpoint('/test-db')} disabled={loading}>Test DB</button>
                    <button className="test-button" onClick={() => testSpecificEndpoint('/debug/historico')} disabled={loading}>Debug Histórico</button>
                    <button className="test-button" onClick={() => testSpecificEndpoint('/municipios')} disabled={loading}>Municípios</button>
                    <button className="test-button" onClick={() => testSpecificEndpoint('/previsao/alertas')} disabled={loading}>Alertas</button>
                    <button className="test-button" onClick={() => testSpecificEndpoint('/historico/chuvas?cidade=Rio de Janeiro&estado=RJ')} disabled={loading}>Histórico Chuvas</button>
                    <button className="test-button" onClick={() => testSpecificEndpoint('/previsao/chuvas?cidade=Rio de Janeiro&estado=RJ')} disabled={loading}>Previsão Chuvas</button>
                    <button className="test-button" onClick={testTabelas} disabled={loading}>Verificar Tabelas</button>
                    <button className="test-button" onClick={popularDadosTeste} disabled={loading}>Popular Dados Teste</button>
                    <button className="test-button" onClick={testOpenWeather} disabled={loading}>Testar OpenWeather</button>
                </div>
                <div className="log-output" id="detailedLogs">
                    {logs.slice(-20).map((log, index) => (
                        <div key={index}>{log}</div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default Debug; 