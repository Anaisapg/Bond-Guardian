import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ActivityIndicator,
  Alert
} from 'react-native';
import { useRouter } from 'expo-router';
import * as WebBrowser from 'expo-web-browser';
import { useAuth } from '../../contexts/AuthContext';

WebBrowser.maybeCompleteAuthSession();

export default function LoginScreen() {
  const router = useRouter();
  const { loginWithTestUser, login } = useAuth();
  const [loading, setLoading] = useState(false);

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.EXPO_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const authUrl = `${backendUrl}/api/auth/google`;
      
      const result = await WebBrowser.openAuthSessionAsync(
        authUrl,
        'bondguardian://auth/callback'
      );

      if (result.type === 'success') {
        const url = result.url;
        const params = new URLSearchParams(url.split('?')[1]);
        
        const token = params.get('token');
        const userId = params.get('user_id');
        const name = params.get('name');
        const email = params.get('email');
        const picture = params.get('picture');

        if (token && userId) {
          const user = {
            user_id: userId,
            email: email || '',
            name: name || 'Usuario',
            picture: picture || undefined,
            settings: {},
            bondy_config: {}
          };
          
          await login(token, user);
          router.replace('/(tabs)');
        } else {
          Alert.alert('Error', 'No se recibió token de autenticación');
        }
      }
    } catch (error) {
      console.error('Error en login:', error);
      Alert.alert('Error', 'No se pudo iniciar sesión con Google');
    } finally {
      setLoading(false);
    }
  };

  const handleTestLogin = async () => {
    try {
      setLoading(true);
      await loginWithTestUser();
      router.replace('/(tabs)');
    } catch (error) {
      console.error('Error test login:', error);
      Alert.alert('Error', 'No se pudo iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.logoContainer}>
          <Text style={styles.logoEmoji}>🤝</Text>
          <Text style={styles.title}>Bond Guardian</Text>
          <Text style={styles.subtitle}>
            Tu compañero inteligente para cuidar relaciones personales
          </Text>
        </View>

        <View style={styles.featuresContainer}>
          <FeatureItem icon="🌟" text="Ritual diario de conexión" />
          <FeatureItem icon="💬" text="Chat con Bondy (IA)" />
          <FeatureItem icon="🔔" text="Recordatorios inteligentes" />
          <FeatureItem icon="📊" text="Estadísticas y rachas" />
        </View>

        <View style={styles.buttonsContainer}>
          <TouchableOpacity
            style={styles.googleButton}
            onPress={handleGoogleLogin}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <>
                <View style={styles.googleIconContainer}>
                  <Text style={styles.googleIcon}>G</Text>
                </View>
                <Text style={styles.googleButtonText}>
                  Continuar con Google
                </Text>
              </>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.testButton}
            onPress={handleTestLogin}
            disabled={loading}
          >
            <Text style={styles.testButtonText}>
              Usar cuenta de prueba
            </Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.termsText}>
          Al continuar, aceptas nuestros términos de servicio
        </Text>
      </View>
    </SafeAreaView>
  );
}

function FeatureItem({ icon, text }: { icon: string; text: string }) {
  return (
    <View style={styles.featureItem}>
      <Text style={styles.featureIcon}>{icon}</Text>
      <Text style={styles.featureText}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  content: {
    flex: 1,
    padding: 24,
    justifyContent: 'space-between',
  },
  logoContainer: {
    alignItems: 'center',
    marginTop: 40,
  },
  logoEmoji: {
    fontSize: 80,
    marginBottom: 16,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#1F2937',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 22,
  },
  featuresContainer: {
    marginVertical: 32,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  featureIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  featureText: {
    fontSize: 16,
    color: '#374151',
    fontWeight: '500',
  },
  buttonsContainer: {
    gap: 12,
  },
  googleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#8B5CF6',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
  },
  googleIconContainer: {
    width: 24,
    height: 24,
    backgroundColor: '#fff',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  googleIcon: {
    fontSize: 16,
    fontWeight: '700',
    color: '#8B5CF6',
  },
  googleButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  testButton: {
    paddingVertical: 16,
    alignItems: 'center',
  },
  testButtonText: {
    color: '#6B7280',
    fontSize: 14,
    fontWeight: '500',
  },
  termsText: {
    fontSize: 12,
    color: '#9CA3AF',
    textAlign: 'center',
    marginTop: 16,
  },
});
