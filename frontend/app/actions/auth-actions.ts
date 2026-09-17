'use server';

import { createClient } from '@supabase/supabase-js';
import { Profile } from '@/lib/types';

function getSupabaseAdmin() {
  const supabaseUrl =
    process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://vkkbvvpjfomxwawggsel.supabase.co';
  const supabaseSecretKey =
    process.env.SUPABASE_SERVICE_ROLE_KEY ||
    process.env.SUPABASE_SECRET_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
    '';

  return createClient(supabaseUrl, supabaseSecretKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });
}

export async function updateProfileServerAction(
  userId: string,
  updates: Partial<Profile>
): Promise<{ success: boolean; profile?: Profile; error?: string }> {
  try {
    const supabase = getSupabaseAdmin();

    const { data, error } = await supabase
      .from('profiles')
      .update(updates)
      .eq('id', userId)
      .select()
      .maybeSingle();

    if (error) {
      console.error('Error updating profile in Supabase Admin:', error);
      return { success: false, error: error.message };
    }

    return { success: true, profile: data as Profile };
  } catch (err: any) {
    console.error('Exception updating profile:', err);
    return { success: false, error: err.message || 'Erro ao conectar ao banco de dados.' };
  }
}

export async function getProfileByTokenServerAction(
  token: string
): Promise<{ success: boolean; profile?: Profile; error?: string }> {
  try {
    if (!token || token.trim().length === 0) {
      return { success: false, error: 'Token vazio' };
    }

    const supabase = getSupabaseAdmin();
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('auth_token', token.trim())
      .maybeSingle();

    if (error) {
      return { success: false, error: error.message };
    }

    if (!data) {
      return { success: false, error: 'Perfil não encontrado para o token fornecido' };
    }

    return { success: true, profile: data as Profile };
  } catch (err: any) {
    return { success: false, error: err.message };
  }
}

export async function getProfileByIdServerAction(
  userId: string
): Promise<{ success: boolean; profile?: Profile; error?: string }> {
  try {
    const supabase = getSupabaseAdmin();
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .maybeSingle();

    if (error) {
      return { success: false, error: error.message };
    }

    return { success: true, profile: (data as Profile) || undefined };
  } catch (err: any) {
    return { success: false, error: err.message };
  }
}

export async function getSchedulesServerAction(
  userId: string
): Promise<{ success: boolean; schedules: any[]; error?: string }> {
  try {
    const supabase = getSupabaseAdmin();
    const { data, error } = await supabase
      .from('schedules')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: true });

    if (error) {
      console.warn('Error fetching schedules with admin client:', error);
      return { success: false, schedules: [], error: error.message };
    }

    return { success: true, schedules: data || [] };
  } catch (err: any) {
    return { success: false, schedules: [], error: err.message };
  }
}

export async function getWorkoutsServerAction(
  userId: string
): Promise<{ success: boolean; workouts: any[]; error?: string }> {
  try {
    const supabase = getSupabaseAdmin();
    const { data, error } = await supabase
      .from('workouts')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) {
      console.warn('Error fetching workouts with admin client:', error);
      return { success: false, workouts: [], error: error.message };
    }

    return { success: true, workouts: data || [] };
  } catch (err: any) {
    return { success: false, workouts: [], error: err.message };
  }
}

export async function markWorkoutCompletedServerAction(
  scheduleId: string,
  userId?: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = getSupabaseAdmin();
    const nowStr = new Date().toISOString();

    let query = supabase
      .from('schedules')
      .update({
        status: 'Concluído',
        data_conclusao: nowStr,
      })
      .eq('id', scheduleId);

    if (userId) {
      query = query.eq('user_id', userId);
    }

    const { error } = await query;
    if (error) {
      return { success: false, error: error.message };
    }

    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message };
  }
}

export async function recordManualWorkoutServerAction(
  userId: string,
  data: {
    distancia_km: number;
    tempo_min: number;
    pace_medio: string;
    fc_media: number;
    rpe: number;
    notas_atleta?: string;
  },
  scheduleId?: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = getSupabaseAdmin();
    const now = new Date();
    const formattedDate = `${String(now.getDate()).padStart(2, '0')}/${String(
      now.getMonth() + 1
    ).padStart(2, '0')}/${now.getFullYear()}`;

    const { error: insertError } = await supabase.from('workouts').insert({
      user_id: userId,
      data: formattedDate,
      distancia_km: Number(data.distancia_km) || 0,
      tempo_min: Number(data.tempo_min) || 0,
      pace_medio: data.pace_medio || '05:30',
      fc_media: Number(data.fc_media) || 0,
      zona_predominante: 'Rodagem Aeróbica',
      rpe: Number(data.rpe) || 5,
      notas_atleta: data.notas_atleta || 'Registro manual',
      parecer_treinador: 'Treino manual registrado diretamente pelo atleta.',
    });

    if (insertError) {
      console.error('Error inserting manual workout:', insertError);
      return { success: false, error: insertError.message };
    }

    if (scheduleId) {
      await supabase
        .from('schedules')
        .update({
          status: 'Concluído',
          data_conclusao: now.toISOString(),
        })
        .eq('id', scheduleId);
    }

    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message };
  }
}
