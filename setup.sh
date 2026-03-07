#!/bin/bash

# ===========================================
# Bond Guardian - Setup Script para Mac
# ===========================================

set -e

echo "🤝 Bond Guardian - Configuración Automática"
echo "============================================"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directorio del proyecto
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "📁 Directorio del proyecto: $PROJECT_DIR"
echo ""

# ===========================================
# 1. Verificar requisitos
# ===========================================
echo "🔍 Verificando requisitos..."

# Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python3 no encontrado. Instálalo desde python.org${NC}"
    exit 1
fi

# Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js $NODE_VERSION${NC}"
else
    echo -e "${RED}❌ Node.js no encontrado. Instálalo desde nodejs.org${NC}"
    exit 1
fi

# npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✅ npm $NPM_VERSION${NC}"
else
    echo -e "${RED}❌ npm no encontrado${NC}"
    exit 1
fi

echo ""

# ===========================================
# 2. Arreglar permisos
# ===========================================
echo "🔐 Configurando permisos..."
chmod -R 755 "$PROJECT_DIR"
echo -e "${GREEN}✅ Permisos configurados${NC}"
echo ""

# ===========================================
# 3. Configurar Backend
# ===========================================
echo "🐍 Configurando Backend (Python/FastAPI)..."
cd "$PROJECT_DIR/backend"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "   Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
echo "   Instalando dependencias Python..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Crear .env si no existe
if [ ! -f ".env" ]; then
    echo "   Creando archivo .env..."
    cp .env.example .env 2>/dev/null || cat > .env << 'EOF'
# MongoDB Atlas
MONGODB_URI=mongodb+srv://bondguardian:SlWgFaKePdJramYP@bondguardian.ljvhstb.mongodb.net/bond_guardian?retryWrites=true&w=majority&appName=BondGuardian

# JWT Configuration
JWT_SECRET=bond-guardian-secret-key-2024-production-ready
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=720

# Gemini API
GEMINI_API_KEY=AIzaSyDZsRWKc49X2XznXibEwamljQ-0eN29BHI

# Cloudinary
CLOUDINARY_CLOUD_NAME=bondguardian
CLOUDINARY_API_KEY=673347524733675
CLOUDINARY_API_SECRET=ggUHYinRO_vxyOO-Futs6W7oXGs

# App Configuration
APP_NAME=Bond Guardian
FRONTEND_URL=http://localhost:8081
BACKEND_PORT=8000
DEBUG=true
EOF
fi

echo -e "${GREEN}✅ Backend configurado${NC}"
deactivate
echo ""

# ===========================================
# 4. Configurar Frontend Mobile
# ===========================================
echo "📱 Configurando Frontend (React Native/Expo)..."
cd "$PROJECT_DIR/mobile"

# Limpiar cache si existe
rm -rf node_modules/.cache .expo 2>/dev/null

# Instalar dependencias
echo "   Instalando dependencias npm..."
npm install --silent 2>/dev/null || npm install

# Obtener IP local
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || echo "localhost")

# Crear .env
echo "   Creando archivo .env..."
cat > .env << EOF
EXPO_PUBLIC_BACKEND_URL=http://${LOCAL_IP}:8000
EOF

echo -e "${GREEN}✅ Frontend configurado${NC}"
echo -e "${YELLOW}   Tu IP local: ${LOCAL_IP}${NC}"
echo ""

# ===========================================
# 5. Crear scripts de inicio
# ===========================================
echo "📝 Creando scripts de inicio..."

# Script para iniciar backend
cat > "$PROJECT_DIR/start-backend.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/backend"
source venv/bin/activate
echo "🚀 Iniciando Backend en http://localhost:8000"
echo "📚 Documentación API: http://localhost:8000/docs"
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
EOF
chmod +x "$PROJECT_DIR/start-backend.sh"

# Script para iniciar frontend
cat > "$PROJECT_DIR/start-mobile.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/mobile"
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || echo "localhost")
echo "🚀 Iniciando Expo..."
echo "📱 Escanea el QR con Expo Go en tu móvil"
echo "🌐 Tu IP local: $LOCAL_IP"
REACT_NATIVE_PACKAGER_HOSTNAME=$LOCAL_IP npx expo start --lan
EOF
chmod +x "$PROJECT_DIR/start-mobile.sh"

# Script para iniciar todo
cat > "$PROJECT_DIR/start-all.sh" << 'EOF'
#!/bin/bash
echo "🤝 Iniciando Bond Guardian..."
echo ""

# Iniciar backend en background
cd "$(dirname "$0")"
./start-backend.sh &
BACKEND_PID=$!

# Esperar a que el backend esté listo
sleep 5

# Iniciar frontend
./start-mobile.sh

# Cuando se cierre el frontend, cerrar el backend
kill $BACKEND_PID 2>/dev/null
EOF
chmod +x "$PROJECT_DIR/start-all.sh"

echo -e "${GREEN}✅ Scripts creados${NC}"
echo ""

# ===========================================
# 6. Resumen
# ===========================================
echo "============================================"
echo -e "${GREEN}🎉 ¡Configuración completada!${NC}"
echo "============================================"
echo ""
echo "Para iniciar Bond Guardian:"
echo ""
echo "  1️⃣  Backend solo:"
echo "      ./start-backend.sh"
echo ""
echo "  2️⃣  Mobile solo:"
echo "      ./start-mobile.sh"
echo ""
echo "  3️⃣  Todo junto:"
echo "      ./start-all.sh"
echo ""
echo "============================================"
echo ""
