# Bond Guardian - Guía de Despliegue a Producción

Esta guía te permitirá desplegar Bond Guardian directamente a producción sin necesidad de ejecutarlo localmente.

---

## 📋 Resumen de Pasos

1. **Subir el código a GitHub**
2. **Desplegar Backend en Render**
3. **Configurar EAS y construir la app móvil**

---

## Paso 1: Subir a GitHub

### Opción A: Usando GitHub CLI (Recomendado)

```bash
# Inicializar git si no existe
cd bond-guardian
git init

# Crear .gitignore adecuado (ya existe)
# Agregar archivos
git add .
git commit -m "Initial commit - Bond Guardian"

# Crear repo en GitHub
gh repo create bond-guardian --private --source=. --remote=origin

# Subir
git push -u origin main
```

### Opción B: Manualmente

1. Ve a https://github.com/new
2. Crea un repositorio llamado `bond-guardian` (privado recomendado)
3. No inicialices con README ni .gitignore
4. Sigue las instrucciones que GitHub te muestra para "push an existing repository"

---

## Paso 2: Desplegar Backend en Render

### 2.1 Crear cuenta en Render

1. Ve a https://render.com
2. Regístrate con GitHub para vincular automáticamente tus repos

### 2.2 Crear Web Service

1. Ve a https://dashboard.render.com/select-repo?type=web
2. Conecta tu repositorio de GitHub
3. Selecciona el repo `bond-guardian`

### 2.3 Configurar el servicio

| Campo | Valor |
|-------|-------|
| **Name** | `bond-guardian-api` |
| **Root Directory** | `backend` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn server:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

### 2.4 Configurar Variables de Entorno

En la sección "Environment Variables", añade:

| Variable | Valor | Notas |
|----------|-------|-------|
| `MONGODB_URI` | `mongodb+srv://bondguardian:SlWgFaKePdJramYP@bondguardian.ljvhstb.mongodb.net/bond_guardian?retryWrites=true&w=majority&appName=BondGuardian` | Tu MongoDB Atlas URI |
| `JWT_SECRET` | *(Auto-generate)* | Haz clic en "Generate" |
| `JWT_ALGORITHM` | `HS256` | |
| `JWT_EXPIRATION_HOURS` | `720` | |
| `GEMINI_API_KEY` | `AIzaSyDZsRWKc49X2XznXibEwamljQ-0eN29BHI` | Tu API key |
| `CLOUDINARY_CLOUD_NAME` | `bondguardian` | |
| `CLOUDINARY_API_KEY` | `673347524733675` | |
| `CLOUDINARY_API_SECRET` | `ggUHYinRO_vxyOO-Futs6W7oXGs` | |
| `DEBUG` | `false` | |
| `APP_NAME` | `Bond Guardian` | |

### 2.5 Desplegar

1. Haz clic en "Create Web Service"
2. Espera 5-10 minutos para el primer despliegue
3. Tu backend estará en: `https://bond-guardian-api.onrender.com`

### 2.6 Verificar el despliegue

Visita estas URLs para verificar:
- **Health check**: https://bond-guardian-api.onrender.com/health
- **API Docs**: https://bond-guardian-api.onrender.com/docs

Deberías ver:
```json
{
  "status": "healthy",
  "database": "connected",
  "mock_mode": false
}
```

---

## Paso 3: Desplegar App Móvil con EAS

### 3.1 Instalar EAS CLI

```bash
npm install -g eas-cli
```

### 3.2 Iniciar sesión en Expo

```bash
cd mobile
eas login
```

Si no tienes cuenta, créala en https://expo.dev/signup

### 3.3 Configurar el proyecto

```bash
# Esto creará/actualizará tu proyecto en Expo
eas build:configure
```

Cuando pregunte por el proyecto ID, selecciona "Create a new project".

### 3.4 Actualizar la URL del backend

Edita `mobile/eas.json` y reemplaza la URL con tu URL de Render real:

```json
{
  "build": {
    "preview": {
      "env": {
        "EXPO_PUBLIC_BACKEND_URL": "https://TU-SERVICIO.onrender.com"
      }
    },
    "production": {
      "env": {
        "EXPO_PUBLIC_BACKEND_URL": "https://TU-SERVICIO.onrender.com"
      }
    }
  }
}
```

### 3.5 Construir APK para Android (Preview)

```bash
# Construir APK para testing (descargable directamente)
eas build --platform android --profile preview
```

Esto tomará 10-20 minutos. Al finalizar, recibirás un enlace para descargar el APK.

### 3.6 Construir para iOS (Preview)

Para iOS necesitas una cuenta de Apple Developer ($99/año) o usar Expo Go:

```bash
# Si tienes Apple Developer account
eas build --platform ios --profile preview

# Si no, puedes usar la app Expo Go para testing
# Solo necesitas el APK de Android para demostrar la app
```

### 3.7 Alternativa: Usar Expo Go (Sin construir)

Si solo quieres probar la app sin crear builds:

1. Instala Expo Go en tu teléfono (iOS/Android)
2. Ejecuta en tu máquina local (si logras resolver el error EMFILE):
   ```bash
   cd mobile
   npx expo start --tunnel
   ```
3. Escanea el QR con Expo Go

Pero dado tu problema de EMFILE, recomiendo usar EAS Build.

---

## Paso 4: Alternativa - Web App con Expo Web

Si prefieres tener una versión web accesible:

### 4.1 Configurar para web

El proyecto ya está configurado para web. Solo necesitas desplegarlo.

### 4.2 Construir para web

```bash
cd mobile
npx expo export --platform web
```

Esto genera una carpeta `dist/` que puedes desplegar en cualquier hosting estático.

### 4.3 Desplegar en Netlify

1. Ve a https://app.netlify.com/drop
2. Arrastra la carpeta `dist/` generada
3. ¡Listo! Tu app web estará en una URL de Netlify

---

## 🔧 Troubleshooting

### El backend no conecta a MongoDB

1. Verifica que la IP `0.0.0.0/0` esté permitida en MongoDB Atlas:
   - Ve a tu cluster → Network Access → Add IP Address → Allow Access from Anywhere

### La app no conecta al backend

1. Verifica que la URL en `eas.json` sea correcta
2. Asegúrate de que el backend esté corriendo (visita /health)
3. Los servicios gratuitos de Render se "duermen" después de inactividad - la primera request puede tardar 30-60 segundos

### Error en EAS Build

1. Verifica que `app.json` tenga configuración válida
2. Asegúrate de haber hecho `eas login`
3. Revisa los logs del build en https://expo.dev

---

## 📱 URLs Finales

Después del despliegue tendrás:

| Servicio | URL |
|----------|-----|
| **Backend API** | https://bond-guardian-api.onrender.com |
| **API Docs** | https://bond-guardian-api.onrender.com/docs |
| **APK Android** | (enlace de EAS Build) |
| **iOS** | (enlace de EAS Build o TestFlight) |
| **Web App** | (opcional, si despliegas en Netlify) |

---

## 🎉 ¡Listo!

Una vez completados estos pasos, tendrás Bond Guardian funcionando en producción sin necesidad de ejecutar nada localmente.

Para soporte adicional:
- Render Docs: https://render.com/docs
- EAS Docs: https://docs.expo.dev/build/introduction/
- Expo Web: https://docs.expo.dev/distribution/publishing-websites/
