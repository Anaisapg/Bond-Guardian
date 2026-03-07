import Constants from 'expo-constants';

const BACKEND_URL = Constants.expoConfig?.extra?.backendUrl || 
                   process.env.EXPO_PUBLIC_BACKEND_URL || 
                   'http://localhost:8000';

class ApiService {
  private baseUrl: string;
  private token: string | null = null;

  constructor() {
    this.baseUrl = BACKEND_URL;
  }

  setToken(token: string) {
    this.token = token;
  }

  getToken() {
    return this.token;
  }

  clearToken() {
    this.token = null;
  }

  private async fetch(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
      throw new Error(error.detail || `Error ${response.status}`);
    }

    return response.json();
  }

  // Auth
  async loginWithGoogle() {
    // Abrir navegador para OAuth
    const authUrl = `${this.baseUrl}/api/auth/google`;
    return authUrl;
  }

  async createTestUser() {
    return this.fetch('/api/auth/dev/create-test-user', {
      method: 'POST',
    });
  }

  async getMe() {
    return this.fetch('/api/auth/me');
  }

  // Contacts
  async getContacts() {
    return this.fetch('/api/contacts');
  }

  async createContact(data: any) {
    return this.fetch('/api/contacts', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Ritual
  async getPersonOfDay() {
    return this.fetch('/api/ritual/person-of-day');
  }

  async getRitualStats() {
    return this.fetch('/api/ritual/stats');
  }

  async completeRitual() {
    return this.fetch('/api/ritual/complete', {
      method: 'POST',
    });
  }

  async getInsights() {
    return this.fetch('/api/ritual/insights');
  }

  // Chat
  async sendMessage(content: string, mode: string = 'charla') {
    return this.fetch('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify({ content, mode }),
    });
  }

  async getChatHistory(limit: number = 50) {
    return this.fetch(`/api/chat/history?limit=${limit}`);
  }
}

export const api = new ApiService();
