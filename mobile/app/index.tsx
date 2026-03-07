import { useEffect } from 'react';
import { Redirect } from 'expo-router';
import { View } from 'react-native';
import { useAuth } from '@/contexts/AuthContext';
import { LoadingSpinner } from '@/components';

export default function Index() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F8FAFC' }}>
        <LoadingSpinner message="Cargando..." fullScreen />
      </View>
    );
  }

  if (isAuthenticated) {
    return <Redirect href="/(tabs)/ritual" />;
  }

  return <Redirect href="/(auth)/login" />;
}
