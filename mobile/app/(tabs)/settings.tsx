import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  TextInput,
  Modal,
} from 'react-native';
import { router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '@/contexts/AuthContext';
import * as api from '@/services/api';
import { Avatar, Button, Card } from '@/components';

export default function SettingsScreen() {
  const { user, logout, refreshUser } = useAuth();
  const [showBondyModal, setShowBondyModal] = useState(false);
  const [bondyName, setBondyName] = useState(user?.bondy_config.name || 'Bondy');
  const [saving, setSaving] = useState(false);

  const handleLogout = () => {
    Alert.alert(
      'Cerrar sesión',
      '¿Seguro que quieres cerrar sesión?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Cerrar sesión',
          style: 'destructive',
          onPress: async () => {
            await logout();
            router.replace('/(auth)/login');
          },
        },
      ]
    );
  };

  const handleUpdateNotifications = async (enabled: boolean) => {
    try {
      await api.updateSettings({
        settings: { notifications_enabled: enabled },
      });
      await refreshUser();
    } catch {
      Alert.alert('Error', 'No se pudo actualizar la configuración');
    }
  };

  const handleUpdateCoachingLevel = async (level: string) => {
    try {
      await api.updateSettings({
        settings: { coaching_level: level as 'activo' | 'moderado' | 'sutil' },
        bondy_config: { coaching_level: level },
      });
      await refreshUser();
    } catch {
      Alert.alert('Error', 'No se pudo actualizar el nivel de coaching');
    }
  };

  const handleSaveBondyName = async () => {
    if (!bondyName.trim()) {
      Alert.alert('Error', 'El nombre no puede estar vacío');
      return;
    }

    try {
      setSaving(true);
      await api.updateSettings({
        bondy_config: { name: bondyName.trim() },
      });
      await refreshUser();
      setShowBondyModal(false);
    } catch {
      Alert.alert('Error', 'No se pudo actualizar el nombre');
    } finally {
      setSaving(false);
    }
  };

  if (!user) return null;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Profile Section */}
      <Card style={styles.profileCard} variant="elevated">
        <View style={styles.profileRow}>
          <Avatar name={user.name} photoUrl={user.picture} size="large" />
          <View style={styles.profileInfo}>
            <Text style={styles.profileName}>{user.name}</Text>
            <Text style={styles.profileEmail}>{user.email}</Text>
          </View>
        </View>
      </Card>

      {/* Bondy Section */}
      <Text style={styles.sectionTitle}>Tu asistente</Text>
      <Card variant="outlined">
        <TouchableOpacity style={styles.settingRow} onPress={() => setShowBondyModal(true)}>
          <View style={styles.settingLeft}>
            <Text style={styles.settingEmoji}>🤖</Text>
            <View>
              <Text style={styles.settingLabel}>Nombre del asistente</Text>
              <Text style={styles.settingValue}>{user.bondy_config.name}</Text>
            </View>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        <View style={styles.divider} />

        <View style={styles.settingRow}>
          <View style={styles.settingLeft}>
            <Text style={styles.settingEmoji}>💪</Text>
            <View>
              <Text style={styles.settingLabel}>Nivel de coaching</Text>
              <Text style={styles.settingValue}>
                {user.settings.coaching_level === 'activo'
                  ? 'Activo - Consejos proactivos'
                  : user.settings.coaching_level === 'sutil'
                  ? 'Sutil - Solo cuando preguntes'
                  : 'Moderado - Equilibrado'}
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.coachingButtons}>
          {['activo', 'moderado', 'sutil'].map((level) => (
            <TouchableOpacity
              key={level}
              style={[
                styles.coachingButton,
                user.settings.coaching_level === level && styles.coachingButtonActive,
              ]}
              onPress={() => handleUpdateCoachingLevel(level)}
            >
              <Text
                style={[
                  styles.coachingButtonText,
                  user.settings.coaching_level === level && styles.coachingButtonTextActive,
                ]}
              >
                {level.charAt(0).toUpperCase() + level.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </Card>

      {/* Notifications Section */}
      <Text style={styles.sectionTitle}>Notificaciones</Text>
      <Card variant="outlined">
        <View style={styles.settingRow}>
          <View style={styles.settingLeft}>
            <Text style={styles.settingEmoji}>🔔</Text>
            <View>
              <Text style={styles.settingLabel}>Notificaciones push</Text>
              <Text style={styles.settingValue}>Recibe recordatorios y sugerencias</Text>
            </View>
          </View>
          <Switch
            value={user.settings.notifications_enabled}
            onValueChange={handleUpdateNotifications}
            trackColor={{ false: '#D1D5DB', true: '#C4B5FD' }}
            thumbColor={user.settings.notifications_enabled ? '#8B5CF6' : '#9CA3AF'}
          />
        </View>

        <View style={styles.divider} />

        <View style={styles.settingRow}>
          <View style={styles.settingLeft}>
            <Text style={styles.settingEmoji}>⏰</Text>
            <View>
              <Text style={styles.settingLabel}>Hora del ritual</Text>
              <Text style={styles.settingValue}>{user.settings.ritual_time}</Text>
            </View>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </View>
      </Card>

      {/* Preferences Section */}
      <Text style={styles.sectionTitle}>Preferencias</Text>
      <Card variant="outlined">
        <View style={styles.settingRow}>
          <View style={styles.settingLeft}>
            <Text style={styles.settingEmoji}>📅</Text>
            <View>
              <Text style={styles.settingLabel}>Días sin contacto = descuidado</Text>
              <Text style={styles.settingValue}>{user.settings.neglect_days} días</Text>
            </View>
          </View>
        </View>
      </Card>

      {/* About Section */}
      <Text style={styles.sectionTitle}>Acerca de</Text>
      <Card variant="outlined">
        <View style={styles.settingRow}>
          <View style={styles.settingLeft}>
            <Text style={styles.settingEmoji}>📱</Text>
            <View>
              <Text style={styles.settingLabel}>Versión</Text>
              <Text style={styles.settingValue}>1.0.0</Text>
            </View>
          </View>
        </View>
      </Card>

      {/* Logout Button */}
      <Button
        title="Cerrar sesión"
        onPress={handleLogout}
        variant="outline"
        fullWidth
        style={styles.logoutButton}
      />

      {/* Bondy Name Modal */}
      <Modal
        visible={showBondyModal}
        animationType="fade"
        transparent
        onRequestClose={() => setShowBondyModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Nombre del asistente</Text>
            <Text style={styles.modalSubtitle}>
              Personaliza cómo quieres que se llame tu asistente
            </Text>
            <TextInput
              style={styles.modalInput}
              value={bondyName}
              onChangeText={setBondyName}
              placeholder="Nombre"
              maxLength={20}
            />
            <View style={styles.modalButtons}>
              <Button
                title="Cancelar"
                onPress={() => setShowBondyModal(false)}
                variant="ghost"
              />
              <Button
                title="Guardar"
                onPress={handleSaveBondyName}
                variant="primary"
                loading={saving}
              />
            </View>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  content: {
    padding: 16,
    paddingBottom: 32,
  },
  profileCard: {
    marginBottom: 24,
  },
  profileRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  profileInfo: {
    marginLeft: 16,
  },
  profileName: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1F2937',
  },
  profileEmail: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 2,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    marginBottom: 8,
    marginTop: 16,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingEmoji: {
    fontSize: 24,
    marginRight: 12,
  },
  settingLabel: {
    fontSize: 15,
    fontWeight: '500',
    color: '#1F2937',
  },
  settingValue: {
    fontSize: 13,
    color: '#6B7280',
    marginTop: 2,
  },
  divider: {
    height: 1,
    backgroundColor: '#E5E7EB',
    marginVertical: 12,
  },
  coachingButtons: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 12,
  },
  coachingButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    backgroundColor: '#F3F4F6',
    alignItems: 'center',
  },
  coachingButtonActive: {
    backgroundColor: '#8B5CF6',
  },
  coachingButtonText: {
    fontSize: 13,
    fontWeight: '500',
    color: '#6B7280',
  },
  coachingButtonTextActive: {
    color: '#FFFFFF',
  },
  logoutButton: {
    marginTop: 32,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    width: '100%',
    maxWidth: 340,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    textAlign: 'center',
  },
  modalSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 20,
  },
  modalInput: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 14,
    fontSize: 16,
    color: '#1F2937',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    textAlign: 'center',
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 12,
    marginTop: 20,
  },
});
