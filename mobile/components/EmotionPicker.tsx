import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import type { EmotionType } from '@/types';
import { EMOTION_EMOJIS } from '@/types';

interface EmotionPickerProps {
  value: EmotionType;
  onChange: (emotion: EmotionType) => void;
}

const EMOTIONS: { value: EmotionType; label: string }[] = [
  { value: 'muy_positivo', label: 'Genial' },
  { value: 'positivo', label: 'Bien' },
  { value: 'neutral', label: 'Normal' },
  { value: 'negativo', label: 'Mal' },
  { value: 'muy_negativo', label: 'Fatal' },
];

export function EmotionPicker({ value, onChange }: EmotionPickerProps) {
  return (
    <View style={styles.container}>
      {EMOTIONS.map((emotion) => (
        <TouchableOpacity
          key={emotion.value}
          onPress={() => onChange(emotion.value)}
          style={[
            styles.option,
            value === emotion.value && styles.optionSelected,
          ]}
          activeOpacity={0.7}
        >
          <Text style={styles.emoji}>{EMOTION_EMOJIS[emotion.value]}</Text>
          <Text
            style={[
              styles.label,
              value === emotion.value && styles.labelSelected,
            ]}
          >
            {emotion.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 8,
  },
  option: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 4,
    borderRadius: 12,
    backgroundColor: '#F9FAFB',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  optionSelected: {
    backgroundColor: '#F3E8FF',
    borderColor: '#8B5CF6',
  },
  emoji: {
    fontSize: 24,
    marginBottom: 4,
  },
  label: {
    fontSize: 11,
    color: '#6B7280',
    fontWeight: '500',
  },
  labelSelected: {
    color: '#8B5CF6',
    fontWeight: '600',
  },
});
