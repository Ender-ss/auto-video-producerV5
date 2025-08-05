/**
 * 🖼️ Image Generation Step Component
 * 
 * Componente para a etapa de geração de imagens no pipeline
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Image, Loader2, AlertCircle, CheckCircle } from 'lucide-react';

const ImageGenerationStep = ({ script, onComplete, onError }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [generatedImages, setGeneratedImages] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const generateImages = async () => {
      if (!script) return;

      setIsLoading(true);
      setError(null);

      try {
        // Lógica para chamar o backend e gerar as imagens
        // Esta é uma simulação, substitua pela chamada de API real
        console.log("🖼️ Iniciando geração de imagens para o roteiro...");
        await new Promise(resolve => setTimeout(resolve, 3000)); // Simula a chamada de API

        const mockImages = [
          '/api/placeholder/image/1',
          '/api/placeholder/image/2',
          '/api/placeholder/image/3',
          '/api/placeholder/image/4',
        ];

        setGeneratedImages(mockImages);
        console.log("✅ Imagens geradas com sucesso:", mockImages);

        if (onComplete) {
          onComplete(mockImages);
        }

      } catch (err) {
        console.error("❌ Erro ao gerar imagens:", err);
        setError("Falha na geração de imagens. Verifique o backend.");
        if (onError) {
          onError(err);
        }
      } finally {
        setIsLoading(false);
      }
    };

    generateImages();
  }, [script, onComplete, onError]);

  return (
    <div className="p-4 bg-gray-800 rounded-lg">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
        <Image size={20} className="mr-2 text-pink-400" />
        Etapa: Geração de Imagens
      </h3>

      {isLoading && (
        <div className="flex items-center text-yellow-400">
          <Loader2 size={18} className="animate-spin mr-2" />
          <span>Gerando imagens a partir do roteiro...</span>
        </div>
      )}

      {error && (
        <div className="flex items-center text-red-400">
          <AlertCircle size={18} className="mr-2" />
          <span>{error}</span>
        </div>
      )}

      {generatedImages.length > 0 && (
        <div>
          <div className="flex items-center text-green-400 mb-4">
            <CheckCircle size={18} className="mr-2" />
            <span>Imagens geradas com sucesso!</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {generatedImages.map((img, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
              >
                <img src={img} alt={`Generated ${index + 1}`} className="w-full h-auto rounded-md" />
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageGenerationStep;
