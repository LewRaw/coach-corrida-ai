'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { useToast } from '@/context/ToastContext';
import { Lock, Save, ArrowLeft, Loader2, CheckCircle2 } from 'lucide-react';

export default function ResetPasswordPage() {
  const router = useRouter();
  const { showToast } = useToast();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionChecking, setSessionChecking] = useState(true);
  const [hasValidSession, setHasValidSession] = useState(false);

  useEffect(() => {
    async function checkSession() {
      // Supabase recovers session from URL hash tokens (#access_token=...&type=recovery) automatically
      const { data } = await supabase.auth.getSession();
      if (data?.session) {
        setHasValidSession(true);
      } else {
        // Also listen to onAuthStateChange for PASSWORD_RECOVERY event
        const { data: sub } = supabase.auth.onAuthStateChange((event, session) => {
          if (event === 'PASSWORD_RECOVERY' || session) {
            setHasValidSession(true);
          }
        });
        return () => sub.subscription.unsubscribe();
      }
      setSessionChecking(false);
    }
    checkSession();
  }, []);

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password.length < 6) {
      showToast('A senha deve ter no mínimo 6 caracteres.', 'error');
      return;
    }
    if (password !== confirmPassword) {
      showToast('As senhas digitadas não coincidem.', 'error');
      return;
    }

    setLoading(true);
    try {
      const { error } = await supabase.auth.updateUser({ password });
      if (error) {
        showToast(error.message || 'Erro ao redefinir senha.', 'error');
      } else {
        showToast('Nova senha salva com sucesso! Entrando no app...', 'success');
        setTimeout(() => {
          router.push('/');
        }, 1500);
      }
    } catch (err: any) {
      showToast('Erro de conexão ao atualizar senha.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#F5F6F8] dark:bg-[#000000] text-slate-900 dark:text-white transition-colors duration-150">
      <div className="w-full max-w-sm bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] rounded-3xl p-6 sm:p-7 shadow-xl">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-2xl bg-[#11C76F] text-white flex items-center justify-center shadow-xs">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-extrabold tracking-tight">Redefinir Senha</h1>
            <p className="text-xs text-slate-500 dark:text-[#8E8E93]">Coach AI Assessoria</p>
          </div>
        </div>

        <form onSubmit={handleReset} className="space-y-4 text-xs sm:text-sm">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Nova Senha
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <Lock className="w-4 h-4" />
              </div>
              <input
                type="password"
                required
                placeholder="Mínimo 6 caracteres"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-3 py-2.5 bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] rounded-2xl text-slate-900 dark:text-white text-xs sm:text-sm focus:outline-none focus:border-[#11C76F] min-h-[44px]"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Confirmar Nova Senha
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <CheckCircle2 className="w-4 h-4" />
              </div>
              <input
                type="password"
                required
                placeholder="Repita sua nova senha"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full pl-10 pr-3 py-2.5 bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] rounded-2xl text-slate-900 dark:text-white text-xs sm:text-sm focus:outline-none focus:border-[#11C76F] min-h-[44px]"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-[#11C76F] hover:bg-[#0ea85d] active:scale-[0.99] text-white font-bold rounded-2xl text-sm transition-all shadow-xs flex items-center justify-center gap-2 min-h-[46px] disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {loading ? 'Salvando...' : 'Salvar Nova Senha'}
          </button>

          <button
            type="button"
            onClick={() => router.push('/')}
            className="w-full py-2.5 text-xs text-slate-500 hover:text-slate-900 dark:text-[#8E8E93] dark:hover:text-white transition-colors flex items-center justify-center gap-1.5"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Voltar para o Início
          </button>
        </form>
      </div>
    </div>
  );
}
