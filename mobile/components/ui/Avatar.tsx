import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';

interface AvatarProps {
  name: string;
  photoUrl?: string | null;
  size?: 'small' | 'medium' | 'large';
}

const SIZES = {
  small: 36,
  medium: 48,
  large: 80,
};

const FONT_SIZES = {
  small: 14,
  medium: 18,
  large: 28,
};

// Generate a consistent color based on name
function getColorFromName(name: string): string {
  const colors = [
    '#8B5CF6', // purple
    '#EC4899', // pink
    '#F59E0B', // amber
    '#10B981', // green
    '#3B82F6', // blue
    '#EF4444', // red
    '#6366F1', // indigo
    '#14B8A6', // teal
  ];

  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }

  return colors[Math.abs(hash) % colors.length];
}

function getInitials(name: string): string {
  const parts = name.trim().split(' ');
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
}

export function Avatar({ name, photoUrl, size = 'medium' }: AvatarProps) {
  const dimension = SIZES[size];
  const fontSize = FONT_SIZES[size];
  const backgroundColor = getColorFromName(name);

  if (photoUrl) {
    return (
      <Image
        source={{ uri: photoUrl }}
        style={[
          styles.image,
          {
            width: dimension,
            height: dimension,
            borderRadius: dimension / 2,
          },
        ]}
      />
    );
  }

  return (
    <View
      style={[
        styles.placeholder,
        {
          width: dimension,
          height: dimension,
          borderRadius: dimension / 2,
          backgroundColor,
        },
      ]}
    >
      <Text style={[styles.initials, { fontSize }]}>
        {getInitials(name)}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  image: {
    backgroundColor: '#E5E7EB',
  },
  placeholder: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  initials: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
});
