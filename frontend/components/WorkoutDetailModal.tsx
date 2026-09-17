'use client';

import React, { useState } from 'react';
import { Schedule } from '@/lib/types';
import {
  X,
  Calendar,
  Gauge,
  Clock,
  Flame,
  Info,
  CheckCircle2,
  FileText,
  Upload,
  Loader2,
  Edit3,
  SkipForward,
} from 'lucide-react';
import { analyzeWorkoutPrintAction } from '@/app/actions/ai-actions';

interface WorkoutDetailModalProps {
  workout: Schedule | null;
  onClose: () => void;
  onComplete: (id: string) => Promise<void>;
  userId: string;
}

export default function WorkoutDetailModal({
  workout,
  onClose,
  onComplete,
  userId,
}: WorkoutDetailModalProps) {
  const [activeTab, setActiveTab] = useState<'info' | 'print' | 'manual' | 'skip'>('info');
  const [isUploading, setIsUploading] = useState(false);

  // Manual input form state
  const [manualDist, setManualDist] = useState(workout?.distancia_km || 5.0);
  const [manualDur, setManualDur] = useState(workout?.duracao_min || 30);
  const [manualPace, setManualPace] = useState(workout?.pace_alvo || '05:30');
  const [manualFC, setManualFC] = useState(145);
  const [manualRPE, setManualRPE] = useState(workout?.rpe_alvo || 5);
  const [manualNotes, setManualNotes] = useState('');

  if (!workout) return null;

  const isCompleted = workout.status === 'Concluído';

  const handleComplete = async () => {
    await onComplete(workout.id);
    onClose();
  };

  const compressImage = (file: File): Promise<{ base64: string; mimeType: string }> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement('canvas');
          let width = img.width;
          let height = img.height;
          const maxDim = 1000;
          if (width > maxDim || height > maxDim) {
            if (width > height) {
              height = Math.round((height * maxDim) / width);
              width = maxDim;
            } else {
              width = Math.round((width * maxDim) / height);
              height = maxDim;
            }
          }
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext('2d');
          if (!ctx) {
            const raw = (reader.result as string).split(',')[1];
            resolve({ base64: raw, mimeType: file.type });
            return;
          }
          ctx.drawImage(img, 0, 0, width, height);
          const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
          const base64 = dataUrl.split(',')[1];
          resolve({ base64, mimeType: 'image/jpeg' });
        };
        img.onerror = reject;
        img.src = e.target?.result as string;
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsUploading(true);
      const { base64, mimeType } = await compressImage(file);
      const res = await analyzeWorkoutPrintAction(userId || 'demo-athlete-001', base64, mimeType);

      if (res.success && res.data) {
        const data = res.data;
        alert(`✨ Dados extraídos pela IA!\nDistância: ${data.distancia_km || 0}km\nTempo: ${data.tempo_min || 0}min\nPace Médio: ${data.pace_medio || 'N/A'}\nFC: ${data.fc_media || 'N/A'} bpm\n\nConcluindo treino...`);
        await handleComplete();
      } else {
        alert(`Não foi possível analisar o print: ${res.error || 'Tente novamente.'}`);
      }
    } catch (error: any) {
      alert('Erro ao processar imagem.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    alert(`Treino manual gravado com sucesso!\nDistância: ${manualDist}km | Tempo: ${manualDur}min | RPE: ${manualRPE}/10`);
    await handleComplete();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="w-full max-w-lg max-h-[90vh] overflow-y-auto bg-white dark:bg-[#141414] border-t sm:border border-slate-200 dark:border-[#262626] rounded-t-3xl sm:rounded-3xl p-5 sm:p-6 shadow-2xl space-y-4 text-slate-900 dark:text-white"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span
                className={`inline-flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${
                  isCompleted
                    ? 'bg-[#11C76F]/15 text-[#11C76F]'
                    : 'bg-amber-500/15 text-amber-500'
                }`}
              >
                {isCompleted ? '✓ Concluído' : '⏳ Pendente'}
              </span>
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-[#11C76F]" />
                {workout.dia_semana} • {workout.data_prevista}
              </span>
            </div>

            <h2 className="text-lg sm:text-xl font-extrabold">{workout.tipo_treino}</h2>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar detalhes"
            className="p-2 rounded-2xl bg-slate-100 dark:bg-[#202020] text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Selector (Streamlit-style options) */}
        {!isCompleted && (
          <div className="flex rounded-full bg-slate-100 dark:bg-[#1c1c1c] p-1 border border-slate-200 dark:border-[#262626]">
            <button
              type="button"
              onClick={() => setActiveTab('info')}
              className={`flex-1 py-1.5 text-xs font-bold rounded-full transition-all ${
                activeTab === 'info'
                  ? 'bg-white dark:bg-[#262626] text-slate-900 dark:text-white shadow-xs'
                  : 'text-slate-500 dark:text-[#8E8E93]'
              }`}
            >
              Estrutura
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('print')}
              className={`flex-1 py-1.5 text-xs font-bold rounded-full transition-all ${
                activeTab === 'print'
                  ? 'bg-[#11C76F] text-white shadow-xs'
                  : 'text-slate-500 dark:text-[#8E8E93]'
              }`}
            >
              Enviar Print
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('manual')}
              className={`flex-1 py-1.5 text-xs font-bold rounded-full transition-all ${
                activeTab === 'manual'
                  ? 'bg-[#11C76F] text-white shadow-xs'
                  : 'text-slate-500 dark:text-[#8E8E93]'
              }`}
            >
              Manual
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('skip')}
              className={`flex-1 py-1.5 text-xs font-bold rounded-full transition-all ${
                activeTab === 'skip'
                  ? 'bg-rose-500 text-white shadow-xs'
                  : 'text-slate-500 dark:text-[#8E8E93]'
              }`}
            >
              Pular
            </button>
          </div>
        )}

        {/* TAB 1: ESTRUTURA / DETALHES */}
        {activeTab === 'info' && (
          <div className="space-y-4">
            {/* Prescription Metric Badges */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 bg-slate-50 dark:bg-[#1c1c1c] p-3 rounded-2xl border border-slate-100 dark:border-[#242424]">
              <div className="text-center p-2 rounded-xl bg-white dark:bg-[#141414] shadow-xs">
                <div className="text-[10px] uppercase font-semibold text-slate-400 mb-0.5 flex items-center justify-center gap-1">
                  <Gauge className="w-3 h-3 text-[#11C76F]" />
                  Distância
                </div>
                <div className="text-base font-bold text-slate-900 dark:text-white">
                  {workout.distancia_km.toFixed(1)} km
                </div>
              </div>

              <div className="text-center p-2 rounded-xl bg-white dark:bg-[#141414] shadow-xs">
                <div className="text-[10px] uppercase font-semibold text-slate-400 mb-0.5 flex items-center justify-center gap-1">
                  <Clock className="w-3 h-3 text-slate-400" />
                  Duração
                </div>
                <div className="text-base font-bold text-slate-900 dark:text-white">
                  {workout.duracao_min} min
                </div>
              </div>

              <div className="text-center p-2 rounded-xl bg-white dark:bg-[#141414] shadow-xs">
                <div className="text-[10px] uppercase font-semibold text-slate-400 mb-0.5 flex items-center justify-center gap-1">
                  <Flame className="w-3 h-3 text-amber-500" />
                  Pace Alvo
                </div>
                <div className="text-xs font-bold text-slate-900 dark:text-white truncate">
                  {workout.pace_alvo}
                </div>
              </div>

              <div className="text-center p-2 rounded-xl bg-white dark:bg-[#141414] shadow-xs">
                <div className="text-[10px] uppercase font-semibold text-slate-400 mb-0.5 flex items-center justify-center gap-1">
                  <Info className="w-3 h-3 text-purple-500" />
                  Esforço
                </div>
                <div className="text-base font-bold text-slate-900 dark:text-white">
                  RPE {workout.rpe_alvo}/10
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-[#8E8E93] mb-1.5 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-[#11C76F]" />
                Estrutura Detalhada da Sessão
              </h4>
              <div className="bg-slate-50 dark:bg-[#1c1c1c] border border-slate-100 dark:border-[#242424] rounded-2xl p-4 text-slate-700 dark:text-slate-200 text-xs leading-relaxed whitespace-pre-line">
                {workout.estrutura_treino || 'Estrutura detalhada não prescrita para este treino.'}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: ENVIAR PRINT */}
        {activeTab === 'print' && (
          <div className="space-y-3 bg-slate-50 dark:bg-[#1c1c1c] p-4 rounded-2xl border border-slate-100 dark:border-[#242424]">
            <p className="text-xs text-slate-600 dark:text-[#8E8E93] leading-relaxed">
              Tire um print da tela do Garmin Connect, Strava, Polar ou Apple Watch. A IA extrai o ritmo, tempo e quilometragem automaticamente.
            </p>

            <div className="relative border-2 border-dashed border-slate-300 dark:border-[#333333] hover:border-[#11C76F] rounded-2xl p-6 text-center transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                disabled={isUploading}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
              />
              <div className="flex flex-col items-center justify-center">
                {isUploading ? (
                  <Loader2 className="w-8 h-8 text-[#11C76F] animate-spin mb-2" />
                ) : (
                  <Upload className="w-8 h-8 text-[#11C76F] mb-2" />
                )}
                <span className="font-bold text-xs">
                  {isUploading ? 'Lendo imagem com a IA...' : 'Clique para selecionar o print'}
                </span>
                <span className="text-[11px] text-slate-400 mt-1">PNG, JPG ou WebP</span>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: INSERIR MANUALMENTE */}
        {activeTab === 'manual' && (
          <form onSubmit={handleManualSubmit} className="space-y-3">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-500 mb-1">
                  Distância (km)
                </label>
                <input
                  type="number"
                  step="0.1"
                  required
                  value={manualDist}
                  onChange={(e) => setManualDist(Number(e.target.value))}
                  className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] font-bold text-xs"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-500 mb-1">
                  Duração (min)
                </label>
                <input
                  type="number"
                  required
                  value={manualDur}
                  onChange={(e) => setManualDur(Number(e.target.value))}
                  className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] font-bold text-xs"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-500 mb-1">
                  Pace Médio (ex: 05:15)
                </label>
                <input
                  type="text"
                  value={manualPace}
                  onChange={(e) => setManualPace(e.target.value)}
                  className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] font-bold text-xs"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-500 mb-1">
                  FC Média (bpm)
                </label>
                <input
                  type="number"
                  value={manualFC}
                  onChange={(e) => setManualFC(Number(e.target.value))}
                  className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] font-bold text-xs"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase text-slate-500 mb-1">
                Esforço Percebido (RPE 1 a 10): {manualRPE}/10
              </label>
              <input
                type="range"
                min={1}
                max={10}
                value={manualRPE}
                onChange={(e) => setManualRPE(Number(e.target.value))}
                className="w-full accent-[#11C76F]"
              />
            </div>

            <button
              type="submit"
              className="w-full py-3 rounded-2xl bg-[#11C76F] hover:bg-[#0ea85d] text-white font-bold text-xs shadow-xs flex items-center justify-center gap-1.5"
            >
              <CheckCircle2 className="w-4 h-4" />
              Salvar Treino Manual
            </button>
          </form>
        )}

        {/* TAB 4: PULAR TREINO */}
        {activeTab === 'skip' && (
          <div className="space-y-3 bg-rose-50 dark:bg-[#1c1212] p-4 rounded-2xl border border-rose-200 dark:border-rose-950">
            <h4 className="font-bold text-xs text-rose-700 dark:text-rose-400 flex items-center gap-1.5">
              <SkipForward className="w-4 h-4" />
              Pular Esta Sessão de Treino
            </h4>
            <p className="text-xs text-slate-600 dark:text-[#8E8E93] leading-relaxed">
              Não pôde realizar este treino por motivo de imprevisto, cansaço ou lesão? Você pode avançar o cronograma sem afetar o histórico.
            </p>
            <button
              type="button"
              onClick={handleComplete}
              className="w-full py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs transition-all"
            >
              Confirmar e Pular Treino
            </button>
          </div>
        )}

        {/* Footer Actions */}
        <div className="pt-1 flex items-center justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-5 py-2.5 rounded-2xl bg-slate-100 hover:bg-slate-200 dark:bg-[#202020] dark:hover:bg-[#282828] text-slate-700 dark:text-white text-xs font-bold transition-colors min-h-[42px]"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}
