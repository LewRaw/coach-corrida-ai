'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useTheme } from '@/context/ThemeContext';
import { Activity, Lock, Mail, User as UserIcon, ArrowRight, Sparkles, Sun, Moon } from 'lucide-react';

export default function AuthModal() {
  const { signIn, signUp, setDemoMode } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [tab, setTab] = useState<'login' | 'register'>('login');

  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  const [regNome, setRegNome] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirmPassword, setRegConfirmPassword] = useState('');

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

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50 dark:bg-[#0b0f0e] transition-colors duration-200">
      <div className="w-full max-w-sm bg-white dark:bg-[#141d18] border border-slate-200 dark:border-[#23312a] rounded-3xl p-6 sm:p-7 shadow-xl">
        {/* Top right theme switch */}
        <div className="flex justify-end mb-2">
          <button
            onClick={toggleTheme}
            aria-label="Alternar tema"
            className="p-2 rounded-2xl bg-slate-100 dark:bg-[#1a2520] text-slate-500 dark:text-slate-400 hover:text-emerald-500 transition-colors"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
          </button>
        </div>

        {/* App Branding */}
        <div className="flex flex-col items-center text-center mb-6">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20 mb-3 text-white">
            <Activity className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">Coach AI</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Assessoria Esportiva & Periodização Inteligente
          </p>
        </div>

        {/* Tab Selector */}
        <div className="flex rounded-full bg-slate-100 dark:bg-[#0e1411] p-1 mb-5 border border-slate-200 dark:border-[#1d2922]">
          <button
            type="button"
            onClick={() => {
              setTab('login');
              setErrorMessage(null);
            }}
            className={`flex-1 py-2 text-xs font-bold rounded-full transition-all min-h-[38px] ${
              tab === 'login'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
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
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Criar Conta
          </button>
        </div>

        {/* Error / Info messages */}
        {errorMessage && (
          <div className="mb-4 p-3 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/40 text-rose-700 dark:text-rose-300 text-xs leading-relaxed">
            {errorMessage}
          </div>
        )}
        {infoMessage && (
          <div className="mb-4 p-3 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/40 text-emerald-700 dark:text-emerald-300 text-xs leading-relaxed">
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
                  className="w-full pl-10 pr-3 py-2.5 bg-slate-50 dark:bg-[#0e1411] border border-slate-200 dark:border-[#23312a] rounded-2xl text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:border-emerald-500 min-h-[44px]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Senha
              </label>
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
                  className="w-full pl-10 pr-3 py-2.5 bg-slate-50 dark:bg-[#0e1411] border border-slate-200 dark:border-[#23312a] rounded-2xl text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:border-emerald-500 min-h-[44px]"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-2xl text-sm transition-all shadow-md shadow-emerald-600/20 flex items-center justify-center gap-2 min-h-[46px] disabled:opacity-50 active:scale-[0.99]"
            >
              {submitting ? 'Verificando...' : 'Acessar Treinos'}
              <ArrowRight className="w-4 h-4" />
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
                  className="w-full pl-10 pr-3 py-2 bg-slate-50 dark:bg-[#0e1411] border border-slate-200 dark:border-[#23312a] rounded-2xl text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:border-emerald-500 min-h-[44px]"
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
                  className="w-full pl-10 pr-3 py-2 bg-slate-50 dark:bg-[#0e1411] border border-slate-200 dark:border-[#23312a] rounded-2xl text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:border-emerald-500 min-h-[44px]"
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
                  className="w-full pl-10 pr-3 py-2 bg-slate-50 dark:bg-[#0e1411] border border-slate-200 dark:border-[#23312a] rounded-2xl text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:border-emerald-500 min-h-[44px]"
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
                  className="w-full pl-10 pr-3 py-2 bg-slate-50 dark:bg-[#0e1411] border border-slate-200 dark:border-[#23312a] rounded-2xl text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:border-emerald-500 min-h-[44px]"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-2xl text-sm transition-all shadow-md shadow-emerald-600/20 flex items-center justify-center gap-2 min-h-[46px] disabled:opacity-50 active:scale-[0.99]"
            >
              {submitting ? 'Cadastrando...' : 'Cadastrar Atleta'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}

        {/* Demo / Offline Preview Mode */}
        <div className="mt-5 pt-3 border-t border-slate-200 dark:border-[#23312a] text-center">
          <button
            type="button"
            onClick={() => setDemoMode(true)}
            className="w-full py-2.5 px-3 bg-slate-100 hover:bg-slate-200 dark:bg-[#0e1411] dark:hover:bg-[#141d18] border border-slate-200 dark:border-[#1d2922] text-slate-700 dark:text-slate-300 rounded-2xl text-xs font-semibold transition-colors flex items-center justify-center gap-2 min-h-[42px]"
          >
            <Sparkles className="w-4 h-4 text-emerald-500" />
            Acessar Atleta Demo (Visualização Rápida)
          </button>
        </div>
      </div>
    </div>
  );
}
