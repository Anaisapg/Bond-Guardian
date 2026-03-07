import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Avatar } from './ui/Avatar';
import type { Contact } from '@/types';
import { getRelationshipEmoji } from '@/types';

interface ContactCardProps {
  contact: Contact;
  onPress?: () => void;
  showLastInteraction?: boolean;
}

export function ContactCard({ contact, onPress, showLastInteraction = true }: ContactCardProps) {
  const daysAgo = contact.days_since_last_interaction;

  const getDaysLabel = () => {
    if (daysAgo === null) return 'Sin contacto';
    if (daysAgo === 0) return 'Hoy';
    if (daysAgo === 1) return 'Ayer';
    return `Hace ${daysAgo}d`;
  };

  const getDaysColor = () => {
    if (daysAgo === null) return '#9CA3AF';
    if (daysAgo <= 7) return '#10B981';
    if (daysAgo <= 14) return '#F59E0B';
    return '#EF4444';
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      style={styles.container}
      activeOpacity={0.7}
    >
      <Avatar name={contact.name} photoUrl={contact.photo_url} size="medium" />

      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.name} numberOfLines={1}>
            {contact.name}
          </Text>
          <Text style={styles.relationshipEmoji}>
            {getRelationshipEmoji(contact.relationship_type)}
          </Text>
        </View>

        {showLastInteraction && (
          <Text style={styles.summary} numberOfLines={1}>
            {contact.last_interaction_summary || 'Sin interacciones registradas'}
          </Text>
        )}
      </View>

      <View style={styles.badge}>
        <Text style={[styles.daysText, { color: getDaysColor() }]}>
          {getDaysLabel()}
        </Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#F3F4F6',
  },
  content: {
    flex: 1,
    marginLeft: 12,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  name: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    flex: 1,
  },
  relationshipEmoji: {
    fontSize: 14,
  },
  summary: {
    fontSize: 13,
    color: '#6B7280',
    marginTop: 2,
  },
  badge: {
    marginLeft: 8,
  },
  daysText: {
    fontSize: 12,
    fontWeight: '600',
  },
});
