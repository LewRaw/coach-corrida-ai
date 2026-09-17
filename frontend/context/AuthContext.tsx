'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, Session } from '@supabase/supabase-js';
import { supabase, DEMO_PROFILE, getProfile, upsertProfile } from '@/lib/supabase';
import { Profile } from '@/lib/types';

interface AuthContextType {
  user: User | null;
  profile: Profile | null;
  session: Session | null;
  loading: boolean;
  isDemoMode: boolean;
  signIn: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  signUp: (
    nome: string,
    email: string,
    password: string
  ) => Promise<{ success: boolean; error?: string }>;
  signOut: () => Promise<void>;
  updateProfile: (updated: Partial<Profile>) => Promise<boolean>;
  setDemoMode: (enabled: boolean) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isDemoMode, setIsDemoMode] = useState<boolean>(false);

  // Initialize session and listen for auth state changes
  useEffect(() => {
    let isMounted = true;

    async function initAuth() {
      try {
        // Check active session
        const { data, error } = await supabase.auth.getSession();
        if (error) {
          console.warn('Get session warning:', error.message);
        }

        if (data?.session && isMounted) {
          setSession(data.session);
          setUser(data.session.user);
          const prof = await getProfile(data.session.user.id);
          if (isMounted) {
            setProfile(
              prof || {
                id: data.session.user.id,
                email: data.session.user.email || '',
                nome: data.session.user.user_metadata?.nome || 'Atleta',
                modalidade_preferida: 'Corrida',
                objetivo_principal: 'Meia Maratona (21.1 km)',
                esportes_ativos: ['Corrida'],
                nivel_experiencia: 'Intermediário',
                dias_disponiveis: 4,
                onboarding_concluido: true,
              }
            );
          }
        }
      } catch (err) {
        console.warn('Error during auth initialization:', err);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    initAuth();

    // Listen to Supabase auth events
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, currentSession) => {
      if (!isMounted) return;

      if (currentSession?.user) {
        setSession(currentSession);
        setUser(currentSession.user);
        setIsDemoMode(false);
        const prof = await getProfile(currentSession.user.id);
        if (isMounted) {
          setProfile(
            prof || {
              id: currentSession.user.id,
              email: currentSession.user.email || '',
              nome: currentSession.user.user_metadata?.nome || 'Atleta',
              modalidade_preferida: 'Corrida',
              objetivo_principal: 'Meia Maratona (21.1 km)',
              esportes_ativos: ['Corrida'],
              nivel_experiencia: 'Intermediário',
              dias_disponiveis: 4,
              onboarding_concluido: true,
            }
          );
        }
      } else if (!isDemoMode) {
        setSession(null);
        setUser(null);
        setProfile(null);
      }
      setLoading(false);
    });

    return () => {
      isMounted = false;
      subscription.unsubscribe();
    };
  }, [isDemoMode]);

  const signIn = async (email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        if (
          error.message.includes('Invalid login') ||
          error.message.includes('credentials')
        ) {
          return { success: false, error: 'E-mail ou senha incorretos.' };
        }
        return { success: false, error: error.message };
      }

      if (data.user) {
        setUser(data.user);
        setSession(data.session);
        setIsDemoMode(false);
        const prof = await getProfile(data.user.id);
        setProfile(
          prof || {
            id: data.user.id,
            email: data.user.email || email,
            nome: data.user.user_metadata?.nome || 'Atleta',
            modalidade_preferida: 'Corrida',
            objetivo_principal: 'Meia Maratona (21.1 km)',
            esportes_ativos: ['Corrida'],
            nivel_experiencia: 'Intermediário',
            dias_disponiveis: 4,
            onboarding_concluido: true,
          }
        );
      }

      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message || 'Falha ao conectar com o servidor de autenticação.' };
    }
  };

  const signUp = async (nome: string, email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { nome },
        },
      });

      if (error) {
        if (
          error.message.includes('already registered') ||
          error.message.includes('User already registered')
        ) {
          return {
            success: false,
            error: 'Este e-mail já está cadastrado. Faça login na aba ao lado.',
          };
        }
        return { success: false, error: error.message };
      }

      if (data.user) {
        const initialProfile: Profile = {
          id: data.user.id,
          nome,
          email,
          modalidade_preferida: 'Corrida',
          objetivo_principal: 'Meia Maratona (21.1 km)',
          esportes_ativos: ['Corrida'],
          nivel_experiencia: 'Intermediário',
          dias_disponiveis: 4,
          onboarding_concluido: true,
          created_at: new Date().toISOString(),
        };

        // Provision profile into public.profiles
        await upsertProfile(initialProfile);

        setUser(data.user);
        setSession(data.session);
        setProfile(initialProfile);
        setIsDemoMode(false);
      }

      return { success: true };
    } catch (err: any) {
      return {
        success: false,
        error: err.message || 'Erro inesperado durante o cadastro.',
      };
    }
  };

  const signOut = async () => {
    try {
      await supabase.auth.signOut();
    } catch (err) {
      console.warn('Sign out warning:', err);
    } finally {
      setUser(null);
      setSession(null);
      setProfile(null);
      setIsDemoMode(false);
    }
  };

  const updateProfileData = async (updated: Partial<Profile>): Promise<boolean> => {
    if (!profile) return false;
    const newProfile = { ...profile, ...updated };
    setProfile(newProfile);

    if (isDemoMode) {
      return true;
    }

    return await upsertProfile(newProfile);
  };

  const setDemoMode = (enabled: boolean) => {
    setIsDemoMode(enabled);
    if (enabled) {
      setProfile(DEMO_PROFILE);
      setUser({
        id: DEMO_PROFILE.id,
        app_metadata: {},
        user_metadata: { nome: DEMO_PROFILE.nome },
        aud: 'authenticated',
        created_at: new Date().toISOString(),
      } as User);
    } else {
      setProfile(null);
      setUser(null);
      setSession(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        session,
        loading,
        isDemoMode,
        signIn,
        signUp,
        signOut,
        updateProfile: updateProfileData,
        setDemoMode,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
