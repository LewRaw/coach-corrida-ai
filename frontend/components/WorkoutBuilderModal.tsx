'use client';

import React, { useState } from 'react';
import { X, Sparkles, Loader2, Calendar, Target, Activity, Flame, ShieldAlert } from 'lucide-react';
import { generateWeeklyPlanAction, PlanGenerationParams } from '@/app/actions/ai-actions';
import { useToast } from '@/context/ToastContext';

interface WorkoutBuilderModalProps {
  isOpen: boolean;
  onClose: () => void;
  userId: string;
  onSuccess: () => void;
}

const ARQUITETURAS = [
  { id: 'corrida', label: 'Corrida de Rua', desc: 'Quilometragem, ritmo e evolução aeróbica' },
  { id: 'multi', label: 'Multi-Esportes', desc: 'Corrida, bike, natação e fortalecimento' },
  { id: 'triatlo', label: 'Triatlo', desc: 'Swim, Bike & Run + transições' },
  { id: 'coletivos', label: 'Esportes Coletivos', desc: 'Futebol, basquete ou vôlei + cardio' },
];

const OBJETIVOS_POR_ARQUITETURA: Record<string, string[]> = {
  corrida: [
    'Construção Sólida de Base Aeróbica (Zona 2)',
    'Recorde Pessoal nos 5 km',
    'Sub 50 minutos nos 10 km',
    'Estreia em Meia Maratona (21.1 km)',
    'Preparação Completa para Maratona (42.2 km)',
    'Condicionamento Geral e Saúde Cardiovascular',
  ],
  multi: [
    'Equilíbrio Global: Resistência Aeróbica + Força Funcional',
    'Prioridade Corrida com Manutenção das Outras Modalidades',
    'Prioridade Ciclismo com Treinos Cruzados de Suporte',
    'Preservação Muscular e Condicionamento para Jogos Coletivos',
    'Ênfase em Fortalecimento e Prevenção de Lesões',
    'Condicionamento Geral e Queima Calórica',
  ],
  triatlo: [
    'Triatlo Sprint (750m / 20km / 5km)',
    'Triatlo Olímpico / Standard (1.500m / 40km / 10km)',
    'Meio Ironman 70.3 (1.9km / 90km / 21.1km)',
    'Ironman Completo 140.6 (3.8km / 180km / 42.2km)',
    'Transição e Brick (Adaptação neuromuscular bike-corrida)',
  ],
  coletivos: [
    'Fôlego e Resistência para suportar a partida em alta intensidade',
    'Explosão e Agilidade em tiros curtos com rápida recuperação',
    'Prevenção de Lesões em adutores, isquiotibiais e joelhos',
    'Condicionamento Geral intercalando corridas e partidas',
  ],
};

