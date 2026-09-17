'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, Session } from '@supabase/supabase-js';
import { supabase, DEMO_PROFILE, getProfile, upsertProfile } from '@/lib/supabase';
import { Profile } from '@/lib/types';
import {
  getProfileByTokenServerAction,
  getProfileByIdServerAction,
  updateProfileServerAction,
} from '@/app/actions/auth-actions';

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
        // 1. Check URL query params for ?token=... or stored localStorage token
        let token: string | null = null;
        if (typeof window !== 'undefined') {
          const params = new URLSearchParams(window.location.search);
          token = params.get('token') || localStorage.getItem('coachai_auth_token');
        }

        if (token && token.trim()) {
          const tokenRes = await getProfileByTokenServerAction(token.trim());
          if (tokenRes.success && tokenRes.profile && isMounted) {
            const athleteProf = tokenRes.profile;
            setProfile(athleteProf);
            setUser({
              id: athleteProf.id,
              email: athleteProf.email || '',
              app_metadata: {},
              user_metadata: { nome: athleteProf.nome },
              aud: 'authenticated',
              created_at: athleteProf.created_at,
            } as User);
            setIsDemoMode(false);
            if (typeof window !== 'undefined') {
              localStorage.setItem('coachai_auth_token', token.trim());
            }
            return;
          }
        }

        // 2. Check active Supabase session
        const { data, error } = await supabase.auth.getSession();
        if (error) {
          console.warn('Get session warning:', error.message);
        }

        if (data?.session && isMounted) {
          setSession(data.session);
          setUser(data.session.user);
          const profRes = await getProfileByIdServerAction(data.session.user.id);
          if (isMounted) {
            if (profRes.success && profRes.profile) {
              setProfile(profRes.profile);
              if (profRes.profile.auth_token && typeof window !== 'undefined') {
                localStorage.setItem('coachai_auth_token', profRes.profile.auth_token);
              }
            } else {
              setProfile({
                id: data.session.user.id,
                email: data.session.user.email || '',
                nome: data.session.user.user_metadata?.nome || 'Atleta',
                modalidade_preferida: 'Corrida',
                objetivo_principal: 'Meia Maratona (21.1 km)',
                esportes_ativos: ['Corrida de Rua'],
                nivel_experiencia: 'Intermediário',
                dias_disponiveis: 4,
                onboarding_concluido: true,
              });
            }
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
        const profRes = await getProfileByIdServerAction(currentSession.user.id);
        if (isMounted) {
          if (profRes.success && profRes.profile) {
            setProfile(profRes.profile);
            if (profRes.profile.auth_token && typeof window !== 'undefined') {
              localStorage.setItem('coachai_auth_token', profRes.profile.auth_token);
            }
          } else {
            setProfile({
              id: currentSession.user.id,
              email: currentSession.user.email || '',
              nome: currentSession.user.user_metadata?.nome || 'Atleta',
              modalidade_preferida: 'Corrida',
              objetivo_principal: 'Meia Maratona (21.1 km)',
              esportes_ativos: ['Corrida de Rua'],
              nivel_experiencia: 'Intermediário',
              dias_disponiveis: 4,
              onboarding_concluido: true,
            });
          }
        }
      } else if (!isDemoMode) {
        // If not using URL token, clear session
        const storedToken = typeof window !== 'undefined' ? localStorage.getItem('coachai_auth_token') : null;
        if (!storedToken) {
          setSession(null);
          setUser(null);
          setProfile(null);
        }
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
        const profRes = await getProfileByIdServerAction(data.user.id);
        const loadedProf: Profile =
          profRes.success && profRes.profile
            ? profRes.profile
            : {
                id: data.user.id,
                email: data.user.email || email,
                nome: data.user.user_metadata?.nome || 'Atleta',
                modalidade_preferida: 'Corrida',
                objetivo_principal: 'Meia Maratona (21.1 km)',
                esportes_ativos: ['Corrida de Rua'],
                nivel_experiencia: 'Intermediário',
                dias_disponiveis: 4,
                onboarding_concluido: true,
              };
        setProfile(loadedProf);
        if (loadedProf.auth_token && typeof window !== 'undefined') {
          localStorage.setItem('coachai_auth_token', loadedProf.auth_token);
        }
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
          esportes_ativos: ['Corrida de Rua'],
          nivel_experiencia: 'Intermediário',
          dias_disponiveis: 4,
          onboarding_concluido: true,
          created_at: new Date().toISOString(),
        };

        // Provision profile into public.profiles via server action
        await updateProfileServerAction(data.user.id, initialProfile);

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
      if (typeof window !== 'undefined') {
        localStorage.removeItem('coachai_auth_token');
        if (window.location.search.includes('token=')) {
          window.history.replaceState({}, '', window.location.pathname);
        }
      }
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

    try {
      const res = await updateProfileServerAction(profile.id, updated);
      if (res.success && res.profile) {
        setProfile(res.profile);
        return true;
      }
      return false;
    } catch (err) {
      console.error('Exception during updateProfileData:', err);
      return false;
    }
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
