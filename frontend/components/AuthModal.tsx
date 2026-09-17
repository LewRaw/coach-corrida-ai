'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Activity, Lock, Mail, User as UserIcon, ArrowRight, Sparkles } from 'lucide-react';

export default function AuthModal() {
  const { signIn, signUp, setDemoMode } = useAuth();
  const [tab, setTab] = useState<'login' | 'register'>('login');
  
  // Login form state
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register form state
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
    <div className="min-h-screen flex items-center justify-center p-4 bg-background">
      <div className="w-full max-w-md bg-surface border border-surface-border rounded-2xl p-6 shadow-2xl">
        {/* App Branding */}
        <div className="flex flex-col items-center text-center mb-6">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-primary-600 to-brand-emerald flex items-center justify-center shadow-lg mb-3">
            <Activity className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Coach AI</h1>
          <p className="text-xs text-slate-400 mt-1">
            Assessoria Esportiva Inteligente & Periodização
          </p>
        </div>

        {/* Tab Selector */}
        <div className="flex rounded-xl bg-surface-card p-1 mb-5 border border-surface-border">
          <button
            type="button"
            onClick={() => {
              setTab('login');
              setErrorMessage(null);
            }}
            className={`flex-1 py-2.5 text-sm font-semibold rounded-lg transition-all min-h-[44px] ${
              tab === 'login'
                ? 'bg-primary-600 text-white shadow'
                : 'text-slate-400 hover:text-white'
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
            className={`flex-1 py-2.5 text-sm font-semibold rounded-lg transition-all min-h-[44px] ${
              tab === 'register'
                ? 'bg-primary-600 text-white shadow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Criar Conta
          </button>
        </div>

        {/* Error / Info messages */}
        {errorMessage && (
          <div className="mb-4 p-3 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs leading-relaxed">
            {errorMessage}
          </div>
        )}
        {infoMessage && (
          <div className="mb-4 p-3 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs leading-relaxed">
            {infoMessage}
          </div>
        )}

        {/* Login Form */}
        {tab === 'login' && (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                E-mail
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  placeholder="seu@email.com"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  className="w-full pl-10 pr-3 py-3 bg-surface-card border border-surface-border rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 min-h-[44px]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Senha
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  placeholder="Sua senha secreta"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  className="w-full pl-10 pr-3 py-3 bg-surface-card border border-surface-border rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 min-h-[44px]"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3.5 px-4 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-600 text-white font-bold rounded-xl text-sm transition-all shadow-lg flex items-center justify-center gap-2 min-h-[48px] disabled:opacity-50"
            >
              {submitting ? 'Verificando...' : 'Acessar Treinos'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}

        {/* Register Form */}
        {tab === 'register' && (
          <form onSubmit={handleRegister} className="space-y-3.5">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Nome Completo
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <UserIcon className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  required
                  placeholder="Seu nome"
                  value={regNome}
                  onChange={(e) => setRegNome(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 bg-surface-card border border-surface-border rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 min-h-[44px]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                E-mail
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  placeholder="seu@email.com"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 bg-surface-card border border-surface-border rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 min-h-[44px]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Senha (mínimo 6 caracteres)
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  placeholder="Escolha uma senha"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 bg-surface-card border border-surface-border rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 min-h-[44px]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Confirmar Senha
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  placeholder="Repita a senha"
                  value={regConfirmPassword}
                  onChange={(e) => setRegConfirmPassword(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 bg-surface-card border border-surface-border rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 min-h-[44px]"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3.5 px-4 bg-gradient-to-r from-brand-emerald to-primary-600 hover:from-primary-600 hover:to-brand-emerald text-white font-bold rounded-xl text-sm transition-all shadow-lg flex items-center justify-center gap-2 min-h-[48px] disabled:opacity-50"
            >
              {submitting ? 'Cadastrando...' : 'Cadastrar Atleta'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}

        {/* Demo / Offline Preview Mode */}
        <div className="mt-6 pt-4 border-t border-surface-border text-center">
          <button
            type="button"
            onClick={() => setDemoMode(true)}
            className="w-full py-2.5 px-3 bg-surface-card hover:bg-surface-card-hover border border-primary-500/30 text-primary-100 rounded-xl text-xs font-medium transition-colors flex items-center justify-center gap-2 min-h-[44px]"
          >
            <Sparkles className="w-4 h-4 text-brand-emerald" />
            Acessar Atleta Demo (Visualização Rápida)
          </button>
          <p className="text-[11px] text-slate-500 mt-2">
            Permite testar o painel PWA e registrar conclusão de treinos imediatamente.
          </p>
        </div>
      </div>
    </div>
  );
}
