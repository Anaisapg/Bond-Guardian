// User Types
export interface UserSettings {
  gender_preference: 'masculino' | 'femenino' | 'neutro' | 'no_especificado';
  coaching_level: 'activo' | 'moderado' | 'sutil';
  ritual_time: string;
  neglect_days: number;
  notifications_enabled: boolean;
}

export interface BondyConfig {
  name: string;
  coaching_level: string;
  gender: string;
  welcome_messages_enabled: boolean;
  birthday_reminders_enabled: boolean;
}

export interface User {
  user_id: string;
  email: string;
  name: string;
  picture: string | null;
  auth_provider: string;
  settings: UserSettings;
  bondy_config: BondyConfig;
  created_at: string;
}

// Contact Types
export interface Contact {
  contact_id: string;
  user_id: string;
  name: string;
  phone: string | null;
  email: string | null;
  photo_url: string | null;
  relationship_type: string;
  birthday: string | null;
  last_interaction_date: string | null;
  last_interaction_summary: string | null;
  notes: string | null;
  days_since_last_interaction: number | null;
  created_at: string;
  updated_at: string;
}

export interface ContactCreate {
  name: string;
  phone?: string;
  email?: string;
  photo_url?: string;
  relationship_type?: string;
  birthday?: string;
  notes?: string;
}

// Interaction Types
export type EmotionType = 'muy_positivo' | 'positivo' | 'neutral' | 'negativo' | 'muy_negativo';

export const EMOTION_EMOJIS: Record<EmotionType, string> = {
  muy_positivo: '😄',
  positivo: '🙂',
  neutral: '😐',
  negativo: '😔',
  muy_negativo: '😢',
};

export interface Interaction {
  interaction_id: string;
  contact_id: string;
  user_id: string;
  contact_name: string | null;
  date: string;
  quick_summary: string;
  emotion: EmotionType;
  emotion_emoji: string;
  topics: string[];
  is_highlight: boolean;
  photos: string[];
  created_at: string;
  updated_at: string;
}

export interface InteractionCreate {
  contact_id: string;
  date?: string;
  quick_summary: string;
  emotion?: EmotionType;
  topics?: string[];
  is_highlight?: boolean;
}

// Reminder Types
export interface Reminder {
  reminder_id: string;
  contact_id: string;
  user_id: string;
  contact_name: string | null;
  reminder_date: string;
  reason: string;
  is_birthday: boolean;
  completed: boolean;
  completed_at: string | null;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReminderCreate {
  contact_id: string;
  reminder_date: string;
  reason: string;
  is_birthday?: boolean;
}

// Ritual Types
export interface RitualStreak {
  user_id: string;
  current_streak: number;
  longest_streak: number;
  last_ritual_date: string | null;
  total_rituals: number;
  completed_today: boolean;
}

export interface PersonOfDay {
  contact: Contact;
  context: string;
  reason: string;
  days_since_contact: number | null;
  suggested_actions: string[];
}

export interface RitualStats {
  streak: RitualStreak;
  total_contacts: number;
  neglected_contacts: number;
  interactions_this_week: number;
  interactions_this_month: number;
  upcoming_birthdays: {
    contact_id: string;
    name: string;
    birthday: string;
    days_until: number;
  }[];
}

// Chat Types
export type ChatMode = 'accion' | 'charla' | 'analisis';
export type SenderType = 'user' | 'bondy';
export type MessageType = 'text' | 'action_preview' | 'system';

export interface ActionPreview {
  type: string;
  data: Record<string, unknown>;
  status: 'pending' | 'confirmed' | 'cancelled';
}

export interface ChatMessage {
  message_id: string;
  sender: SenderType;
  content: string;
  timestamp: string;
  message_type: MessageType;
  metadata: {
    mode: ChatMode;
    action_preview?: ActionPreview;
  };
}

// API Response Types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export interface ListResponse<T> {
  items: T[];
  total: number;
}

// Relationship Types for Display
export const RELATIONSHIP_TYPES = [
  { value: 'familia', label: 'Familia', emoji: '👨‍👩‍👧‍👦' },
  { value: 'amigo', label: 'Amigo/a', emoji: '🤝' },
  { value: 'pareja', label: 'Pareja', emoji: '❤️' },
  { value: 'trabajo', label: 'Trabajo', emoji: '💼' },
  { value: 'conocido', label: 'Conocido/a', emoji: '👋' },
] as const;

export const getRelationshipEmoji = (type: string): string => {
  const rel = RELATIONSHIP_TYPES.find(r => r.value === type);
  return rel?.emoji || '👤';
};

export const getRelationshipLabel = (type: string): string => {
  const rel = RELATIONSHIP_TYPES.find(r => r.value === type);
  return rel?.label || type;
};
