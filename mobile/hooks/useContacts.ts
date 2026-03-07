import { useState, useEffect, useCallback } from 'react';
import type { Contact, ContactCreate } from '@/types';
import * as api from '@/services/api';

interface UseContactsOptions {
  relationship_type?: string;
  search?: string;
  sort_by?: string;
  order?: string;
}

export function useContacts(options: UseContactsOptions = {}) {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const fetchContacts = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.getContacts(options);
      setContacts(response.contacts);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar contactos');
    } finally {
      setIsLoading(false);
    }
  }, [options.relationship_type, options.search, options.sort_by, options.order]);

  useEffect(() => {
    fetchContacts();
  }, [fetchContacts]);

  const createContact = async (data: ContactCreate): Promise<Contact> => {
    const newContact = await api.createContact(data);
    setContacts(prev => [...prev, newContact].sort((a, b) => a.name.localeCompare(b.name)));
    setTotal(prev => prev + 1);
    return newContact;
  };

  const updateContact = async (contactId: string, data: Partial<ContactCreate>): Promise<Contact> => {
    const updated = await api.updateContact(contactId, data);
    setContacts(prev => prev.map(c => c.contact_id === contactId ? updated : c));
    return updated;
  };

  const deleteContact = async (contactId: string): Promise<void> => {
    await api.deleteContact(contactId);
    setContacts(prev => prev.filter(c => c.contact_id !== contactId));
    setTotal(prev => prev - 1);
  };

  return {
    contacts,
    isLoading,
    error,
    total,
    refresh: fetchContacts,
    createContact,
    updateContact,
    deleteContact,
  };
}

export function useContact(contactId: string) {
  const [contact, setContact] = useState<Contact | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchContact = useCallback(async () => {
    if (!contactId) return;

    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getContact(contactId);
      setContact(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar contacto');
    } finally {
      setIsLoading(false);
    }
  }, [contactId]);

  useEffect(() => {
    fetchContact();
  }, [fetchContact]);

  return {
    contact,
    isLoading,
    error,
    refresh: fetchContact,
  };
}
