import { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  RefreshControl,
  Alert,
  Modal,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useContacts } from '@/hooks';
import {
  ContactCard,
  Button,
  LoadingSpinner,
  EmptyState,
} from '@/components';
import type { Contact, ContactCreate } from '@/types';
import { RELATIONSHIP_TYPES } from '@/types';

export default function ContactsScreen() {
  const [search, setSearch] = useState('');
  const { contacts, isLoading, error, refresh, createContact, deleteContact } = useContacts({ search });
  const [refreshing, setRefreshing] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [newContact, setNewContact] = useState<ContactCreate>({
    name: '',
    phone: '',
    relationship_type: 'amigo',
  });
  const [saving, setSaving] = useState(false);

  const onRefresh = async () => {
    setRefreshing(true);
    await refresh();
    setRefreshing(false);
  };

  const handleCreateContact = async () => {
    if (!newContact.name.trim()) {
      Alert.alert('Error', 'El nombre es obligatorio');
      return;
    }

    try {
      setSaving(true);
      await createContact(newContact);
      setShowModal(false);
      setNewContact({ name: '', phone: '', relationship_type: 'amigo' });
      Alert.alert('Contacto creado', `${newContact.name} ha sido añadido`);
    } catch (err) {
      Alert.alert('Error', 'No se pudo crear el contacto');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteContact = (contact: Contact) => {
    Alert.alert(
      'Eliminar contacto',
      `¿Seguro que quieres eliminar a ${contact.name}? Se borrarán todas sus interacciones.`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteContact(contact.contact_id);
            } catch {
              Alert.alert('Error', 'No se pudo eliminar el contacto');
            }
          },
        },
      ]
    );
  };

  const renderContact = useCallback(
    ({ item }: { item: Contact }) => (
      <ContactCard
        contact={item}
        onPress={() => {
          // TODO: Navigate to contact detail
        }}
      />
    ),
    []
  );

  if (isLoading && !refreshing && contacts.length === 0) {
    return <LoadingSpinner message="Cargando contactos..." fullScreen />;
  }

  return (
    <View style={styles.container}>
      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <View style={styles.searchBar}>
          <Ionicons name="search" size={20} color="#9CA3AF" />
          <TextInput
            style={styles.searchInput}
            placeholder="Buscar contactos..."
            placeholderTextColor="#9CA3AF"
            value={search}
            onChangeText={setSearch}
          />
          {search.length > 0 && (
            <Ionicons
              name="close-circle"
              size={20}
              color="#9CA3AF"
              onPress={() => setSearch('')}
            />
          )}
        </View>
        <Button
          title=""
          onPress={() => setShowModal(true)}
          variant="primary"
          style={styles.addButton}
          leftIcon={<Ionicons name="add" size={24} color="#FFFFFF" />}
        />
      </View>

      {/* Contacts List */}
      {contacts.length === 0 ? (
        <EmptyState
          icon="👥"
          title="Sin contactos"
          message="Añade tus primeros contactos para empezar a cuidar tus relaciones"
          actionLabel="Añadir contacto"
          onAction={() => setShowModal(true)}
        />
      ) : (
        <FlatList
          data={contacts}
          renderItem={renderContact}
          keyExtractor={(item) => item.contact_id}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor="#8B5CF6"
            />
          }
        />
      )}

      {/* Add Contact Modal */}
      <Modal
        visible={showModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowModal(false)}
      >
        <KeyboardAvoidingView
          style={styles.modalContainer}
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
          <View style={styles.modalHeader}>
            <Button
              title="Cancelar"
              onPress={() => setShowModal(false)}
              variant="ghost"
            />
            <Text style={styles.modalTitle}>Nuevo contacto</Text>
            <Button
              title="Guardar"
              onPress={handleCreateContact}
              variant="ghost"
              loading={saving}
            />
          </View>

          <ScrollView style={styles.modalContent}>
            <Text style={styles.inputLabel}>Nombre *</Text>
            <TextInput
              style={styles.input}
              placeholder="Nombre del contacto"
              placeholderTextColor="#9CA3AF"
              value={newContact.name}
              onChangeText={(text) => setNewContact({ ...newContact, name: text })}
            />

            <Text style={styles.inputLabel}>Teléfono</Text>
            <TextInput
              style={styles.input}
              placeholder="+34 600 000 000"
              placeholderTextColor="#9CA3AF"
              keyboardType="phone-pad"
              value={newContact.phone}
              onChangeText={(text) => setNewContact({ ...newContact, phone: text })}
            />

            <Text style={styles.inputLabel}>Relación</Text>
            <View style={styles.relationshipGrid}>
              {RELATIONSHIP_TYPES.map((rel) => (
                <Button
                  key={rel.value}
                  title={`${rel.emoji} ${rel.label}`}
                  onPress={() => setNewContact({ ...newContact, relationship_type: rel.value })}
                  variant={newContact.relationship_type === rel.value ? 'primary' : 'outline'}
                  size="small"
                  style={styles.relationshipButton}
                />
              ))}
            </View>

            <Text style={styles.inputLabel}>Notas</Text>
            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Notas sobre este contacto..."
              placeholderTextColor="#9CA3AF"
              multiline
              numberOfLines={4}
              value={newContact.notes || ''}
              onChangeText={(text) => setNewContact({ ...newContact, notes: text })}
            />
          </ScrollView>
        </KeyboardAvoidingView>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  searchContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  searchBar: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: 12,
    height: 48,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  searchInput: {
    flex: 1,
    marginLeft: 8,
    fontSize: 16,
    color: '#1F2937',
  },
  addButton: {
    width: 48,
    height: 48,
    paddingHorizontal: 0,
  },
  list: {
    padding: 16,
    paddingTop: 0,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  modalTitle: {
    fontSize: 17,
    fontWeight: '600',
    color: '#1F2937',
  },
  modalContent: {
    flex: 1,
    padding: 16,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 8,
    marginTop: 16,
  },
  input: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 14,
    fontSize: 16,
    color: '#1F2937',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  relationshipGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  relationshipButton: {
    flex: 1,
    minWidth: '45%',
  },
});
