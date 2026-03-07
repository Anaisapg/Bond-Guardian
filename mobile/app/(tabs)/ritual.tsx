import { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Alert,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '@/contexts/AuthContext';
import { usePersonOfDay, useRitualStats, useInsights } from '@/hooks';
import {
  Card,
  Button,
  Avatar,
  StatCard,
  LoadingSpinner,
  EmptyState,
} from '@/components';
import { getRelationshipEmoji } from '@/types';

export default function RitualScreen() {
  const { user } = useAuth();
  const { personOfDay, isLoading: loadingPerson, refresh: refreshPerson } = usePersonOfDay();
  const { stats, isLoading: loadingStats, refresh: refreshStats, completeRitual } = useRitualStats();
  const { insights, isLoading: loadingInsights, refresh: refreshInsights } = useInsights();
  const [refreshing, setRefreshing] = useState(false);
  const [completing, setCompleting] = useState(false);

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([refreshPerson(), refreshStats(), refreshInsights()]);
    setRefreshing(false);
  };

  const handleCompleteRitual = async () => {
    if (!personOfDay) return;

    try {
      setCompleting(true);
      await completeRitual();
      Alert.alert(
        '¡Ritual completado!',
        `Has mantenido tu conexión con ${personOfDay.contact.name}. ¡Sigue así!`,
        [{ text: 'Genial', style: 'default' }]
      );
      await refreshStats();
    } catch (err) {
      Alert.alert('Error', 'No se pudo completar el ritual');
    } finally {
      setCompleting(false);
    }
  };

  const isLoading = loadingPerson && loadingStats && !refreshing;

  if (isLoading) {
    return <LoadingSpinner message="Preparando tu ritual..." fullScreen />;
  }

  const completedToday = stats?.streak.completed_today ?? false;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={onRefresh}
          tintColor="#8B5CF6"
        />
      }
    >
      {/* Header Greeting */}
      <View style={styles.header}>
        <Text style={styles.greeting}>
          ¡Hola, {user?.name.split(' ')[0]}!
        </Text>
        <Text style={styles.subgreeting}>
          {completedToday
            ? '¡Has completado tu ritual de hoy!'
            : 'Es momento de cuidar tus relaciones'}
        </Text>
      </View>

      {/* Streak Card */}
      {stats && (
        <Card style={styles.streakCard} variant="elevated">
          <View style={styles.streakHeader}>
            <Text style={styles.streakEmoji}>🔥</Text>
            <View>
              <Text style={styles.streakNumber}>{stats.streak.current_streak}</Text>
              <Text style={styles.streakLabel}>días de racha</Text>
            </View>
            {completedToday && (
              <View style={styles.completedBadge}>
                <Ionicons name="checkmark-circle" size={20} color="#10B981" />
                <Text style={styles.completedText}>Hoy</Text>
              </View>
            )}
          </View>
          <View style={styles.streakStats}>
            <View style={styles.streakStat}>
              <Text style={styles.streakStatValue}>{stats.streak.longest_streak}</Text>
              <Text style={styles.streakStatLabel}>Mejor racha</Text>
            </View>
            <View style={styles.streakStat}>
              <Text style={styles.streakStatValue}>{stats.streak.total_rituals}</Text>
              <Text style={styles.streakStatLabel}>Total rituales</Text>
            </View>
          </View>
        </Card>
      )}

      {/* Person of the Day */}
      <Text style={styles.sectionTitle}>Persona del día</Text>

      {personOfDay ? (
        <Card style={styles.personCard} variant="elevated">
          <View style={styles.personHeader}>
            <Avatar
              name={personOfDay.contact.name}
              photoUrl={personOfDay.contact.photo_url}
              size="large"
            />
            <View style={styles.personInfo}>
              <Text style={styles.personName}>{personOfDay.contact.name}</Text>
              <View style={styles.personMeta}>
                <Text style={styles.relationshipEmoji}>
                  {getRelationshipEmoji(personOfDay.contact.relationship_type)}
                </Text>
                <Text style={styles.reason}>{personOfDay.reason}</Text>
              </View>
            </View>
          </View>

          <View style={styles.contextBox}>
            <Ionicons name="bulb-outline" size={16} color="#8B5CF6" />
            <Text style={styles.contextText}>{personOfDay.context}</Text>
          </View>

          {personOfDay.days_since_contact !== null && (
            <View style={styles.daysInfo}>
              <Ionicons name="time-outline" size={14} color="#6B7280" />
              <Text style={styles.daysText}>
                Último contacto: {personOfDay.days_since_contact === 0
                  ? 'Hoy'
                  : personOfDay.days_since_contact === 1
                  ? 'Ayer'
                  : `hace ${personOfDay.days_since_contact} días`}
              </Text>
            </View>
          )}

          {/* Suggested Actions */}
          <View style={styles.actionsContainer}>
            <Text style={styles.actionsTitle}>Acciones sugeridas</Text>
            <View style={styles.actionButtons}>
              {personOfDay.suggested_actions.map((action, index) => (
                <TouchableOpacity key={index} style={styles.actionButton}>
                  <Ionicons
                    name={
                      action.includes('mensaje')
                        ? 'chatbubble-outline'
                        : action.includes('llamada')
                        ? 'call-outline'
                        : 'calendar-outline'
                    }
                    size={20}
                    color="#8B5CF6"
                  />
                  <Text style={styles.actionText}>{action}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Complete Button */}
          {!completedToday && (
            <Button
              title="Completar ritual"
              onPress={handleCompleteRitual}
              variant="primary"
              fullWidth
              loading={completing}
              leftIcon={<Ionicons name="checkmark-circle" size={20} color="#FFFFFF" />}
            />
          )}
        </Card>
      ) : (
        <EmptyState
          icon="👥"
          title="Sin contactos"
          message="Añade contactos para empezar tu ritual diario"
          actionLabel="Ir a Personas"
          onAction={() => {}}
        />
      )}

      {/* Quick Stats */}
      {stats && (
        <>
          <Text style={styles.sectionTitle}>Resumen</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.statsScroll}
          >
            <StatCard
              title="Contactos"
              value={stats.total_contacts}
              icon="👥"
              color="#3B82F6"
            />
            <StatCard
              title="Descuidados"
              value={stats.neglected_contacts}
              icon="⚠️"
              color={stats.neglected_contacts > 0 ? '#EF4444' : '#10B981'}
            />
            <StatCard
              title="Esta semana"
              value={stats.interactions_this_week}
              subtitle="interacciones"
              icon="📅"
              color="#8B5CF6"
            />
            <StatCard
              title="Este mes"
              value={stats.interactions_this_month}
              subtitle="interacciones"
              icon="📊"
              color="#F59E0B"
            />
          </ScrollView>
        </>
      )}

      {/* Upcoming Birthdays */}
      {stats && stats.upcoming_birthdays.length > 0 && (
        <>
          <Text style={styles.sectionTitle}>Próximos cumpleaños</Text>
          <Card variant="outlined">
            {stats.upcoming_birthdays.map((birthday, index) => (
              <View
                key={birthday.contact_id}
                style={[
                  styles.birthdayItem,
                  index < stats.upcoming_birthdays.length - 1 && styles.birthdayBorder,
                ]}
              >
                <Text style={styles.birthdayEmoji}>🎂</Text>
                <View style={styles.birthdayInfo}>
                  <Text style={styles.birthdayName}>{birthday.name}</Text>
                  <Text style={styles.birthdayDate}>
                    {birthday.days_until === 0
                      ? '¡Hoy!'
                      : birthday.days_until === 1
                      ? 'Mañana'
                      : `En ${birthday.days_until} días`}
                  </Text>
                </View>
              </View>
            ))}
          </Card>
        </>
      )}

      {/* AI Insights */}
      {insights.length > 0 && (
        <>
          <Text style={styles.sectionTitle}>Insights de {user?.bondy_config.name || 'Bondy'}</Text>
          <Card variant="outlined" style={styles.insightsCard}>
            {insights.map((insight, index) => (
              <View key={index} style={styles.insightItem}>
                <Ionicons name="sparkles" size={16} color="#8B5CF6" />
                <Text style={styles.insightText}>{insight}</Text>
              </View>
            ))}
          </Card>
        </>
      )}

      {/* Footer spacing */}
      <View style={{ height: 32 }} />
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
  },
  header: {
    marginBottom: 20,
  },
  greeting: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1F2937',
  },
  subgreeting: {
    fontSize: 16,
    color: '#6B7280',
    marginTop: 4,
  },
  streakCard: {
    backgroundColor: '#8B5CF6',
    marginBottom: 24,
  },
  streakHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  streakEmoji: {
    fontSize: 40,
    marginRight: 12,
  },
  streakNumber: {
    fontSize: 48,
    fontWeight: '700',
    color: '#FFFFFF',
    lineHeight: 52,
  },
  streakLabel: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
    marginTop: -4,
  },
  completedBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    marginLeft: 'auto',
    gap: 4,
  },
  completedText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 13,
  },
  streakStats: {
    flexDirection: 'row',
    gap: 24,
  },
  streakStat: {
    alignItems: 'center',
  },
  streakStatValue: {
    fontSize: 20,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  streakStatLabel: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.7)',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 12,
    marginTop: 8,
  },
  personCard: {
    marginBottom: 24,
  },
  personHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  personInfo: {
    marginLeft: 16,
    flex: 1,
  },
  personName: {
    fontSize: 22,
    fontWeight: '600',
    color: '#1F2937',
  },
  personMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 4,
  },
  relationshipEmoji: {
    fontSize: 16,
  },
  reason: {
    fontSize: 14,
    color: '#8B5CF6',
    fontWeight: '500',
  },
  contextBox: {
    flexDirection: 'row',
    backgroundColor: '#F3E8FF',
    padding: 12,
    borderRadius: 12,
    gap: 8,
    marginBottom: 12,
  },
  contextText: {
    flex: 1,
    fontSize: 14,
    color: '#6B21A8',
    lineHeight: 20,
  },
  daysInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 16,
  },
  daysText: {
    fontSize: 13,
    color: '#6B7280',
  },
  actionsContainer: {
    marginBottom: 16,
  },
  actionsTitle: {
    fontSize: 13,
    fontWeight: '500',
    color: '#6B7280',
    marginBottom: 8,
  },
  actionButtons: {
    gap: 8,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    padding: 12,
    borderRadius: 10,
    gap: 10,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  actionText: {
    fontSize: 14,
    color: '#374151',
    fontWeight: '500',
  },
  statsScroll: {
    gap: 12,
    paddingRight: 16,
    marginBottom: 16,
  },
  birthdayItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
  },
  birthdayBorder: {
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  birthdayEmoji: {
    fontSize: 24,
    marginRight: 12,
  },
  birthdayInfo: {
    flex: 1,
  },
  birthdayName: {
    fontSize: 15,
    fontWeight: '500',
    color: '#1F2937',
  },
  birthdayDate: {
    fontSize: 13,
    color: '#6B7280',
  },
  insightsCard: {
    gap: 12,
  },
  insightItem: {
    flexDirection: 'row',
    gap: 10,
  },
  insightText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
});
