import React, { useState, useEffect } from 'react';
import { Save, RotateCcw, Eye, EyeOff, AlertCircle, CheckCircle, Copy, Download, Upload, FileText, Plus, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

const PromptsConfig = () => {
  const [prompts, setPrompts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeSection, setActiveSection] = useState('titles');
  const [previewMode, setPreviewMode] = useState(false);
  const [validationResults, setValidationResults] = useState({});
  const [showTemplates, setShowTemplates] = useState(false);
  const [customVariables, setCustomVariables] = useState({});
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  // Seções de prompts
  const sections = {
    titles: {
      name: 'Geração de Títulos',
      icon: '🎯',
      description: 'Prompts para gerar títulos alternativos usando Gemini'
    },
    premises: {
      name: 'Geração de Premissas',
      icon: '💡',
      description: 'Prompts para criar premissas do roteiro'
    },
    scripts: {
      name: 'Geração de Roteiros',
      icon: '📝',
      description: 'Prompts para gerar roteiros completos com capítulos'
    },
    image_prompts: {
      name: 'Prompts de Imagem',
      icon: '🎨',
      description: 'Prompts para gerar descrições de imagens usando IA'
    }
  };

  // Carregar configuração de prompts
  const loadPromptsConfig = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/prompts/config');
      const data = await response.json();
      
      if (data.success) {
        setPrompts(data.data);
      } else {
        toast.error('Erro ao carregar configuração de prompts');
      }
    } catch (error) {
      console.error('Erro ao carregar prompts:', error);
      toast.error('Erro de conexão com o servidor');
    } finally {
      setLoading(false);
    }
  };

  // Salvar configuração de prompts
  const savePromptsConfig = async () => {
    try {
      setSaving(true);
      const response = await fetch('http://localhost:5000/api/prompts/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(prompts),
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast.success('Configuração salva com sucesso!');
        if (data.backup_file) {
          toast.info('Backup criado automaticamente');
        }
      } else {
        toast.error(data.message || 'Erro ao salvar configuração');
      }
    } catch (error) {
      console.error('Erro ao salvar prompts:', error);
      toast.error('Erro de conexão com o servidor');
    } finally {
      setSaving(false);
    }
  };

  // Restaurar configuração padrão
  const resetToDefault = async () => {
    if (!confirm('Tem certeza que deseja restaurar a configuração padrão? Esta ação não pode ser desfeita.')) {
      return;
    }

    try {
      setSaving(true);
      const response = await fetch('http://localhost:5000/api/prompts/config/reset', {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (data.success) {
        setPrompts(data.data);
        toast.success('Configuração restaurada para padrão');
      } else {
        toast.error(data.message || 'Erro ao restaurar configuração');
      }
    } catch (error) {
      console.error('Erro ao restaurar prompts:', error);
      toast.error('Erro de conexão com o servidor');
    } finally {
      setSaving(false);
    }
  };

  // Validação de prompts avançada
  const validatePrompt = async (sectionKey) => {
    if (!prompts[sectionKey]) return;

    const prompt = prompts[sectionKey].prompt;
    const variables = prompts[sectionKey].variables || [];
    const issues = [];
    
    // Validações locais
    if (!prompt || prompt.trim().length === 0) {
      issues.push('Prompt não pode estar vazio');
    }
    
    if (prompt && prompt.length < 10) {
      issues.push('Prompt muito curto (mínimo 10 caracteres)');
    }
    
    if (prompt && prompt.length > 5000) {
      issues.push('Prompt muito longo (máximo 5000 caracteres)');
    }
    
    // Verificar variáveis não utilizadas
    const usedVariables = [];
    const variableRegex = /{([^}]+)}/g;
    let match;
    while ((match = variableRegex.exec(prompt)) !== null) {
      usedVariables.push(match[1]);
    }
    
    const unusedVariables = variables.filter(v => !usedVariables.includes(v));
    if (unusedVariables.length > 0) {
      issues.push(`Variáveis não utilizadas: ${unusedVariables.join(', ')}`);
    }
    
    const undefinedVariables = usedVariables.filter(v => !variables.includes(v));
    if (undefinedVariables.length > 0) {
      issues.push(`Variáveis não definidas: ${undefinedVariables.join(', ')}`);
    }

    try {
      const response = await fetch('http://localhost:5000/api/prompts/config/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          variables: variables
        }),
      });
      
      const data = await response.json();
      
      if (data.success && data.issues) {
        issues.push(...data.issues);
      }
    } catch (error) {
      console.error('Erro ao validar prompt:', error);
      issues.push('Erro na validação do servidor');
    }
    
    const validationResult = {
      valid: issues.length === 0,
      issues,
      usedVariables,
      unusedVariables,
      undefinedVariables
    };
    
    setValidationResults(prev => ({
      ...prev,
      [sectionKey]: validationResult
    }));
  };

  // Preview com substituição de variáveis
  const generatePreview = (prompt, variables = []) => {
    let preview = prompt;
    
    // Substituir variáveis por valores de exemplo
    const exampleValues = {
      topic: 'Inteligência Artificial',
      title: 'Como a IA está Transformando o Mundo',
      premise: 'Exploramos o impacto da inteligência artificial na sociedade moderna',
      chapters: '5',
      duration: '10',
      target_words: '1500',
      tone: 'educacional',
      style: 'storytelling',
      platform: 'YouTube',
      keywords: 'IA, tecnologia, futuro',
      count: '3',
      level: 'intermediário',
      objective: 'ensinar conceitos básicos de IA',
      genre: 'educacional',
      audience: 'jovens adultos',
      topics: 'machine learning, deep learning, aplicações práticas',
      objectives: 'compreender IA, identificar aplicações, avaliar impactos',
      script_content: 'Roteiro sobre inteligência artificial e suas aplicações',
      color_palette: 'azul e branco',
      images_per_chapter: '2',
      resolution: '1920x1080',
      theme: 'tecnologia',
      mood: 'inspirador'
    };
    
    variables.forEach(variable => {
      const value = exampleValues[variable] || `[${variable}]`;
      const regex = new RegExp(`{${variable}}`, 'g');
      preview = preview.replace(regex, value);
    });
    
    return preview;
  };

  // Atualizar prompt com validação em tempo real
  const updatePrompt = (sectionKey, field, value) => {
    setPrompts(prev => ({
      ...prev,
      [sectionKey]: {
        ...prev[sectionKey],
        [field]: value
      }
    }));
    
    // Validação em tempo real para o campo prompt
    if (field === 'prompt') {
      setTimeout(() => {
        validatePrompt(sectionKey);
      }, 500); // Debounce de 500ms
    } else {
      // Limpar validação anterior para outros campos
      setValidationResults(prev => {
        const newResults = { ...prev };
        delete newResults[sectionKey];
        return newResults;
      });
    }
  };

  // Copiar prompt
  const copyPrompt = async (prompt) => {
    try {
      await navigator.clipboard.writeText(prompt);
      toast.success('Prompt copiado para a área de transferência!');
    } catch (error) {
      toast.error('Erro ao copiar prompt');
    }
  };

  // Funções para templates
  const applyTemplate = (templateKey) => {
    const template = promptTemplates[activeSection]?.[templateKey];
    if (template) {
      updatePrompt(activeSection, 'name', template.name);
      updatePrompt(activeSection, 'description', template.description);
      updatePrompt(activeSection, 'prompt', template.prompt);
      updatePrompt(activeSection, 'variables', template.variables);
      setSelectedTemplate(templateKey);
      setShowTemplates(false);
      toast.success(`Template "${template.name}" aplicado!`);
    }
  };

  // Funções para variáveis dinâmicas
  const addCustomVariable = (sectionKey, variableName) => {
    if (variableName && !currentSection?.variables?.includes(variableName)) {
      const newVariables = [...(currentSection?.variables || []), variableName];
      updatePrompt(sectionKey, 'variables', newVariables);
      setCustomVariables(prev => ({ ...prev, [sectionKey]: '' }));
      toast.success(`Variável "${variableName}" adicionada!`);
    }
  };

  const removeVariable = (sectionKey, variableName) => {
    const newVariables = currentSection?.variables?.filter(v => v !== variableName) || [];
    updatePrompt(sectionKey, 'variables', newVariables);
    toast.success(`Variável "${variableName}" removida!`);
  };

  const insertVariableInPrompt = (variableName) => {
    const currentPrompt = currentSection?.prompt || '';
    const variableTag = `{${variableName}}`;
    const newPrompt = currentPrompt + (currentPrompt ? '\n' : '') + variableTag;
    updatePrompt(activeSection, 'prompt', newPrompt);
    toast.success(`Variável "${variableName}" inserida no prompt!`);
  };

  // Exportar configuração
  const exportConfig = () => {
    const dataStr = JSON.stringify(prompts, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `prompts_config_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
    toast.success('Configuração exportada com sucesso');
  };

  // Importar configuração
  const importConfig = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedConfig = JSON.parse(e.target.result);
        setPrompts(importedConfig);
        toast.success('Configuração importada com sucesso');
      } catch (error) {
        toast.error('Erro ao importar configuração: arquivo inválido');
      }
    };
    reader.readAsText(file);
  };

  useEffect(() => {
    loadPromptsConfig();
  }, []);

  // Templates pré-definidos
  const promptTemplates = {
    titles: {
      viral: {
        name: "Títulos Virais",
        description: "Templates para títulos que geram engajamento",
        prompt: "Crie títulos virais e envolventes para o vídeo sobre '{topic}'. Os títulos devem:\n\n1. Despertar curiosidade\n2. Usar números quando apropriado\n3. Incluir palavras de impacto\n4. Ter entre 40-60 caracteres\n5. Ser otimizados para {platform}\n\nTópico: {topic}\nPalavras-chave: {keywords}\nTom: {tone}\n\nGere {count} títulos únicos e criativos.",
        variables: ['topic', 'platform', 'keywords', 'tone', 'count']
      },
      educational: {
        name: "Títulos Educacionais",
        description: "Templates para conteúdo educativo",
        prompt: "Crie títulos educacionais claros e informativos sobre '{topic}'. Os títulos devem:\n\n1. Indicar claramente o que será aprendido\n2. Usar linguagem acessível\n3. Incluir benefícios do aprendizado\n4. Ser específicos e diretos\n\nTópico: {topic}\nNível: {level}\nDuração: {duration}\nObjetivo: {objective}\n\nGere {count} títulos educacionais.",
        variables: ['topic', 'level', 'duration', 'objective', 'count']
      }
    },
    premises: {
      storytelling: {
        name: "Premissa Narrativa",
        description: "Template para histórias envolventes",
        prompt: "Desenvolva uma premissa narrativa envolvente baseada no título '{title}'. A premissa deve:\n\n1. Estabelecer o contexto da história\n2. Apresentar o conflito principal\n3. Criar expectativa no espectador\n4. Ser adequada para {duration} minutos\n\nTítulo: {title}\nGênero: {genre}\nTom: {tone}\nPúblico-alvo: {audience}\n\nCrie uma premissa que mantenha o espectador interessado do início ao fim.",
        variables: ['title', 'duration', 'genre', 'tone', 'audience']
      },
      educational: {
        name: "Premissa Educacional",
        description: "Template para conteúdo didático",
        prompt: "Desenvolva uma premissa educacional estruturada para o título '{title}'. A premissa deve:\n\n1. Definir os objetivos de aprendizado\n2. Estabelecer a metodologia\n3. Indicar os resultados esperados\n4. Ser adequada para {level}\n\nTítulo: {title}\nNível: {level}\nDuração: {duration}\nTópicos principais: {topics}\n\nCrie uma premissa que facilite o aprendizado.",
        variables: ['title', 'level', 'duration', 'topics']
      }
    },
    scripts: {
      storytelling: {
        name: "Roteiro Narrativo",
        description: "Template para roteiros com storytelling",
        prompt: "Crie um roteiro narrativo envolvente baseado na premissa: '{premise}'\n\nEstrutura do roteiro:\n- Introdução (gancho inicial)\n- Desenvolvimento ({chapters} capítulos)\n- Conclusão (call-to-action)\n\nRequisitos:\n- Duração total: {duration} minutos\n- Palavras-alvo: {target_words}\n- Tom: {tone}\n- Incluir transições suaves entre capítulos\n- Manter engajamento constante\n\nPremissa: {premise}\nCapítulos: {chapters}\nEstilo: {style}\n\nDesenvolvimento detalhado por capítulo com timing específico.",
        variables: ['premise', 'chapters', 'duration', 'target_words', 'tone', 'style']
      },
      educational: {
        name: "Roteiro Educacional",
        description: "Template para conteúdo didático estruturado",
        prompt: "Desenvolva um roteiro educacional baseado na premissa: '{premise}'\n\nEstrutura pedagógica:\n- Introdução (apresentação do tópico)\n- Desenvolvimento ({chapters} módulos)\n- Conclusão (resumo e próximos passos)\n\nRequisitos:\n- Duração: {duration} minutos\n- Palavras-alvo: {target_words}\n- Nível: {level}\n- Incluir exemplos práticos\n- Facilitar a compreensão\n\nPremissa: {premise}\nMódulos: {chapters}\nObjetivos: {objectives}\n\nDetalhamento por módulo com exercícios e exemplos.",
        variables: ['premise', 'chapters', 'duration', 'target_words', 'level', 'objectives']
      }
    },
    images: {
      cinematic: {
        name: "Imagens Cinematográficas",
        description: "Template para imagens com estilo cinematográfico",
        prompt: "Gere prompts para imagens cinematográficas baseadas no roteiro: '{script_content}'\n\nEstilo visual:\n- Cinematográfico e profissional\n- Iluminação dramática\n- Composição equilibrada\n- Cores {color_palette}\n\nRequisitos:\n- {images_per_chapter} imagens por capítulo\n- Resolução: {resolution}\n- Estilo consistente\n- Adequado ao tom: {tone}\n\nConteúdo do roteiro: {script_content}\nTom: {tone}\nEstilo: {style}\n\nDescreva cada imagem detalhadamente para IA.",
        variables: ['script_content', 'color_palette', 'images_per_chapter', 'resolution', 'tone', 'style']
      },
      minimalist: {
        name: "Imagens Minimalistas",
        description: "Template para visual clean e moderno",
        prompt: "Crie prompts para imagens minimalistas baseadas no roteiro: '{script_content}'\n\nEstilo visual:\n- Design limpo e moderno\n- Cores neutras e suaves\n- Composição simples\n- Foco no essencial\n\nRequisitos:\n- {images_per_chapter} imagens por capítulo\n- Paleta: {color_palette}\n- Estilo minimalista\n- Alta qualidade visual\n\nConteúdo: {script_content}\nTema: {theme}\nMood: {mood}\n\nDescrições precisas para geração de imagens.",
        variables: ['script_content', 'images_per_chapter', 'color_palette', 'theme', 'mood']
      }
    }
  };

  useEffect(() => {
    if (prompts && prompts[activeSection]) {
      validatePrompt(activeSection);
    }
  }, [activeSection, prompts]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Carregando configuração...</span>
      </div>
    );
  }

  if (!prompts) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-600">Erro ao carregar configuração de prompts</p>
        <button 
          onClick={loadPromptsConfig}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  const currentSection = prompts[activeSection];
  const validation = validationResults[activeSection];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          ⚙️ Configuração de Prompts
        </h1>
        <p className="text-gray-600">
          Configure os prompts usados na automação completa para personalizar a geração de conteúdo
        </p>
      </div>

      {/* Toolbar */}
      <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <button
              onClick={savePromptsConfig}
              disabled={saving}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              <Save className="h-4 w-4" />
              {saving ? 'Salvando...' : 'Salvar'}
            </button>
            
            <button
              onClick={resetToDefault}
              disabled={saving}
              className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50"
            >
              <RotateCcw className="h-4 w-4" />
              Restaurar Padrão
            </button>
            
            <button
              onClick={() => setPreviewMode(!previewMode)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
                previewMode 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <Eye className="h-4 w-4" />
              Preview
            </button>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={exportConfig}
              className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Download className="h-4 w-4" />
              Exportar
            </button>
            
            <label className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 cursor-pointer">
              <Upload className="h-4 w-4" />
              Importar
              <input
                type="file"
                accept=".json"
                onChange={importConfig}
                className="hidden"
              />
            </label>
            
            <button
              onClick={() => setShowTemplates(!showTemplates)}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              <FileText className="h-4 w-4" />
              Templates
            </button>
          </div>
        </div>
      </div>

      {/* Modal de Templates */}
      {showTemplates && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold text-gray-900">Templates de Prompts</h3>
                <button
                  onClick={() => setShowTemplates(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              <p className="text-gray-600 mt-2">
                Escolha um template para a seção "{currentSection?.name}"
              </p>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {promptTemplates[activeSection] && Object.entries(promptTemplates[activeSection]).map(([key, template]) => (
                  <div
                    key={key}
                    className="border rounded-lg p-4 hover:border-purple-300 cursor-pointer transition-colors"
                    onClick={() => applyTemplate(key)}
                  >
                    <h4 className="font-semibold text-gray-900 mb-2">{template.name}</h4>
                    <p className="text-gray-600 text-sm mb-3">{template.description}</p>
                    
                    <div className="mb-3">
                      <h5 className="text-xs font-medium text-gray-700 mb-1">Variáveis incluídas:</h5>
                      <div className="flex flex-wrap gap-1">
                        {template.variables.map((variable, index) => (
                          <span 
                            key={index}
                            className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-mono"
                          >
                            {`{${variable}}`}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 rounded p-2">
                      <p className="text-xs text-gray-600 line-clamp-3">
                        {template.prompt.substring(0, 150)}...
                      </p>
                    </div>
                    
                    <button className="w-full mt-3 px-3 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm">
                      Aplicar Template
                    </button>
                  </div>
                ))}
              </div>
              
              {(!promptTemplates[activeSection] || Object.keys(promptTemplates[activeSection]).length === 0) && (
                <div className="text-center py-8 text-gray-500">
                  <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>Nenhum template disponível para esta seção</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar - Seções */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <h3 className="font-semibold text-gray-900 mb-4">Seções</h3>
            <div className="space-y-2">
              {Object.entries(sections).map(([key, section]) => (
                <button
                  key={key}
                  onClick={() => setActiveSection(key)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    activeSection === key
                      ? 'bg-blue-50 border-blue-200 text-blue-900'
                      : 'hover:bg-gray-50 border-transparent'
                  } border`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{section.icon}</span>
                    <div>
                      <div className="font-medium text-sm">{section.name}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {section.description}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Editor Principal */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-sm border">
            {/* Header da Seção */}
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                    <span className="text-2xl">{sections[activeSection]?.icon}</span>
                    {currentSection?.name}
                  </h2>
                  <p className="text-gray-600 mt-1">{currentSection?.description}</p>
                </div>
                
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => copyPrompt(currentSection?.prompt)}
                    className="flex items-center gap-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                  >
                    <Copy className="h-4 w-4" />
                    Copiar
                  </button>
                  
                  {validation && (
                    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
                      validation.valid 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {validation.valid ? (
                        <CheckCircle className="h-4 w-4" />
                      ) : (
                        <AlertCircle className="h-4 w-4" />
                      )}
                      {validation.valid ? 'Válido' : 'Inválido'}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Conteúdo da Seção */}
            <div className="p-6">
              {previewMode ? (
                /* Modo Preview */
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">Preview do Prompt</h4>
                    <div className="whitespace-pre-wrap text-sm text-gray-700 font-mono bg-white p-4 rounded border">
                      {generatePreview(currentSection?.prompt || '', currentSection?.variables || [])}
                    </div>
                  </div>
                  
                  {currentSection?.variables && currentSection.variables.length > 0 && (
                    <div className="bg-blue-50 rounded-lg p-4">
                      <h4 className="font-medium text-blue-900 mb-2">Variáveis Disponíveis</h4>
                      <div className="flex flex-wrap gap-2">
                        {currentSection.variables.map((variable, index) => (
                          <span 
                            key={index}
                            className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm font-mono"
                          >
                            {`{${variable}}`}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                /* Modo Edição */
                <div className="space-y-6">
                  {/* Nome da Seção */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nome da Seção
                    </label>
                    <input
                      type="text"
                      value={currentSection?.name || ''}
                      onChange={(e) => updatePrompt(activeSection, 'name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Nome da seção"
                    />
                  </div>

                  {/* Descrição */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Descrição
                    </label>
                    <input
                      type="text"
                      value={currentSection?.description || ''}
                      onChange={(e) => updatePrompt(activeSection, 'description', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Descrição da seção"
                    />
                  </div>

                  {/* Editor de Prompt */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Prompt
                    </label>
                    <div className="relative">
                      <textarea
                        value={currentSection?.prompt || ''}
                        onChange={(e) => updatePrompt(activeSection, 'prompt', e.target.value)}
                        rows={15}
                        className={`w-full px-3 py-2 border rounded-lg font-mono text-sm focus:ring-2 focus:border-blue-500 ${
                          validationResults[activeSection]?.valid === false 
                            ? 'border-red-300 focus:ring-red-500' 
                            : validationResults[activeSection]?.valid === true
                            ? 'border-green-300 focus:ring-green-500'
                            : 'border-gray-300 focus:ring-blue-500'
                        }`}
                        placeholder="Digite o prompt aqui..."
                      />
                      
                      {/* Indicador de status de validação */}
                      {validationResults[activeSection] && (
                        <div className="absolute top-2 right-2">
                          {validationResults[activeSection].valid ? (
                            <div className="flex items-center text-green-600">
                              <CheckCircle className="w-4 h-4" />
                              <span className="ml-1 text-xs">Válido</span>
                            </div>
                          ) : (
                            <div className="flex items-center text-red-600">
                              <AlertCircle className="w-4 h-4" />
                              <span className="ml-1 text-xs">Inválido</span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    
                    {/* Estatísticas do prompt */}
                     <div className="mt-2 flex justify-between items-center text-xs text-gray-500">
                       <div className="flex space-x-4">
                         <span>Caracteres: {(currentSection?.prompt || '').length}/5000</span>
                         <span>Palavras: {(currentSection?.prompt || '').split(/\s+/).filter(word => word.length > 0).length}</span>
                         <span>Linhas: {(currentSection?.prompt || '').split('\n').length}</span>
                         {validationResults[activeSection]?.usedVariables && (
                           <span>Variáveis: {validationResults[activeSection].usedVariables.length}</span>
                         )}
                       </div>
                       <div className="flex items-center space-x-2">
                         <button
                           onClick={() => validatePrompt(activeSection)}
                           className="text-blue-600 hover:text-blue-800"
                           title="Validar prompt"
                         >
                           Validar
                         </button>
                       </div>
                     </div>
                     
                     {/* Exibir problemas de validação */}
                     {validationResults[activeSection]?.issues?.length > 0 && (
                       <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                         <h4 className="text-sm font-medium text-red-800 mb-1">Problemas encontrados:</h4>
                         <ul className="text-sm text-red-700 list-disc list-inside">
                           {validationResults[activeSection].issues.map((issue, index) => (
                             <li key={index}>{issue}</li>
                           ))}
                         </ul>
                       </div>
                     )}
                     
                     {/* Exibir informações de validação positivas */}
                     {validationResults[activeSection]?.valid && (
                       <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                         <div className="flex items-center text-green-800">
                           <CheckCircle className="w-4 h-4 mr-2" />
                           <span className="text-sm font-medium">Prompt válido!</span>
                         </div>
                         {validationResults[activeSection].usedVariables?.length > 0 && (
                           <div className="mt-1 text-sm text-green-700">
                             Variáveis utilizadas: {validationResults[activeSection].usedVariables.join(', ')}
                           </div>
                         )}
                       </div>
                     )}
                  </div>

                  {/* Gerenciamento de Variáveis */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Variáveis Dinâmicas
                    </label>
                    
                    {/* Variáveis Existentes */}
                    {currentSection?.variables && currentSection.variables.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-medium text-gray-600 mb-2">Variáveis Ativas:</h4>
                        <div className="flex flex-wrap gap-2">
                          {currentSection.variables.map((variable, index) => (
                            <div 
                              key={index}
                              className="flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                            >
                              <span className="font-mono">{`{${variable}}`}</span>
                              <button
                                onClick={() => insertVariableInPrompt(variable)}
                                className="text-blue-600 hover:text-blue-800"
                                title="Inserir no prompt"
                              >
                                <Plus className="h-3 w-3" />
                              </button>
                              <button
                                onClick={() => removeVariable(activeSection, variable)}
                                className="text-red-600 hover:text-red-800"
                                title="Remover variável"
                              >
                                <Trash2 className="h-3 w-3" />
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Adicionar Nova Variável */}
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={customVariables[activeSection] || ''}
                        onChange={(e) => setCustomVariables(prev => ({ ...prev, [activeSection]: e.target.value }))}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            addCustomVariable(activeSection, customVariables[activeSection]);
                          }
                        }}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Nome da nova variável (ex: topic, duration, style)"
                      />
                      <button
                        onClick={() => addCustomVariable(activeSection, customVariables[activeSection])}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                      >
                        <Plus className="h-4 w-4" />
                        Adicionar
                      </button>
                    </div>
                    
                    <p className="text-xs text-gray-500 mt-2">
                      Use variáveis como {`{variable_name}`} no prompt. Clique em + para inserir no prompt ou 🗑️ para remover.
                    </p>
                  </div>

                  {/* Validação */}
                  {validation && !validation.valid && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <h4 className="font-medium text-red-900 mb-2 flex items-center gap-2">
                        <AlertCircle className="h-4 w-4" />
                        Problemas Encontrados
                      </h4>
                      <ul className="text-sm text-red-700 space-y-1">
                        {validation.issues.map((issue, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <span className="text-red-500 mt-0.5">•</span>
                            {issue}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PromptsConfig;