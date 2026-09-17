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
    { role: 'model', content: 'Olá! Sou o seu Treinador de IA. Como posso te ajudar com os treinos hoje?' }
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
    if (!input.trim() || !profile) return;

    const userMessage = input.trim();
    setInput('');
    const newMessages: Message[] = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const reply = await chatWithCoach(profile.id, newMessages);
      setMessages([...newMessages, { role: 'model', content: reply }]);
    } catch (error) {
      setMessages([...newMessages, { role: 'model', content: 'Desculpe, tive um problema para processar sua mensagem.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-20 right-4 sm:bottom-6 sm:right-6 w-14 h-14 bg-gradient-to-tr from-primary-600 to-brand-emerald rounded-full shadow-lg shadow-primary-500/30 flex items-center justify-center text-white hover:scale-105 transition-transform z-40 ${isOpen ? 'hidden' : 'flex'}`}
        aria-label="Abrir Chat com Treinador"
      >
        <MessageCircle className="w-6 h-6" />
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed inset-0 sm:inset-auto sm:bottom-24 sm:right-6 sm:w-96 sm:h-[500px] z-50 flex flex-col bg-surface border-t sm:border border-surface-border rounded-t-2xl sm:rounded-2xl shadow-2xl overflow-hidden animate-in slide-in-from-bottom-5">
          {/* Header */}
          <div className="flex items-center justify-between p-4 bg-surface-card border-b border-surface-border">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary-600 to-brand-emerald flex items-center justify-center text-white">
                🤖
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Coach AI</h3>
                <p className="text-[10px] text-emerald-400 font-medium">Online e pronto</p>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="p-2 text-slate-400 hover:text-white transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-background">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[85%] p-3 rounded-2xl text-sm ${
                    m.role === 'user'
                      ? 'bg-primary-600 text-white rounded-br-sm'
                      : 'bg-surface-card border border-surface-border text-slate-200 rounded-bl-sm'
                  }`}
                >
                  {m.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[85%] p-3 rounded-2xl text-sm bg-surface-card border border-surface-border text-slate-400 rounded-bl-sm flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" /> Digitando...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSend} className="p-3 bg-surface-card border-t border-surface-border flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Digite sua mensagem..."
              className="flex-1 bg-background border border-surface-border rounded-full px-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-primary-500"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="w-10 h-10 rounded-full bg-primary-600 text-white flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
