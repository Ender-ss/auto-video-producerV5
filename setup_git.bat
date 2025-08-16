@echo off
echo Inicializando repositorio Git...
git init

echo Configurando usuario Git (substitua pelos seus dados):
echo git config user.name "Seu Nome"
echo git config user.email "seu.email@exemplo.com"

echo Adicionando arquivos ao Git...
git add .

echo Fazendo commit inicial...
git commit -m "Initial commit: Auto Video Producer project"

echo.
echo ========================================
echo PROXIMOS PASSOS:
echo ========================================
echo 1. Configure seu usuario Git executando:
echo    git config user.name "Seu Nome"
echo    git config user.email "seu.email@exemplo.com"
echo.
echo 2. Crie um repositorio no GitHub:
echo    - Va para https://github.com/new
echo    - Nome: auto-video-producer
echo    - Deixe como publico ou privado conforme preferir
echo    - NAO inicialize com README (ja temos arquivos)
echo.
echo 3. Adicione o remote origin (substit