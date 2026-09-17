'use client';

import React, { useState } from 'react';
import { X, Check, Save, Sliders, Target, Award, Calendar, Sparkles } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

interface EditProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const TODAS_MODALIDADES = [
  'Corrida de Rua',
  'Ciclismo / Bike',
  'Natação',
  'Futebol (Society / Campo / Futsal)',
  'Basquete (Quadra / Meia Quadra)',
  'Vôlei (Quadra / Areia / Futevôlei)',
  'Musculação / Fortalecimento',
  'Crossfit / Funcional',
  'Triatlo (Swim, Bike & Run)',
  'Outro Esporte',
];

const NIVEIS_EXPERIENCIA = ['Iniciante', 'Intermediário', 'Avançado', 'Competitivo'];

const OBJETIVOS_LIST = [
  'Construção de Base Aeróbica (Zona 2)',
  'Primeiros 5 km ou 10 km',
  'Estreia em Meia Maratona (21.1 km)',
  'Preparação para Maratona (42.2 km)',
  'Triatlo Sprint / Olímpico',
  'Meio Ironman (70.3) / Ironman',
  'Condicionamento Físico e Queima de Gordura',
  'Preparação Física para Futebol / Coletivos',
];

export default function EditProfileModal({ isOpen, onClose }: EditProfileModalProps) {
  const { profile, updateProfile } = useAuth();

  const [esportes, setEsportes] = useState<string[]>(
    profile?.esportes_ativos?.length ? profile.esportes_ativos : ['Corrida de Rua']
  );
  const [nivel, setNivel] = useState(profile?.nivel_experiencia || 'Intermediário');
  const [dias, setDias] = useState(profile?.dias_disponiveis || 4);
  const [meta, setMeta] = useState(profile?.objetivo_principal || 'Construção de Base Aeróbica (Zona 2)');
  const [saving, setSaving] = useState(false);

  if (!isOpen) return null;

  const toggleSport = (sport: string) => {
    if (esportes.includes(sport)) {
      if (esportes.length === 1) return; // manter ao menos 1
      setEsportes(esportes.filter((s) => s !== sport));
    } else {
      setEsportes([...esportes, sport]);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const ok = await updateProfile({
        esportes_ativos: esportes,
        nivel_experiencia: nivel,
        dias_disponiveis: dias,
        objetivo_principal: meta,
      });
      if (ok) {
        alert('Perfil e modalidades atualizados com sucesso!');
        onClose();
      } else {
        alert('Não foi possível salvar no momento. Tente novamente.');
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="w-full max-w-lg max-h-[92vh] overflow-y-auto bg-white dark:bg-[#141414] border-t sm:border border-slate-200 dark:border-[#262626] rounded-t-3xl sm:rounded-3xl p-5 sm:p-6 shadow-2xl text-slate-900 dark:text-white"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-4 pb-3 border-b border-slate-100 dark:border-[#222222]">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-2xl bg-[#11C76F] text-white flex items-center justify-center shadow-xs">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-extrabold tracking-tight">Ajustar Esportes & Metas</h2>
              <p className="text-xs text-slate-500 dark:text-[#8E8E93]">Personalize seu perfil atlético</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-2xl bg-slate-100 dark:bg-[#202020] text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSave} className="space-y-4 text-xs sm:text-sm">
          {/* 1. Modalidades Ativas */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-[#8E8E93] mb-1.5 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-[#11C76F]" />
              Suas modalidades ativas (selecione as que pratica):
            </label>
            <div className="flex flex-wrap gap-1.5">
              {TODAS_MODALIDADES.map((sport) => {
                const selected = esportes.includes(sport);
                return (
                  <button
                    key={sport}
                    type="button"
                    onClick={() => toggleSport(sport)}
                    className={`px-3 py-2 rounded-xl text-xs font-semibold transition-all border ${
                      selected
                        ? 'bg-[#11C76F] text-white border-[#11C76F] shadow-xs'
                        : 'bg-slate-50 dark:bg-[#1c1c1c] text-slate-700 dark:text-[#8E8E93] border-slate-200 dark:border-[#262626] hover:border-slate-300'
                    }`}
                  >
                    {selected && <Check className="w-3 h-3 inline-block mr-1 -mt-0.5" />}
                    {sport}
                  </button>
                );
              })}
            </div>
          </div>

          {/* 2. Nível de Experiência */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-[#8E8E93] mb-1.5 flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5 text-amber-500" />
              Nível de Experiência:
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
              {NIVEIS_EXPERIENCIA.map((n) => (
                <button
                  key={n}
                  type="button"
                  onClick={() => setNivel(n)}
                  className={`py-2 px-2 rounded-xl text-xs font-bold border transition-all ${
                    nivel === n
                      ? 'bg-[#11C76F] text-white border-[#11C76F]'
                      : 'bg-slate-50 dark:bg-[#1c1c1c] text-slate-700 dark:text-[#8E8E93] border-slate-200 dark:border-[#262626]'
                  }`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>

          {/* 3. Dias Disponíveis por Semana */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-[#8E8E93] flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-[#11C76F]" />
                Dias disponíveis por semana:
              </label>
              <span className="font-extrabold text-xs text-[#11C76F]">{dias} dias/semana</span>
            </div>
            <div className="grid grid-cols-6 gap-1.5">
              {[2, 3, 4, 5, 6, 7].map((num) => (
                <button
                  key={num}
                  type="button"
                  onClick={() => setDias(num)}
                  className={`py-2 rounded-xl font-extrabold text-xs transition-all ${
                    dias === num
                      ? 'bg-[#11C76F] text-white shadow-xs'
                      : 'bg-slate-50 dark:bg-[#1c1c1c] text-slate-700 dark:text-[#8E8E93] border border-slate-200 dark:border-[#262626]'
                  }`}
                >
                  {num}d
                </button>
              ))}
            </div>
          </div>

          {/* 4. Objetivo Esportivo Principal */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-[#8E8E93] mb-1.5 flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5 text-[#11C76F]" />
              Objetivo Esportivo Principal:
            </label>
            <select
              value={meta}
              onChange={(e) => setMeta(e.target.value)}
              className="w-full p-3 rounded-2xl bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] text-slate-900 dark:text-white text-xs sm:text-sm focus:outline-none focus:border-[#11C76F]"
            >
              {OBJETIVOS_LIST.map((m, i) => (
                <option key={i} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>

          {/* Actions */}
          <div className="pt-2 flex items-center gap-2.5">
            <button
              type="submit"
              disabled={saving}
              className="flex-1 py-3.5 px-4 rounded-2xl bg-[#11C76F] hover:bg-[#0ea85d] active:scale-[0.99] text-white font-bold text-sm shadow-xs transition-all flex items-center justify-center gap-2 disabled:opacity-50 min-h-[48px]"
            >
              <Save className="w-4 h-4" />
              {saving ? 'Salvando...' : 'Salvar Alterações'}
            </button>
            <button
              type="button"
              onClick={onClose}
              disabled={saving}
              className="px-5 py-3.5 rounded-2xl bg-slate-100 hover:bg-slate-200 dark:bg-[#202020] dark:hover:bg-[#282828] text-slate-700 dark:text-white font-bold text-xs transition-colors min-h-[48px]"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
