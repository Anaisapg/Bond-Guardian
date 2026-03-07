# Bond Guardian - Guía de Solución de Problemas

## Configuración Actual (SDK 51 - Estable)

Este proyecto usa **Expo SDK 51** que es una versión estable y probada.

### Versiones Compatibles

| Package | Versión |
|---------|---------|
| expo | ~51.0.28 |
| react-native | 0.74.5 |
| expo-router | ~3.5.23 |
| react | 18.2.0 |

---

## Comandos de Build

### Desarrollo Local
```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start

# Iniciar con cache limpio
npx expo start -c
```

### Build con EAS

```bash
# Preview (APK para testing)
eas build --platform android --profile preview

# Producción (AAB para Play Store)
eas build --platform android --profile production

# Desarrollo (con cliente de desarrollo)
eas build --platform android --profile development
```

---

## Problemas Comunes y Soluciones

### Error: "expo-doctor" falla
```bash
# Verificar versiones
npx expo install --check

# Fix automático
npx expo install --fix
```

### Error: Dependencias incompatibles
```bash
# Limpiar e instalar
rm -rf node_modules
rm package-lock.json
npm install
```

### Error: Build fallido en EAS
```bash
# Ver logs detallados
eas build:view --platform android

# Build local para debug
npx expo prebuild --clean
cd android
./gradlew assembleDebug --info --stacktrace
```

---

## Configuración del Backend

La API está configurada en `services/api.ts`:

```typescript
const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL || 'http://localhost:8000';
```

### URLs del Backend
- **Local**: `http://localhost:8000`
- **Producción**: `https://bond-guardian-1.onrender.com`

### Verificar Backend
```bash
curl https://bond-guardian-1.onrender.com/health
```

---

## Assets Requeridos

| Archivo | Tamaño | Uso |
|---------|--------|-----|
| `icon.png` | 1024x1024 | App Store / Play Store |
| `adaptive-icon.png` | 1024x1024 | Android adaptive icon |
| `splash-icon.png` | 288x288+ | Splash screen |
| `favicon.png` | 48x48 | Web favicon |

---

## Rebuild Completo

```bash
# 1. Limpiar todo
rm -rf node_modules .expo android ios
rm package-lock.json

# 2. Instalar
npm install

# 3. Verificar
npx expo install --check

# 4. Build
eas build --platform android --profile preview
```

---

## Soporte

- [Expo Forums](https://forums.expo.dev/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/expo)
- [GitHub Issues](https://github.com/expo/expo/issues)
