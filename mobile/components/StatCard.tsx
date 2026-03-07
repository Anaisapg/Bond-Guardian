import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Card } from './ui/Card';

interface StatCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon?: string;
  color?: string;
}

export function StatCard({ title, value, subtitle, icon, color = '#8B5CF6' }: StatCardProps) {
  return (
    <Card style={styles.container} variant="elevated">
      <View style={styles.header}>
        {icon && <Text style={styles.icon}>{icon}</Text>}
        <Text style={styles.title}>{title}</Text>
      </View>
      <Text style={[styles.value, { color }]}>{value}</Text>
      {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
    </Card>
  );
}

const styles = StyleSheet.create({
  container: {
    minWidth: 140,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 8,
  },
  icon: {
    fontSize: 16,
  },
  title: {
    fontSize: 13,
    color: '#6B7280',
    fontWeight: '500',
  },
  value: {
    fontSize: 28,
    fontWeight: '700',
  },
  subtitle: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 4,
  },
});
