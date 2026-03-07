import { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '@/services/api';
import { Card, LoadingSpinner, EmptyState, Avatar } from '@/components';
import type { Interaction } from '@/types';
import { EMOTION_EMOJIS } from '@/types';

export default function MemoriesScreen() {
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState<'all' | 'highlights'>('all');

  const fetchInteractions = useCallback(async () => {
    try {
      const params = filter === 'highlights' ? { is_highlight: true } : {};
      const response = await api.getInteractions({ ...params, limit: 50 });
      setInteractions(response.interactions);
    } catch (err) {
      console.error('Error fetching interactions:', err);
    } finally {
      setIsLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchInteractions();
  }, [fetchInteractions]);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchInteractions();
    setRefreshing(false);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Hoy';
    if (diffDays === 1) return 'Ayer';
    if (diffDays < 7) return `Hace ${diffDays} días`;

    return date.toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
    });
  };

  const renderInteraction = useCallback(
    ({ item }: { item: Interaction }) => (
      <Card style={styles.interactionCard} variant="outlined">
        <View style={styles.interactionHeader}>
          <Avatar name={item.contact_name || 'Contacto'} size="small" />
          <View style={styles.interactionInfo}>
            <Text style={styles.contactName}>{item.contact_name}</Text>
            <Text style={styles.interactionDate}>{formatDate(item.date)}</Text>
          </View>
          <Text style={styles.emotionEmoji}>{EMOTION_EMOJIS[item.emotion]}</Text>
          {item.is_highlight && (
            <Ionicons name="star" size={16} color="#F59E0B" />
          )}
        </View>

        <Text style={styles.summary}>{item.quick_summary}</Text>

        {item.topics.length > 0 && (
          <View style={styles.topicsContainer}>
            {item.topics.map((topic, index) => (
              <View key={index} style={styles.topicChip}>
                <Text style={styles.topicText}>{topic}</Text>
              </View>
            ))}
          </View>
        )}

        {item.photos.length > 0 && (
          <View style={styles.photosIndicator}>
            <Ionicons name="images" size={16} color="#9CA3AF" />
            <Text style={styles.photosCount}>{item.photos.length} fotos</Text>
          </View>
        )}
      </Card>
    ),
    []
  );

  if (isLoading && !refreshing) {
    return <LoadingSpinner message="Cargando memorias..." fullScreen />;
  }

  return (
    <View style={styles.container}>
      {/* Filter Tabs */}
      <View style={styles.filterContainer}>
        <TouchableOpacity
          style={[styles.filterTab, filter === 'all' && styles.filterTabActive]}
          onPress={() => setFilter('all')}
        >
          <Text style={[styles.filterText, filter === 'all' && styles.filterTextActive]}>
            Todas
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.filterTab, filter === 'highlights' && styles.filterTabActive]}
          onPress={() => setFilter('highlights')}
        >
          <Ionicons
            name="star"
            size={14}
            color={filter === 'highlights' ? '#8B5CF6' : '#6B7280'}
          />
          <Text style={[styles.filterText, filter === 'highlights' && styles.filterTextActive]}>
            Destacadas
          </Text>
        </TouchableOpacity>
      </View>

      {interactions.length === 0 ? (
        <EmptyState
          icon="💭"
          title="Sin memorias"
          message="Registra tus interacciones para crear un historial de momentos especiales"
          actionLabel="Ir a contactos"
          onAction={() => {}}
        />
      ) : (
        <FlatList
          data={interactions}
          renderItem={renderInteraction}
          keyExtractor={(item) => item.interaction_id}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor="#8B5CF6"
            />
          }
          ItemSeparatorComponent={() => <View style={styles.separator} />}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  filterContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  filterTab: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    gap: 6,
  },
  filterTabActive: {
    backgroundColor: '#F3E8FF',
    borderColor: '#8B5CF6',
  },
  filterText: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '500',
  },
  filterTextActive: {
    color: '#8B5CF6',
  },
  list: {
    padding: 16,
    paddingTop: 0,
  },
  separator: {
    height: 12,
  },
  interactionCard: {
    gap: 12,
  },
  interactionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  interactionInfo: {
    flex: 1,
    marginLeft: 10,
  },
  contactName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1F2937',
  },
  interactionDate: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 1,
  },
  emotionEmoji: {
    fontSize: 20,
    marginRight: 8,
  },
  summary: {
    fontSize: 15,
    color: '#374151',
    lineHeight: 22,
  },
  topicsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  topicChip: {
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  topicText: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: '500',
  },
  photosIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  photosCount: {
    fontSize: 12,
    color: '#9CA3AF',
  },
});
