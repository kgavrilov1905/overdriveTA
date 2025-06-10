'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Mic } from 'lucide-react';
import { clsx } from 'clsx';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function MessageInput({ 
  onSendMessage, 
  disabled = false,
  placeholder = "Ask me anything about Alberta's economy, skills training, or business priorities..." 
}: MessageInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="glass rounded-2xl border border-white/20 overflow-hidden shadow-modern">
        <div className="flex items-end">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={disabled}
              rows={1}
              className={clsx(
                "w-full px-6 py-4 bg-transparent border-0 resize-none text-white placeholder-white/50",
                "focus:outline-none focus:ring-0 scrollbar-hide",
                "text-lg font-medium leading-relaxed",
                disabled ? "cursor-not-allowed opacity-50" : ""
              )}
              style={{ maxHeight: '120px' }}
            />
            
            {/* Character count for long messages */}
            {message.length > 500 && (
              <div className="absolute top-2 right-20 text-xs text-white/40 font-medium">
                {message.length}/2000
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2 p-4">
            {/* Voice Input Button (placeholder) */}
            <button
              type="button"
              className="glass-strong p-3 rounded-xl hover:scale-105 transition-all duration-200 group"
              title="Voice input (coming soon)"
            >
              <Mic className="w-5 h-5 text-white/60 group-hover:text-white/80" />
            </button>

            {/* Send Button */}
            <button
              type="submit"
              disabled={!message.trim() || disabled}
              className={clsx(
                "relative p-3 rounded-xl transition-all duration-300 group",
                !message.trim() || disabled
                  ? "glass text-white/40 cursor-not-allowed"
                  : "btn-modern hover:scale-105 active:scale-95 shadow-glow"
              )}
            >
              <Send className="w-5 h-5 text-white" />
              
              {/* Send button glow effect */}
              {message.trim() && !disabled && (
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/20 to-purple-500/20 blur-xl group-hover:from-blue-500/30 group-hover:to-purple-500/30 transition-all duration-300"></div>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Typing indicator */}
      {message.length > 0 && (
        <div className="absolute -bottom-8 left-4 text-xs text-white/50 font-medium">
          {message.length > 100 ? 'Long message' : 'Type your message'} • Press Enter to send
        </div>
      )}
    </form>
  );
} 