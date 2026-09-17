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
      {/* Floating Action Button (Solid PicPay Green, No Gradient) */}
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-20 right-4 sm:bottom-6 sm:right-6 w-14 h-14 bg-[#11C76F] hover:bg-[#0ea85d] rounded-full shadow-lg flex items-center justify-center text-white active:scale-95 transition-all z-40 ${
          isOpen ? 'hidden' : 'flex'
        }`}
        aria-label="Abrir Chat com Treinador"
      >
        <MessageCircle className="w-6 h-6" />
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed inset-0 sm:inset-auto sm:bottom-24 sm:right-6 sm:w-96 sm:h-[520px] z-50 flex flex-col bg-white dark:bg-[#141414] border-t sm:border border-slate-200 dark:border-[#262626] rounded-t-3xl sm:rounded-3xl shadow-2xl overflow-hidden animate-in slide-in-from-bottom-5">
          {/* Header */}
          <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-[#1c1c1c] border-b border-slate-200 dark:border-[#262626]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-[#11C76F] flex items-center justify-center text-white">
                🤖
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">Coach AI</h3>
                <p className="text-[10px] text-[#11C76F] font-semibold flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#11C76F]" />
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
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/60 dark:bg-[#000000]">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[85%] p-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                    m.role === 'user'
                      ? 'bg-[#11C76F] text-white rounded-br-sm shadow-xs'
                      : 'bg-white dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] text-slate-800 dark:text-white rounded-bl-sm shadow-xs'
                  }`}
                >
                  {m.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[85%] p-3 rounded-2xl text-xs bg-white dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] text-slate-400 rounded-bl-sm flex items-center gap-2">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-[#11C76F]" /> O treinador está pensando...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <form
            onSubmit={handleSend}
            className="p-3 bg-white dark:bg-[#141414] border-t border-slate-200 dark:border-[#262626] flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Pergunte ao treinador..."
              className="flex-1 bg-slate-100 dark:bg-[#1c1c1c] border border-slate-200 dark:border-[#262626] rounded-full px-4 py-2.5 text-xs sm:text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-[#11C76F]"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="w-10 h-10 rounded-full bg-[#11C76F] text-white flex items-center justify-center hover:bg-[#0ea85d] disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
