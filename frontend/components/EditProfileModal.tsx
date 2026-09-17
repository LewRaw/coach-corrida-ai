'use client';

import React, { useState, useEffect } from 'react';
import { X, Check, Save, Sliders, Target, Award, Calendar, Sparkles } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { useToast } from '@/context/ToastContext';

interface EditProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ModalidadeItem {
  id: string;
  label: string;
  emoji: string;
  keywords: string[];
}

const MODALIDADES_DISPONIVEIS: ModalidadeItem[] = [
  { id: 'corrida', label: 'Corrida de Rua', emoji: '🏃', keywords: ['corrida', 'maratona', 'running'] },
  { id: 'ciclismo', label: 'Ciclismo / Bike', emoji: '🚴', keywords: ['ciclismo', 'bike', 'bicicleta', 'cycling'] },
  { id: 'natacao', label: 'Natação', emoji: '🏊', keywords: ['natação', 'natacao', 'swimming', 'swim'] },
  { id: 'triatlo', label: 'Especialista em Triatlo', emoji: '🏊🚴🏃', keywords: ['triatlo', 'triathlon'] },
  { id: 'futebol', label: 'Futebol (Society / Futsal)', emoji: '⚽', keywords: ['futebol', 'futsal', 'society'] },
  { id: 'basquete', label: 'Basquete', emoji: '🏀', keywords: ['basquete', 'basketball'] },
  { id: 'volei', label: 'Vôlei', emoji: '🏐', keywords: ['vôlei', 'volei', 'futevôlei'] },
  { id: 'musculacao', label: 'Musculação / Fortalecimento', emoji: '🏋️', keywords: ['musculação', 'musculacao', 'fortalecimento', 'força'] },
];

const NIVEIS_EXPERIENCIA = ['Iniciante', 'Intermediário', 'Avançado', 'Competitivo'];

const OBJETIVOS_PADRAO = [
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
  const { showToast } = useToast();

  // Helper to check if a modalidade matches user profile strings
  const isSportMatching = (item: ModalidadeItem, userSports: string[]): boolean => {
    return userSports.some((us) => {
      const lowerUS = us.toLowerCase();
      if (lowerUS.includes(item.label.toLowerCase())) return true;
      return item.keywords.some((kw) => lowerUS.includes(kw));
    });
  };

  // State
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [nivel, setNivel] = useState('Intermediário');
  const [dias, setDias] = useState(4);
  const [meta, setMeta] = useState('Construção de Base Aeróbica (Zona 2)');
  const [availableMetas, setAvailableMetas] = useState<string[]>(OBJETIVOS_PADRAO);
  const [saving, setSaving] = useState(false);

  // Sync with profile whenever modal opens or profile changes
  useEffect(() => {
    if (!profile) return;

    const userSports = profile.esportes_ativos?.length ? profile.esportes_ativos : ['Corrida de Rua'];
    const matched = MODALIDADES_DISPONIVEIS.filter((item) => isSportMatching(item, userSports)).map(
      (item) => item.id
    );
    setSelectedIds(matched.length ? matched : ['corrida']);

    setNivel(profile.nivel_experiencia || 'Intermediário');
    setDias(profile.dias_disponiveis || 4);

    const currentGoal = profile.objetivo_principal || OBJETIVOS_PADRAO[0];
    if (!OBJETIVOS_PADRAO.includes(currentGoal)) {
      setAvailableMetas([currentGoal, ...OBJETIVOS_PADRAO]);
    } else {
      setAvailableMetas(OBJETIVOS_PADRAO);
    }
    setMeta(currentGoal);
  }, [profile, isOpen]);

  if (!isOpen) return null;

  const toggleSport = (id: string) => {
    if (selectedIds.includes(id)) {
      if (selectedIds.length === 1) {
        showToast('Mantenha ao menos uma modalidade ativa.', 'info');
        return;
      }
      setSelectedIds(selectedIds.filter((s) => s !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      // Map selected IDs back to standard labels
      const esportesFinal = MODALIDADES_DISPONIVEIS.filter((item) =>
        selectedIds.includes(item.id)
      ).map((item) => item.label);

      const ok = await updateProfile({
        esportes_ativos: esportesFinal.length ? esportesFinal : ['Corrida de Rua'],
        nivel_experiencia: nivel,
        dias_disponiveis: dias,
        objetivo_principal: meta,
      });

      if (ok) {
        showToast('Perfil e modalidades salvos com sucesso!', 'success');
        onClose();
      } else {
        showToast('Não foi possível salvar no momento. Tente novamente.', 'error');
      }
    } catch (err: any) {
      showToast(err.message || 'Erro ao atualizar perfil.', 'error');
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
              {MODALIDADES_DISPONIVEIS.map((sport) => {
                const selected = selectedIds.includes(sport.id);
                return (
                  <button
                    key={sport.id}
                    type="button"
                    onClick={() => toggleSport(sport.id)}
                    className={`px-3 py-2 rounded-xl text-xs font-semibold transition-all border flex items-center gap-1.5 ${
                      selected
                        ? 'bg-[#11C76F] text-white border-[#11C76F] shadow-xs'
                        : 'bg-slate-50 dark:bg-[#1c1c1c] text-slate-700 dark:text-[#8E8E93] border-slate-200 dark:border-[#262626] hover:border-slate-300'
                    }`}
                  >
                    <span>{sport.emoji}</span>
                    <span>{sport.label}</span>
                    {selected && <Check className="w-3.5 h-3.5 inline-block ml-0.5" />}
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
              {availableMetas.map((m, i) => (
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
