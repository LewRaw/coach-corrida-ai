'use client';

import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Loader2 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { chatWithCoach } from '@/app/actions/ai-actions';

interface Message {
  role: 'user' | 'model';
  content: string;
}

export default function ChatPopup() {
  const { profile } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'model', content: 'Olá! Sou o seu Treinador de IA. Como posso te ajudar com os treinos hoje?' },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    const newMessages: Message[] = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const athleteId = profile?.id || 'demo-athlete-001';
      const res = await chatWithCoach(athleteId, newMessages);
      if (res.success && res.text) {
        setMessages([...newMessages, { role: 'model', content: res.text }]);
      } else {
        setMessages([...newMessages, { role: 'model', content: res.error || 'Desculpe, não consegui responder agora.' }]);
      }
    } catch (error: any) {
      setMessages([...newMessages, { role: 'model', content: 'Desculpe, tive um problema de conexão com o servidor.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-20 right-4 sm:bottom-6 sm:right-6 w-14 h-14 bg-gradient-to-tr from-emerald-600 to-teal-500 rounded-full shadow-lg shadow-emerald-600/30 flex items-center justify-center text-white hover:scale-105 active:scale-95 transition-all z-40 ${
          isOpen ? 'hidden' : 'flex'
        }`}
        aria-label="Abrir Chat com Treinador"
      >
        <MessageCircle className="w-6 h-6" />
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed inset-0 sm:inset-auto sm:bottom-24 sm:right-6 sm:w-96 sm:h-[520px] z-50 flex flex-col bg-white dark:bg-[#141d18] border-t sm:border border-slate-200 dark:border-[#23312a] rounded-t-3xl sm:rounded-3xl shadow-2xl overflow-hidden animate-in slide-in-from-bottom-5">
          {/* Header */}
          <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-[#0e1411] border-b border-slate-200 dark:border-[#23312a]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white shadow-sm shadow-emerald-500/20">
                🤖
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">Coach AI</h3>
                <p className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  Online
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-2 rounded-xl text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/50 dark:bg-[#0b0f0e]">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[85%] p-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                    m.role === 'user'
                      ? 'bg-emerald-600 text-white rounded-br-sm shadow-sm'
                      : 'bg-white dark:bg-[#141d18] border border-slate-200 dark:border-[#23312a] text-slate-800 dark:text-slate-200 rounded-bl-sm shadow-sm'
                  }`}
                >
                  {m.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[85%] p-3 rounded-2xl text-xs bg-white dark:bg-[#141d18] border border-slate-200 dark:border-[#23312a] text-slate-400 rounded-bl-sm flex items-center gap-2">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-emerald-500" /> O treinador está pensando...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <form
            onSubmit={handleSend}
            className="p-3 bg-white dark:bg-[#0e1411] border-t border-slate-200 dark:border-[#23312a] flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Pergunte ao treinador..."
              className="flex-1 bg-slate-100 dark:bg-[#141d18] border border-slate-200 dark:border-[#23312a] rounded-full px-4 py-2.5 text-xs sm:text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-emerald-500"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="w-10 h-10 rounded-full bg-emerald-600 text-white flex items-center justify-center hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
