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
  const [isUploading, setIsUploading] = useState(false);

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

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="w-full max-w-lg max-h-[90vh] overflow-y-auto bg-white dark:bg-[#141d18] border-t sm:border border-slate-200 dark:border-[#23312a] rounded-t-3xl sm:rounded-3xl p-6 shadow-2xl space-y-5"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span
                className={`inline-flex items-center gap-1 text-[11px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full ${
                  isCompleted
                    ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/40'
                    : 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300 border border-amber-200 dark:border-amber-800/40'
                }`}
              >
                {isCompleted ? '✓ Concluído' : '⏳ Pendente'}
              </span>
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-emerald-500" />
                {workout.dia_semana} • {workout.data_prevista}
              </span>
            </div>

            <h2 className="text-xl font-extrabold text-slate-900 dark:text-white">
              {workout.tipo_treino}
            </h2>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar detalhes"
            className="p-2 rounded-2xl bg-slate-100 dark:bg-[#1a2520] text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors min-w-[40px] min-h-[40px] flex items-center justify-center"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Prescription Metric Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 bg-slate-50 dark:bg-[#0e1411] p-3 rounded-2xl border border-slate-100 dark:border-[#1d2922]">
          <div className="text-center p-2 rounded-xl bg-white dark:bg-[#141d18] shadow-sm">
            <div className="text-[10px] uppercase font-semibold text-slate-400 mb-0.5 flex items-center justify-center gap-1">
              <Gauge className="w-3 h-3 text-emerald-500" />
              Distância
            </div>
            <div className="text-base font-bold text-slate-900 dark:text-white">
              {workout.distancia_km.toFixed(1)} km
            </div>
          </div>

          <div className="text-center p-2 rounded-xl bg-white dark:bg-[#141d18] shadow-sm">
            <div className="text-[10px] uppercase font-semibold text-slate-400 mb-0.5 flex items-center justify-center gap-1">
              <Clock className="w-3 h-3 text-slate-400" />
              Duração
            </div>
            <div className="text-base font-bold text-slate-900 dark:text-white">
              {workout.duracao_min} min
            </div>
          </div>

          <div className="text-center p-2 rounded-xl bg-white dark:bg-[#141d18] shadow-sm">
            <div className="text-[10px] uppercase font-semibold text-slate-400 mb-0.5 flex items-center justify-center gap-1">
              <Flame className="w-3 h-3 text-amber-500" />
              Pace Alvo
            </div>
            <div className="text-xs font-bold text-slate-900 dark:text-white truncate">
              {workout.pace_alvo}
            </div>
          </div>

          <div className="text-center p-2 rounded-xl bg-white dark:bg-[#141d18] shadow-sm">
            <div className="text-[10px] uppercase font-semibold text-slate-400 mb-0.5 flex items-center justify-center gap-1">
              <Info className="w-3 h-3 text-purple-500" />
              Esforço
            </div>
            <div className="text-base font-bold text-slate-900 dark:text-white">
              RPE {workout.rpe_alvo}/10
            </div>
          </div>
        </div>

        {/* Full Prescription Structure */}
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2 flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-emerald-500" />
            Estrutura Detalhada da Sessão
          </h4>
          <div className="bg-slate-50 dark:bg-[#0e1411] border border-slate-100 dark:border-[#1d2922] rounded-2xl p-4 text-slate-700 dark:text-slate-200 text-xs sm:text-sm whitespace-pre-line leading-relaxed">
            {workout.estrutura_treino || 'Estrutura detalhada não prescrita para este treino.'}
          </div>
        </div>

        {/* Completion details if completed */}
        {isCompleted && workout.data_conclusao && (
          <div className="text-xs text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/40 rounded-2xl p-3 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-500" />
            <span>Treino concluído em {new Date(workout.data_conclusao).toLocaleDateString('pt-BR')} às {new Date(workout.data_conclusao).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}.</span>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex flex-col sm:flex-row items-center gap-2.5 pt-1">
          {!isCompleted && (
            <>
              <button
                type="button"
                onClick={handleComplete}
                className="w-full sm:flex-1 min-h-[46px] py-2.5 px-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm shadow-md shadow-emerald-600/20 flex items-center justify-center gap-2 transition-all active:scale-[0.99]"
              >
                <CheckCircle2 className="w-4 h-4" />
                Concluir Manualmente
              </button>

              <div className="w-full sm:flex-1 relative">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                  disabled={isUploading}
                />
                <button
                  type="button"
                  disabled={isUploading}
                  className="w-full min-h-[46px] py-2.5 px-4 rounded-2xl bg-slate-100 hover:bg-slate-200 dark:bg-[#1a2520] dark:hover:bg-[#202e27] border border-slate-200 dark:border-[#283830] text-emerald-700 dark:text-emerald-400 font-bold text-sm shadow-sm flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                >
                  {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                  {isUploading ? 'Lendo...' : 'Auto (Subir Print)'}
                </button>
              </div>
            </>
          )}
          <button
            type="button"
            onClick={onClose}
            className="w-full sm:w-auto px-5 py-2.5 rounded-2xl bg-slate-100 hover:bg-slate-200 dark:bg-[#141d18] dark:hover:bg-[#1a2520] border border-slate-200 dark:border-[#23312a] text-slate-700 dark:text-slate-300 text-sm font-semibold transition-colors min-h-[46px]"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}
