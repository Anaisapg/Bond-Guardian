import { useState, useEffect, useCallback } from 'react';
import type { PersonOfDay, RitualStats } from '@/types';
import * as api from '@/services/api';

export function usePersonOfDay() {
  const [personOfDay, setPersonOfDay] = useState<PersonOfDay | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getPersonOfDay();
      setPersonOfDay(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar persona del día');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return {
    personOfDay,
    isLoading,
    error,
    refresh: fetch,
  };
}

export function useRitualStats() {
  const [stats, setStats] = useState<RitualStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getRitualStats();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar estadísticas');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  const completeRitual = async () => {
    const streak = await api.completeRitual();
    setStats(prev => prev ? { ...prev, streak } : null);
    return streak;
  };

  return {
    stats,
    isLoading,
    error,
    refresh: fetch,
    completeRitual,
  };
}

export function useInsights() {
  const [insights, setInsights] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getInsights();
      setInsights(data.insights);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar insights');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return {
    insights,
    isLoading,
    error,
    refresh: fetch,
  };
}
