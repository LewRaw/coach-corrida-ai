'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { Loader2 } from 'lucide-react';

export default function AuthCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    async function handleAuth() {
      try {
        const { data, error } = await supabase.auth.getSession();
        if (error) {
          console.warn('Auth callback getSession error:', error.message);
        }

        const hash = typeof window !== 'undefined' ? window.location.hash : '';
        const search = typeof window !== 'undefined' ? window.location.search : '';

        if (hash.includes('type=recovery') || search.includes('type=recovery')) {
          router.replace('/reset-password');
          return;
        }

        router.replace('/');
      } catch (err) {
        console.error('Error during auth callback processing:', err);
        router.replace('/');
      }
    }

    handleAuth();
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F5F6F8] dark:bg-[#000000]">
      <div className="flex flex-col items-center gap-3">
        <Loader2 className="w-8 h-8 text-[#11C76F] animate-spin" />
        <p className="text-xs text-slate-500 dark:text-[#8E8E93] font-medium">Validando autenticação...</p>
      </div>
    </div>
  );
}
