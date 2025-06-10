'use client';

import { Brain, User, FileText, Calendar, TrendingUp, ExternalLink } from 'lucide-react';
import { clsx } from 'clsx';

interface Source {
  document_id: number;
  title: string;
  filename: string;
  page_number: number;
  relevance_score: number;
}

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
  confidence?: number;
}

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.type === 'user';
  
  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    }).format(date);
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'text-white/50';
    if (confidence >= 0.8) return 'text-green-400';
    if (confidence >= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getConfidenceLabel = (confidence?: number) => {
    if (!confidence) return 'Unknown';
    if (confidence >= 0.8) return 'High Confidence';
    if (confidence >= 0.6) return 'Medium Confidence';
    return 'Low Confidence';
  };

  if (isUser) {
    return (
      <div className="flex items-start space-x-4 justify-end fade-in">
        <div className="flex flex-col items-end max-w-2xl">
          <div className="glass-strong px-6 py-4 rounded-3xl rounded-tr-lg shadow-modern">
            <p className="text-white font-medium leading-relaxed whitespace-pre-wrap">{message.content}</p>
          </div>
          <div className="flex items-center space-x-2 mt-2 text-xs text-white/50">
            <Calendar className="w-3 h-3" />
            <span>{formatTime(message.timestamp)}</span>
          </div>
        </div>
        <div className="gradient-alberta p-3 rounded-2xl shadow-glow flex-shrink-0">
          <User className="w-5 h-5 text-white" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start space-x-4 fade-in">
      <div className="gradient-alberta p-3 rounded-2xl shadow-glow flex-shrink-0">
        <Brain className="w-5 h-5 text-white" />
      </div>
      
      <div className="flex-1 max-w-4xl">
        <div className="glass-strong rounded-3xl rounded-tl-lg shadow-modern overflow-hidden">
          {/* Message Content */}
          <div className="px-6 py-5">
            <div className="prose prose-lg max-w-none">
              <p className="text-white font-medium leading-relaxed whitespace-pre-wrap m-0">
                {message.content}
              </p>
            </div>
          </div>

          {/* Confidence Score */}
          {message.confidence !== undefined && (
            <div className="px-6 py-3 border-t border-white/10 bg-white/5">
              <div className="flex items-center space-x-3">
                <TrendingUp className="w-4 h-4 text-white/60" />
                <span className="text-white/60 text-sm font-medium">Confidence:</span>
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    {[...Array(5)].map((_, i) => (
                      <div
                        key={i}
                        className={clsx(
                          "w-2 h-2 rounded-full",
                          i < Math.round((message.confidence || 0) * 5)
                            ? getConfidenceColor(message.confidence).replace('text-', 'bg-')
                            : 'bg-white/20'
                        )}
                      />
                    ))}
                  </div>
                  <span className={clsx("text-sm font-semibold", getConfidenceColor(message.confidence))}>
                    {getConfidenceLabel(message.confidence)} ({Math.round((message.confidence || 0) * 100)}%)
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Sources */}
          {message.sources && message.sources.length > 0 && (
            <div className="px-6 py-4 border-t border-white/10 bg-white/5">
              <div className="flex items-center space-x-2 mb-4">
                <FileText className="w-5 h-5 text-white/60" />
                <span className="text-white font-semibold">
                  Sources ({message.sources.length})
                </span>
              </div>
              
              <div className="grid gap-3">
                {message.sources.map((source, index) => (
                  <div 
                    key={index}
                    className="glass p-4 rounded-xl border border-white/10 hover:border-white/20 transition-all duration-200 group"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-semibold text-sm truncate flex-1">
                        {source.title}
                      </h4>
                      <div className="flex items-center space-x-2 ml-3">
                        <div className="flex items-center space-x-1">
                          <div className="w-2 h-2 rounded-full bg-gradient-to-r from-green-400 to-blue-400"></div>
                          <span className="text-white/70 text-xs font-medium">
                            {Math.round(source.relevance_score * 100)}% match
                          </span>
                        </div>
                        <button className="opacity-0 group-hover:opacity-100 transition-opacity">
                          <ExternalLink className="w-3 h-3 text-white/60 hover:text-white/80" />
                        </button>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4 text-xs text-white/60">
                      <span className="truncate font-medium">{source.filename}</span>
                      <span className="text-white/40">•</span>
                      <span className="font-medium">Page {source.page_number}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Timestamp */}
        <div className="flex items-center space-x-2 mt-2 text-xs text-white/50">
          <Calendar className="w-3 h-3" />
          <span>{formatTime(message.timestamp)}</span>
        </div>
      </div>
    </div>
  );
} 