# Bond Guardian 🤝

Tu compañero inteligente para cuidar relaciones personales. Bond Guardian te ayuda a mantener el contacto con las personas importantes en tu vida mediante un "ritual diario" y un asistente de IA llamado Bondy.

## 📱 Características

- **Ritual Diario**: Cada día, recibe una sugerencia de persona para contactar basada en un algoritmo inteligente
- **Persona del Día**: Algoritmo que prioriza cumpleaños, recordatorios pendientes y contactos descuidados
- **Registro de Interacciones**: Guarda un resumen de cada conversación importante
- **Chat con Bondy**: Asistente de IA para ayudarte a gestionar tus relaciones
- **Recordatorios Personalizados**: Nunca olvides fechas o compromisos importantes
- **Estadísticas y Racha**: Gamificación para mantener el hábito

## 🏗️ Arquitectura

```
bond-guardian/
├── backend/          # FastAPI + Python
│   ├── app/
│   │   ├── core/     # Configuración, DB, seguridad
│   │   ├── models/   # Modelos de datos (Beanie/MongoDB)
│   │   ├── routers/  # Endpoints de la API
│   │   └── services/ # Servicios (Gemini AI)
│   └── server.py     # Entry point
└── mobile/           # React Native + Expo
    ├── app/          # Pantallas (Expo Router)
    ├── components/   # Componentes reutilizables
    ├── contexts/     # Estado global (Auth)
    ├── hooks/        # Custom hooks
    ├── services/     # API client
    └── types/        # TypeScript types
```

## 🚀 Configuración Rápida

### 1. Requisitos Previos

- Python 3.10+
- Node.js 18+
- MongoDB Atlas (gratuito) o MongoDB local
- (Opcional) Gemini API key para IA
- (Opcional) Cloudinary para fotos

### 2. Configurar MongoDB Atlas (Gratuito)

1. Ve a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Crea una cuenta gratuita
3. Crea un cluster gratuito (M0 Sandbox)
4. En "Database Access", crea un usuario con contraseña
5. En "Network Access", añade tu IP (o 0.0.0.0/0 para desarrollo)
6. En "Connect", obtén tu connection string:
   ```
   mongodb+srv://usuario:contraseña@cluster.mongodb.net/bond_guardian
   ```

### 3. Backend Setup

```bash
cd backend

# Crear archivo .env con tu configuración
cp .env.example .env

# Editar .env con tu MongoDB URI
nano .env  # o usa tu editor preferido

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

El servidor estará en: http://localhost:8000
Documentación API: http://localhost:8000/docs

### 4. Frontend Setup (React Native)

```bash
cd mobile

# Instalar dependencias
npm install
# o
bun install

# Configurar variables de entorno
cp .env.example .env
# Editar EXPO_PUBLIC_BACKEND_URL

# Ejecutar con Expo
npx expo start
```

Escanea el código QR con Expo Go en tu móvil.

## 🔑 Variables de Entorno

### Backend (.env)

| Variable | Descripción | Requerido |
|----------|-------------|-----------|
| MONGODB_URI | Connection string de MongoDB | ✅ |
| JWT_SECRET | Clave secreta para tokens | ✅ |
| GEMINI_API_KEY | API key de Google Gemini | ❌ |
| GOOGLE_CLIENT_ID | Para OAuth con Google | ❌ |
| CLOUDINARY_* | Para subir fotos | ❌ |

### Frontend (.env)

| Variable | Descripción |
|----------|-------------|
| EXPO_PUBLIC_BACKEND_URL | URL del backend |
| EXPO_PUBLIC_GOOGLE_CLIENT_ID | Para login con Google |

## 📚 API Endpoints

### Autenticación
- `POST /api/auth/session-data` - Crear sesión (desarrollo)
- `POST /api/auth/dev/create-test-user` - Crear usuario de prueba
- `GET /api/auth/me` - Obtener usuario actual

### Contactos
- `GET /api/contacts` - Listar contactos
- `POST /api/contacts` - Crear contacto
- `GET /api/contacts/{id}` - Obtener contacto
- `PUT /api/contacts/{id}` - Actualizar contacto
- `DELETE /api/contacts/{id}` - Eliminar contacto

### Interacciones
- `GET /api/interactions` - Listar interacciones (timeline)
- `POST /api/interactions` - Crear interacción
- `PUT /api/interactions/{id}` - Actualizar
- `DELETE /api/interactions/{id}` - Eliminar

### Ritual
- `GET /api/ritual/person-of-day` - Persona del día
- `GET /api/ritual/stats` - Estadísticas
- `POST /api/ritual/complete` - Completar ritual
- `GET /api/ritual/insights` - Insights de IA

### Chat (Bondy)
- `POST /api/chat/message` - Enviar mensaje
- `GET /api/chat/history` - Historial
- `DELETE /api/chat/history` - Borrar historial

## 🎨 Paleta de Colores

- Primary: `#8B5CF6` (purple-600)
- Success: `#10B981` (green-500)
- Warning: `#F59E0B` (amber-500)
- Error: `#EF4444` (red-500)
- Background: `#F8FAFC` (slate-50)

## 🤖 Obtener API Keys

### Google Gemini (IA)
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una API key
3. Añádela a `GEMINI_API_KEY` en tu .env

### Google OAuth
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto
3. Habilita "Google+ API"
4. Crea credenciales OAuth 2.0
5. Añade los redirect URIs de Expo

### Cloudinary (Fotos)
1. Crea cuenta en [Cloudinary](https://cloudinary.com/)
2. Ve al Dashboard
3. Copia Cloud Name, API Key y API Secret

## 📱 Despliegue

### Backend (Render.com)
1. Conecta tu repo de GitHub
2. Crea un Web Service
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Añade las variables de entorno

### Mobile (EAS Build)
```bash
npm install -g eas-cli
eas login
eas build --platform all
```

## 📄 Licencia

MIT License - Usa este proyecto libremente.

---

Desarrollado con ❤️ para ayudarte a cuidar tus relaciones
