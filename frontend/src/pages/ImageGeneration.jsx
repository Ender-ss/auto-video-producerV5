import React, { useState, useEffect } from 'react';

const ImageGeneration = () => {
    const [script, setScript] = useState('');
    const [style, setStyle] = useState('cinematic');
    const [images, setImages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [apiKey, setApiKey] = useState('');

    useEffect(() => {
        const fetchApiKey = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/settings/api-keys/together');
                const data = await response.json();
                if (data.success) {
                    setApiKey(data.api_key);
                } else {
                    setError('Chave da API Together.ai não encontrada. Por favor, configure-a nas Configurações.');
                }
            } catch (err) {
                setError('Não foi possível buscar a chave da API. Verifique a conexão com o backend.');
            }
        };

        fetchApiKey();
    }, []);

    const handleGenerateImages = async () => {
        if (!apiKey) {
            setError('A chave da API do Together.ai não está configurada.');
            return;
        }

        setIsLoading(true);
        setError(null);
        setImages([]);

        try {
            const response = await fetch('http://localhost:5000/api/images/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    script: script,
                    api_key: apiKey,
                    style: style 
                }),
            });

            const data = await response.json();

            if (data.success) {
                setImages(data.image_urls);
            } else {
                setError(data.error);
            }
        } catch (err) {
            setError('Falha ao conectar com o servidor. Verifique se o backend está rodando.');
        }

        setIsLoading(false);
    };

    return (
        <div className="p-6 bg-gray-900 text-white min-h-screen">
            <h1 className="text-3xl font-bold mb-6">Geração de Imagens com IA</h1>

            <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
                <div className="mb-4">
                    <label htmlFor="script" className="block text-lg font-medium mb-2">Roteiro do Vídeo</label>
                    <textarea
                        id="script"
                        rows="10"
                        className="w-full p-3 bg-gray-700 rounded-md border border-gray-600 focus:ring-2 focus:ring-blue-500"
                        placeholder="Cole o roteiro gerado aqui..."
                        value={script}
                        onChange={(e) => setScript(e.target.value)}
                    />
                </div>

                <div className="mb-6">
                    <label htmlFor="style" className="block text-lg font-medium mb-2">Estilo da Imagem</label>
                    <select 
                        id="style"
                        className="w-full p-3 bg-gray-700 rounded-md border border-gray-600 focus:ring-2 focus:ring-blue-500"
                        value={style}
                        onChange={(e) => setStyle(e.target.value)}
                    >
                        <option value="cinematic, high detail, 4k">Cinemático</option>
                        <option value="photorealistic, sharp focus, f/1.8">Fotorealista</option>
                        <option value="fantasy, epic, detailed, vibrant colors">Fantasia</option>
                        <option value="documentary, natural lighting, realistic">Documental</option>
                        <option value="anime, ghibli style, detailed background">Anime (Ghibli)</option>
                    </select>
                </div>

                <button 
                    onClick={handleGenerateImages}
                    disabled={isLoading || !script || !apiKey}
                    className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 rounded-md text-lg font-semibold disabled:bg-gray-500 disabled:cursor-not-allowed transition-colors"
                >
                    {isLoading ? 'Gerando Imagens...' : 'Gerar Imagens'}
                </button>

                {error && <p className="text-red-400 mt-4">{error}</p>}
            </div>

            {images.length > 0 && (
                <div className="mt-8">
                    <h2 className="text-2xl font-bold mb-4">Imagens Geradas</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        {images.map((url, index) => (
                            <div key={index} className="bg-gray-800 rounded-lg overflow-hidden shadow-lg">
                                <img src={`http://localhost:5000${url}`} alt={`Imagem gerada ${index + 1}`} className="w-full h-auto object-cover" />
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ImageGeneration;