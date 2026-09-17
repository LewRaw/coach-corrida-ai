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
  Loader2
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
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="w-full max-w-lg max-h-[90vh] overflow-y-auto bg-surface border-t sm:border border-surface-border rounded-t-3xl sm:rounded-2xl p-6 shadow-2xl space-y-5"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span
                className={`inline-flex items-center gap-1 text-[11px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full ${
                  isCompleted
                    ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                    : 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                }`}
              >
                {isCompleted ? '✓ Concluído' : '⏳ Pendente'}
              </span>
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-primary-400" />
                {workout.dia_semana} • {workout.data_prevista}
              </span>
            </div>

            <h2 className="text-xl font-extrabold text-white">
              {workout.tipo_treino}
            </h2>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar detalhes"
            className="p-2.5 rounded-xl bg-surface-card border border-surface-border text-slate-400 hover:text-white transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Prescription Metric Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 bg-surface-card p-3 rounded-xl border border-surface-border">
          <div className="text-center p-2 rounded-lg bg-background/50">
            <div className="text-[10px] uppercase font-semibold text-slate-400 mb-0.5 flex items-center justify-center gap-1">
              <Gauge className="w-3 h-3 text-primary-400" />
              Distância
            </div>
            <div className="text-base font-bold text-white">
              {workout.distancia_km.toFixed(1)} km
            </div>
          </div>

          <div className="text-center p-2 rounded-lg bg-background/50">
            <div className="text-[10px] uppercase font-semibold text-slate-400 mb-0.5 flex items-center justify-center gap-1">
              <Clock className="w-3 h-3 text-slate-400" />
              Duração
            </div>
            <div className="text-base font-bold text-white">
              {workout.duracao_min} min
            </div>
          </div>

          <div className="text-center p-2 rounded-lg bg-background/50">
            <div className="text-[10px] uppercase font-semibold text-slate-400 mb-0.5 flex items-center justify-center gap-1">
              <Flame className="w-3 h-3 text-brand-amber" />
              Pace Alvo
            </div>
            <div className="text-xs font-bold text-white truncate">
              {workout.pace_alvo}
            </div>
          </div>

          <div className="text-center p-2 rounded-lg bg-background/50">
            <div className="text-[10px] uppercase font-semibold text-slate-400 mb-0.5 flex items-center justify-center gap-1">
              <Info className="w-3 h-3 text-purple-400" />
              Esforço
            </div>
            <div className="text-base font-bold text-white">
              RPE {workout.rpe_alvo}/10
            </div>
          </div>
        </div>

        {/* Full Prescription Structure */}
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-primary-400" />
            Estrutura Detalhada da Sessão
          </h4>
          <div className="bg-surface-card border border-surface-border rounded-xl p-4 text-slate-200 text-xs sm:text-sm whitespace-pre-line leading-relaxed font-mono">
            {workout.estrutura_treino || 'Estrutura detalhada não prescrita para este treino.'}
          </div>
        </div>

        {/* Completion details if completed */}
        {isCompleted && workout.data_conclusao && (
          <div className="text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-3 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>Treino concluído e registrado em {new Date(workout.data_conclusao).toLocaleDateString('pt-BR')} às {new Date(workout.data_conclusao).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}.</span>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
          {!isCompleted && (
            <>
              <button
                type="button"
                onClick={handleComplete}
                className="w-full sm:flex-1 min-h-[48px] py-3 px-4 rounded-xl bg-gradient-to-r from-brand-emerald to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-bold text-sm shadow-lg flex items-center justify-center gap-2 transition-all"
              >
                <CheckCircle2 className="w-5 h-5" />
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
                  className="w-full min-h-[48px] py-3 px-4 rounded-xl bg-surface-card hover:bg-surface-card-hover border border-surface-border text-primary-400 font-bold text-sm shadow-sm flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                >
                  {isUploading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Upload className="w-5 h-5" />}
                  {isUploading ? 'Lendo...' : 'Auto (Subir Print)'}
                </button>
              </div>
            </>
          )}
          <button
            type="button"
            onClick={onClose}
            className="w-full sm:w-auto px-5 py-3 rounded-xl bg-surface hover:bg-surface-card-hover border border-surface-border text-slate-300 text-sm font-semibold transition-colors min-h-[48px]"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}
