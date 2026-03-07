import { useState, useEffect, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '@/contexts/AuthContext';
import * as api from '@/services/api';
import { LoadingSpinner, Avatar } from '@/components';
import type { ChatMessage, ChatMode } from '@/types';

const MODES: { value: ChatMode; label: string; icon: string }[] = [
  { value: 'charla', label: 'Charla', icon: '💬' },
  { value: 'accion', label: 'Acción', icon: '✨' },
  { value: 'analisis', label: 'Análisis', icon: '📊' },
];

export default function ChatScreen() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [inputText, setInputText] = useState('');
  const [sending, setSending] = useState(false);
  const [mode, setMode] = useState<ChatMode>('charla');
  const flatListRef = useRef<FlatList>(null);

  const bondyName = user?.bondy_config.name || 'Bondy';

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await api.getChatHistory({ limit: 50 });
      setMessages(response.messages);
    } catch (err) {
      console.error('Error fetching chat history:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async () => {
    if (!inputText.trim() || sending) return;

    const userMessage: ChatMessage = {
      message_id: `temp-${Date.now()}`,
      sender: 'user',
      content: inputText.trim(),
      timestamp: new Date().toISOString(),
      message_type: 'text',
      metadata: { mode },
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setSending(true);

    // Scroll to bottom
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);

    try {
      const response = await api.sendChatMessage(userMessage.content, mode);
      setMessages((prev) => [...prev, response]);

      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    } catch (err) {
      Alert.alert('Error', 'No se pudo enviar el mensaje');
      // Remove the temporary message
      setMessages((prev) => prev.filter((m) => m.message_id !== userMessage.message_id));
    } finally {
      setSending(false);
    }
  };

  const handleClearHistory = () => {
    Alert.alert(
      'Borrar historial',
      '¿Seguro que quieres borrar todo el historial de chat?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Borrar',
          style: 'destructive',
          onPress: async () => {
            try {
              await api.deleteChatHistory();
              setMessages([]);
            } catch {
              Alert.alert('Error', 'No se pudo borrar el historial');
            }
          },
        },
      ]
    );
  };

  const renderMessage = useCallback(
    ({ item }: { item: ChatMessage }) => {
      const isUser = item.sender === 'user';

      return (
        <View style={[styles.messageContainer, isUser && styles.userMessageContainer]}>
          {!isUser && (
            <View style={styles.avatarContainer}>
              <Text style={styles.bondyAvatar}>🤖</Text>
            </View>
          )}
          <View
            style={[
              styles.messageBubble,
              isUser ? styles.userBubble : styles.bondyBubble,
            ]}
          >
            <Text style={[styles.messageText, isUser && styles.userMessageText]}>
              {item.content}
            </Text>
            <Text style={[styles.messageTime, isUser && styles.userMessageTime]}>
              {new Date(item.timestamp).toLocaleTimeString('es-ES', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </Text>
          </View>
        </View>
      );
    },
    []
  );

  if (isLoading) {
    return <LoadingSpinner message={`Conectando con ${bondyName}...`} fullScreen />;
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={90}
    >
      {/* Mode Selector */}
      <View style={styles.modeContainer}>
        {MODES.map((m) => (
          <TouchableOpacity
            key={m.value}
            style={[styles.modeButton, mode === m.value && styles.modeButtonActive]}
            onPress={() => setMode(m.value)}
          >
            <Text style={styles.modeIcon}>{m.icon}</Text>
            <Text style={[styles.modeText, mode === m.value && styles.modeTextActive]}>
              {m.label}
            </Text>
          </TouchableOpacity>
        ))}
        <TouchableOpacity style={styles.clearButton} onPress={handleClearHistory}>
          <Ionicons name="trash-outline" size={20} color="#9CA3AF" />
        </TouchableOpacity>
      </View>

      {/* Messages List */}
      {messages.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyEmoji}>👋</Text>
          <Text style={styles.emptyTitle}>¡Hola! Soy {bondyName}</Text>
          <Text style={styles.emptyText}>
            Tu compañero para cuidar relaciones.{'\n'}
            Cuéntame, ¿en qué puedo ayudarte hoy?
          </Text>
        </View>
      ) : (
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.message_id}
          contentContainerStyle={styles.messagesList}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
        />
      )}

      {/* Input Area */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder={`Escribe a ${bondyName}...`}
          placeholderTextColor="#9CA3AF"
          value={inputText}
          onChangeText={setInputText}
          multiline
          maxLength={2000}
        />
        <TouchableOpacity
          style={[styles.sendButton, (!inputText.trim() || sending) && styles.sendButtonDisabled]}
          onPress={handleSend}
          disabled={!inputText.trim() || sending}
        >
          {sending ? (
            <LoadingSpinner size="small" />
          ) : (
            <Ionicons name="send" size={20} color="#FFFFFF" />
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  modeContainer: {
    flexDirection: 'row',
    padding: 12,
    gap: 8,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  modeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 16,
    backgroundColor: '#F3F4F6',
    gap: 4,
  },
  modeButtonActive: {
    backgroundColor: '#8B5CF6',
  },
  modeIcon: {
    fontSize: 14,
  },
  modeText: {
    fontSize: 13,
    color: '#6B7280',
    fontWeight: '500',
  },
  modeTextActive: {
    color: '#FFFFFF',
  },
  clearButton: {
    marginLeft: 'auto',
    padding: 8,
  },
  emptyContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 32,
  },
  emptyEmoji: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 15,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 22,
  },
  messagesList: {
    padding: 16,
    paddingBottom: 8,
  },
  messageContainer: {
    flexDirection: 'row',
    marginBottom: 12,
    alignItems: 'flex-end',
  },
  userMessageContainer: {
    justifyContent: 'flex-end',
  },
  avatarContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#F3E8FF',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  bondyAvatar: {
    fontSize: 18,
  },
  messageBubble: {
    maxWidth: '75%',
    padding: 12,
    borderRadius: 16,
  },
  bondyBubble: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderBottomLeftRadius: 4,
  },
  userBubble: {
    backgroundColor: '#8B5CF6',
    borderBottomRightRadius: 4,
  },
  messageText: {
    fontSize: 15,
    color: '#1F2937',
    lineHeight: 22,
  },
  userMessageText: {
    color: '#FFFFFF',
  },
  messageTime: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 4,
    alignSelf: 'flex-end',
  },
  userMessageTime: {
    color: 'rgba(255,255,255,0.7)',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 12,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    alignItems: 'flex-end',
    gap: 8,
  },
  input: {
    flex: 1,
    backgroundColor: '#F9FAFB',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 15,
    color: '#1F2937',
    maxHeight: 100,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#8B5CF6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#D1D5DB',
  },
});