const DIAS_SEMANA_OPCOES = ['Domingo', 'Sábado', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Segunda-feira', 'Terça-feira'];

const HORIZONTES = [
  'Microciclo Imediato (Próximos 7 dias)',
  'Bloco de Base Aeróbica (4 Semanas)',
  'Polimento Pré-Competição (2 Semanas)',
];

export default function WorkoutBuilderModal({
  isOpen,
  onClose,
  userId,
  onSuccess,
}: WorkoutBuilderModalProps) {
  const { showToast } = useToast();
  const [arquiteturaId, setArquiteturaId] = useState<'corrida' | 'multi' | 'triatlo' | 'coletivos'>('corrida');
  const [objetivo, setObjetivo] = useState(OBJETIVOS_POR_ARQUITETURA['corrida'][0]);
  const [diasSemana, setDiasSemana] = useState(4);
  const [diaLongao, setDiaLongao] = useState('Sábado');
  const [cicloHorizonte, setCicloHorizonte] = useState(HORIZONTES[0]);
  const [obsLesoes, setObsLesoes] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSelectArquitetura = (id: 'corrida' | 'multi' | 'triatlo' | 'coletivos') => {
    setArquiteturaId(id);
    setObjetivo(OBJETIVOS_POR_ARQUITETURA[id][0]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const selectedArq = ARQUITETURAS.find((a) => a.id === arquiteturaId)?.label || 'Corrida de Rua';
      const esportesSelecionados =
        arquiteturaId === 'corrida'
          ? ['Corrida de Rua']
          : arquiteturaId === 'multi'
          ? ['Corrida de Rua', 'Ciclismo / Bike', 'Musculação / Fortalecimento']
          : arquiteturaId === 'triatlo'
          ? ['Natação', 'Ciclismo', 'Corrida']
          : ['Futebol', 'Corrida de Rua', 'Musculação'];

      const params: PlanGenerationParams = {
        userId: userId || 'demo-athlete-001',
        tipoModalidade: selectedArq,
        esportesSelecionados,
        objetivoSelecionado: objetivo,
        diasSemana,
        diaLongao,
        cicloHorizonte,
        obsLesoes,
      };

      const res = await generateWeeklyPlanAction(params);

      if (res.success) {
        showToast('✨ Planilha gerada com sucesso pela IA para os próximos 7 dias!', 'success');
        onSuccess();
        onClose();
      } else {
        showToast(res.error || 'Erro ao prescrever treinos. Tente novamente.', 'error');
      }
    } catch (err: any) {
      showToast('Erro de conexão ao gerar planilha.', 'error');
    } finally {
      setLoading(false);
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
            <div className="w-10 h-10 rounded-2xl bg-[#11C76F] text-white flex items-center justify-center shadow-sm">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-extrabold tracking-tight">Montador de Treinos com IA</h2>
              <p className="text-xs text-slate-500 dark:text-[#8E8E93]">Personalização de microciclo esportivo</p>
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

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-xs sm:text-sm">
          {/* 1. Arquitetura do Planejamento */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-[#8E8E93] mb-2 flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-[#11C76F]" />
              1. Arquitetura do Planejamento
            </label>
            <div className="grid grid-cols-2 gap-2">
              {ARQUITETURAS.map((arq) => (
                <button
                  key={arq.id}
                  type="button"
                  onClick={() => handleSelectArquitetura(arq.id as any)}
                  className={`p-3 rounded-2xl text-left border transition-all ${
                    arquiteturaId === arq.id
                      ? 'border-[#11C76F] bg-[#11C76F]/10 dark:bg-[#11C76F]/15 font-bold text-slate-900 dark:text-white'
                      : 'border-slate-200 dark:border-[#262626] bg-slate-50 dark:bg-[#1c1c1c] text-slate-600 dark:text-[#8E8E93] hover:border-slate-300'
                  }`}
                >
                  <div className="font-bold text-xs">{arq.label}</div>
                  <div className="text-[10px] opacity-75 mt-0.5 line-clamp-1">{arq.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* 2. Foco / Objetivo da Semana */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-[#8E8E93] mb-1.5 flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5 text-[#11C76F]" />
              2. Foco da Semana
            </label>
            <select
              value={objetivo}
              onChange={(e) => setObjetivo(e.target.value)}
              className="w-full p-3 rounded-2xl bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] text-slate-900 dark:text-white text-xs sm:text-sm focus:outline-none focus:border-[#11C76F]"
            >
              {OBJETIVOS_POR_ARQUITETURA[arquiteturaId].map((obj, i) => (
                <option key={i} value={obj}>
                  {obj}
                </option>
              ))}
            </select>
          </div>

          {/* 3. Frequência Semanal (3 a 7 dias) */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-[#8E8E93] flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-[#11C76F]" />
                3. Frequência Semanal (dias de treino)
              </label>
              <span className="font-extrabold text-xs text-[#11C76F]">{diasSemana} dias ativos</span>
            </div>
            <div className="grid grid-cols-5 gap-1.5">
              {[3, 4, 5, 6, 7].map((num) => (
                <button
                  key={num}
                  type="button"
                  onClick={() => setDiasSemana(num)}
                  className={`py-2 rounded-xl font-extrabold text-xs transition-all ${
                    diasSemana === num
                      ? 'bg-[#11C76F] text-white shadow-sm'
                      : 'bg-slate-100 dark:bg-[#1c1c1c] text-slate-600 dark:text-[#8E8E93] border border-slate-200 dark:border-[#262626]'
                  }`}
                >
                  {num} dias
                </button>
              ))}
            </div>
          </div>

          {/* 4. Dia do Treino Chave / Longão & Período */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-[#8E8E93] mb-1.5 flex items-center gap-1.5">
                <Flame className="w-3.5 h-3.5 text-amber-500" />
                4. Dia do Treino Longo / Jogo
              </label>
              <select
                value={diaLongao}
                onChange={(e) => setDiaLongao(e.target.value)}
                className="w-full p-3 rounded-2xl bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] text-slate-900 dark:text-white text-xs sm:text-sm focus:outline-none focus:border-[#11C76F]"
              >
                {DIAS_SEMANA_OPCOES.map((dia, i) => (
                  <option key={i} value={dia}>
                    {dia}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-[#8E8E93] mb-1.5">
                5. Período do Planejamento
              </label>
              <select
                value={cicloHorizonte}
                onChange={(e) => setCicloHorizonte(e.target.value)}
                className="w-full p-3 rounded-2xl bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] text-slate-900 dark:text-white text-xs sm:text-sm focus:outline-none focus:border-[#11C76F]"
              >
                {HORIZONTES.map((h, i) => (
                  <option key={i} value={h}>
                    {h}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* 6. Observações, Dores ou Restrições */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-[#8E8E93] mb-1.5 flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5 text-rose-500" />
              6. Observações, Dores ou Restrições
            </label>
            <textarea
              rows={2}
              value={obsLesoes}
              onChange={(e) => setObsLesoes(e.target.value)}
              placeholder="Ex: Leve desconforto na panturrilha; prefiro correr pela manhã; quarta-feira não posso treinar."
              className="w-full p-3 rounded-2xl bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:border-[#11C76F]"
            />
          </div>

          {/* Action Buttons */}
          <div className="pt-2 flex items-center gap-2.5">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-3.5 px-4 rounded-2xl bg-[#11C76F] hover:bg-[#0ea85d] active:scale-[0.99] text-white font-bold text-sm shadow-md transition-all flex items-center justify-center gap-2 disabled:opacity-50 min-h-[48px]"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Prescrevendo Microciclo...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Gerar Planilha de Treinos
                </>
              )}
            </button>
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
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
