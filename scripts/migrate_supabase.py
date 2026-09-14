"""
Script de Migração DDL para o Supabase PostgreSQL.
Cria as tabelas profiles, workouts, schedules com índices e RLS.
"""

import os
import psycopg2

DB_PASSWORD = os.environ.get("SUPABASE_DB_PASSWORD", "4b67utzfow4ss8IJ")
PROJECT_REF = "vkkbvvpjfomxwawggsel"
DB_HOST = f"db.{PROJECT_REF}.supabase.co"

MIGRATION_SQL = """
-- 1. PROFILES
CREATE TABLE IF NOT EXISTS public.profiles (
  id uuid REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  email text,
  nome text,
  modalidade_preferida text DEFAULT 'Corrida',
  objetivo_principal text,
  esportes_ativos text[] DEFAULT ARRAY['Corrida'],
  nivel_experiencia text DEFAULT 'Intermediário',
  dias_disponiveis integer DEFAULT 4,
  pwa_aviso_dispensado boolean DEFAULT false,
  onboarding_concluido boolean DEFAULT false,
  auth_token text,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. WORKOUTS (Treinos Realizados)
CREATE TABLE IF NOT EXISTS public.workouts (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  data text NOT NULL,
  distancia_km numeric(6,2) NOT NULL DEFAULT 0.0,
  tempo_min numeric(7,2) NOT NULL DEFAULT 0.0,
  pace_medio text,
  fc_media integer DEFAULT 0,
  zona_predominante text,
  rpe integer DEFAULT 6,
  notas_atleta text,
  parecer_treinador text,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. SCHEDULES (Cronograma / Prescrição)
CREATE TABLE IF NOT EXISTS public.schedules (
  id text PRIMARY KEY,
  user_id uuid REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  dia_semana text NOT NULL,
  data_prevista text NOT NULL,
  tipo_treino text NOT NULL,
  distancia_km numeric(6,2) DEFAULT 0.0,
  duracao_min numeric(7,2) DEFAULT 0.0,
  pace_alvo text,
  rpe_alvo integer DEFAULT 6,
  estrutura_treino text,
  status text DEFAULT 'Pendente',
  data_conclusao text,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. INDICES PARA PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_workouts_user_id ON public.workouts(user_id);
CREATE INDEX IF NOT EXISTS idx_workouts_data ON public.workouts(data);
CREATE INDEX IF NOT EXISTS idx_schedules_user_id ON public.schedules(user_id);
CREATE INDEX IF NOT EXISTS idx_schedules_status ON public.schedules(status);

-- 5. ROW LEVEL SECURITY (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.schedules ENABLE ROW LEVEL SECURITY;

-- 6. POLICIES
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE tablename = 'profiles' AND policyname = 'Users can access own profile'
  ) THEN
    CREATE POLICY "Users can access own profile" ON public.profiles FOR ALL USING (auth.uid() = id);
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE tablename = 'workouts' AND policyname = 'Users can access own workouts'
  ) THEN
    CREATE POLICY "Users can access own workouts" ON public.workouts FOR ALL USING (auth.uid() = user_id);
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE tablename = 'schedules' AND policyname = 'Users can access own schedules'
  ) THEN
    CREATE POLICY "Users can access own schedules" ON public.schedules FOR ALL USING (auth.uid() = user_id);
  END IF;
END $$;

-- 7. GRANT PERMISSIONS
GRANT ALL ON TABLE public.profiles TO authenticated;
GRANT ALL ON TABLE public.profiles TO service_role;
GRANT ALL ON TABLE public.workouts TO authenticated;
GRANT ALL ON TABLE public.workouts TO service_role;
GRANT ALL ON TABLE public.schedules TO authenticated;
GRANT ALL ON TABLE public.schedules TO service_role;
"""

def run_migration():
    print(f"Conectando a {DB_HOST}:5432...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=5432,
        dbname="postgres",
        user="postgres",
        password=DB_PASSWORD,
        connect_timeout=10,
    )
    conn.autocommit = True
    cur = conn.cursor()
    print("Executando DDL no Supabase PostgreSQL...")
    cur.execute(MIGRATION_SQL)
    print("Migração concluída com sucesso!")
    
    # Valida tabelas
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cur.fetchall()
    print("Tabelas no schema 'public':", [t[0] for t in tables])
    cur.close()
    conn.close()

if __name__ == "__main__":
    run_migration()
