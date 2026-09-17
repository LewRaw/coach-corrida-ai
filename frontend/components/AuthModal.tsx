'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useTheme } from '@/context/ThemeContext';
import { Activity, Lock, Mail, User as UserIcon, ArrowRight, Sparkles, Sun, Moon } from 'lucide-react';

export default function AuthModal() {
  const { signIn, signUp, setDemoMode } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [tab, setTab] = useState<'login' | 'register' | 'recovery'>('login');

  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  const [regNome, setRegNome] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirmPassword, setRegConfirmPassword] = useState('');

  const [recoveryEmail, setRecoveryEmail] = useState('');

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setInfoMessage(null);

    if (!loginEmail.trim() || !loginPassword.trim()) {
      setErrorMessage('Informe seu e-mail e senha cadastrados.');
      return;
    }

    setSubmitting(true);
    const result = await signIn(loginEmail.trim(), loginPassword);
    setSubmitting(false);

    if (!result.success) {
      setErrorMessage(result.error || 'E-mail ou senha incorretos.');
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setInfoMessage(null);

    if (!regNome.trim()) {
      setErrorMessage('Por favor, informe seu nome completo.');
      return;
    }
    if (!regEmail.trim()) {
      setErrorMessage('Por favor, informe um endereço de e-mail válido.');
      return;
    }
    if (regPassword.length < 6) {
      setErrorMessage('A senha deve conter pelo menos 6 caracteres.');
      return;
    }
    if (regPassword !== regConfirmPassword) {
      setErrorMessage('As senhas digitadas não coincidem.');
      return;
    }

    setSubmitting(true);
    const result = await signUp(regNome.trim(), regEmail.trim(), regPassword);
    setSubmitting(false);

    if (!result.success) {
      setErrorMessage(result.error || 'Falha ao realizar cadastro.');
    } else {
      setInfoMessage('Conta criada com sucesso! Redirecionando para seu painel...');
    }
  };

  const handleRecovery = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setInfoMessage(null);

    if (!recoveryEmail.trim()) {
      setErrorMessage('Por favor, informe o seu e-mail cadastrado.');
      return;
    }

    setSubmitting(true);
    try {
      const redirectUrl =
        typeof window !== 'undefined'
          ? `${window.location.origin}/reset-password`
          : 'https://coach-corrida-ai.vercel.app/reset-password';

      const { error } = await (await import('@/lib/supabase')).supabase.auth.resetPasswordForEmail(
        recoveryEmail.trim(),
        { redirectTo: redirectUrl }
      );

      if (error) {
        setErrorMessage(error.message || 'Erro ao enviar e-mail de recuperação.');
      } else {
        setInfoMessage('Link de redefinição enviado com sucesso! Verifique sua caixa de entrada e spam.');
      }
    } catch (err: any) {
      setErrorMessage('Falha ao conectar com o serviço de autenticação.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#F5F6F8] dark:bg-[#000000] transition-colors duration-150 text-slate-900 dark:text-white">
      <div className="w-full max-w-sm bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] rounded-3xl p-6 sm:p-7 shadow-xl">
        {/* Top right theme switch */}
        <div className="flex justify-end mb-2">
          <button
            onClick={toggleTheme}
            aria-label="Alternar tema"
            className="p-2 rounded-2xl bg-slate-100 dark:bg-[#202020] text-slate-500 dark:text-slate-400 hover:text-[#11C76F] transition-colors"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
          </button>
        </div>

        {/* App Branding */}
        <div className="flex flex-col items-center text-center mb-6">
          <div className="w-14 h-14 rounded-2xl bg-[#11C76F] flex items-center justify-center shadow-xs mb-3 text-white">
            <Activity className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight">Coach AI</h1>
          <p className="text-xs text-slate-500 dark:text-[#8E8E93] mt-1">
            Assessoria Esportiva & Periodização Inteligente
          </p>
        </div>

        {/* Tab Selector */}
        <div className="flex rounded-full bg-slate-100 dark:bg-[#1c1c1c] p-1 mb-5 border border-slate-200 dark:border-[#262626]">
          <button
            type="button"
            onClick={() => {
              setTab('login');
              setErrorMessage(null);
            }}
            className={`flex-1 py-2 text-xs font-bold rounded-full transition-all min-h-[38px] ${
              tab === 'login'
                ? 'bg-[#11C76F] text-white shadow-xs'
                : 'text-slate-500 dark:text-[#8E8E93] hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Entrar
          </button>
          <button
            type="button"
            onClick={() => {
              setTab('register');
              setErrorMessage(null);
            }}
            className={`flex-1 py-2 text-xs font-bold rounded-full transition-all min-h-[38px] ${
              tab === 'register'
                ? 'bg-[#11C76F] text-white shadow-xs'
                : 'text-slate-500 dark:text-[#8E8E93] hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Criar Conta
          </button>
          <button
            type="button"
            onClick={() => {
              setTab('recovery');
              setErrorMessage(null);
            }}
            className={`flex-1 py-2 text-xs font-bold rounded-full transition-all min-h-[38px] ${
              tab === 'recovery'
                ? 'bg-[#11C76F] text-white shadow-xs'
                : 'text-slate-500 dark:text-[#8E8E93] hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Recuperar
          </button>
        </div>

        {/* Error / Info messages */}
        {errorMessage && (
          <div className="mb-4 p-3 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/40 text-rose-700 dark:text-rose-300 text-xs leading-relaxed">
            {errorMessage}
          </div>
        )}
        {infoMessage && (
          <div className="mb-4 p-3 rounded-2xl bg-[#11C76F]/10 border border-[#11C76F]/30 text-[#11C76F] text-xs leading-relaxed">
            {infoMessage}
          </div>
        )}

        {/* Login Form */}
        {tab === 'login' && (
          <form onSubmit={handleLogin} className="space-y-3.5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                E-mail
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  placeholder="seu@email.com"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] rounded-2xl text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:border-[#11C76F] min-h-[44px]"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  Senha
                </label>
                <button
                  type="button"
                  onClick={() => setTab('recovery')}
                  className="text-[11px] font-semibold text-[#11C76F] hover:underline"
                >
                  Esqueceu a senha?
                </button>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  placeholder="Sua senha secreta"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] rounded-2xl text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:border-[#11C76F] min-h-[44px]"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 px-4 bg-[#11C76F] hover:bg-[#0ea85d] active:scale-[0.99] text-white font-bold rounded-2xl text-sm transition-all shadow-xs flex items-center justify-center gap-2 min-h-[46px] disabled:opacity-50"
            >
              {submitting ? 'Verificando...' : 'Acessar Treinos'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}

        {/* Recovery Form */}
        {tab === 'recovery' && (
          <form onSubmit={handleRecovery} className="space-y-3.5">
            <p className="text-xs text-slate-500 dark:text-[#8E8E93] leading-relaxed">
              Digite seu e-mail cadastrado. Enviaremos um link seguro para você redefinir sua senha.
            </p>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                E-mail Cadastrado
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  placeholder="seu@email.com"
                  value={recoveryEmail}
                  onChange={(e) => setRecoveryEmail(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] rounded-2xl text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:border-[#11C76F] min-h-[44px]"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 px-4 bg-[#11C76F] hover:bg-[#0ea85d] active:scale-[0.99] text-white font-bold rounded-2xl text-sm transition-all shadow-xs flex items-center justify-center gap-2 min-h-[46px] disabled:opacity-50"
            >
              {submitting ? 'Enviando link...' : 'Enviar Link de Recuperação'}
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={() => setTab('login')}
              className="w-full py-2 text-xs font-semibold text-slate-500 hover:text-slate-900 dark:text-[#8E8E93] dark:hover:text-white transition-colors"
            >
              Voltar para o Login
            </button>
          </form>
        )}

        {/* Register Form */}
        {tab === 'register' && (
          <form onSubmit={handleRegister} className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Nome Completo
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <UserIcon className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  required
                  placeholder="Seu nome"
                  value={regNome}
                  onChange={(e) => setRegNome(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] rounded-2xl text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:border-[#11C76F] min-h-[44px]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                E-mail
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  placeholder="seu@email.com"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] rounded-2xl text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:border-[#11C76F] min-h-[44px]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Senha (mínimo 6 caracteres)
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  placeholder="Escolha uma senha"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] rounded-2xl text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:border-[#11C76F] min-h-[44px]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Confirmar Senha
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  placeholder="Repita a senha"
                  value={regConfirmPassword}
                  onChange={(e) => setRegConfirmPassword(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] rounded-2xl text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:border-[#11C76F] min-h-[44px]"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 px-4 bg-[#11C76F] hover:bg-[#0ea85d] active:scale-[0.99] text-white font-bold rounded-2xl text-sm transition-all shadow-xs flex items-center justify-center gap-2 min-h-[46px] disabled:opacity-50"
            >
              {submitting ? 'Cadastrando...' : 'Cadastrar Atleta'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}

        {/* Demo / Offline Preview Mode */}
        <div className="mt-5 pt-3 border-t border-slate-100 dark:border-[#262626] text-center">
          <button
            type="button"
            onClick={() => setDemoMode(true)}
            className="w-full py-2.5 px-3 bg-slate-100 hover:bg-slate-200 dark:bg-[#1c1c1c] dark:hover:bg-[#252525] border border-slate-200 dark:border-[#262626] text-slate-700 dark:text-slate-300 rounded-2xl text-xs font-semibold transition-colors flex items-center justify-center gap-2 min-h-[42px]"
          >
            <Sparkles className="w-4 h-4 text-[#11C76F]" />
            Acessar Atleta Demo (Visualização Rápida)
          </button>
        </div>
      </div>
    </div>
  );
}
