'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, MessageCircle } from 'lucide-react';
import { ChatMessage } from '@/components/ChatMessage';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Array<{
    document_id: number;
    title: string;
    filename: string;
    page_number: number;
    relevance_score: number;
  }>;
  confidence?: number;
}

const SAMPLE_QUESTIONS = [
  "What are the key findings about skills training in Alberta?",
  "What are Alberta businesses most concerned about?",
  "What are Alberta's top priorities for the provincial government?",
  "What percentage of organizations report skills shortages?"
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setInputValue('');

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: content.trim(),
          max_results: 5
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.answer,
        timestamp: new Date(),
        sources: data.sources,
        confidence: data.confidence,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'I apologize, but I encountered an error while processing your request. Please make sure the backend server is running and try again.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSampleQuestion = (question: string) => {
    setInputValue(question);
  };

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Chat Messages Area - Takes remaining space */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-6 py-12">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] space-y-12">
              {/* Modern Hero Section */}
              <div className="text-center space-y-6 max-w-2xl">
                <div className="space-y-4">
                  <h1 className="text-4xl font-medium text-gray-800 tracking-tight">
                    Alberta Perspectives
                  </h1>
                  <p className="text-xl text-gray-600 font-light leading-relaxed">
                    AI-powered research assistant for Alberta economic insights
                  </p>
                </div>
              </div>

              {/* Modern Sample Questions */}
              <div className="w-full max-w-2xl space-y-3">
                {SAMPLE_QUESTIONS.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleSampleQuestion(question)}
                    className="group w-full p-4 text-left bg-white hover:bg-gray-50 border border-gray-200 hover:border-gray-300 rounded-xl transition-all duration-200 shadow-sm hover:shadow-md"
                  >
                    <div className="flex items-start gap-4">
                      <div className="mt-0.5 p-2 bg-gray-100 group-hover:bg-gray-200 rounded-lg transition-colors duration-200">
                        <MessageCircle className="w-4 h-4 text-gray-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-gray-800 font-medium leading-relaxed group-hover:text-gray-900 transition-colors duration-200">
                          {question}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-8 pb-8">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isLoading && (
                <div className="flex justify-center py-6">
                  <div className="bg-gray-50 border border-gray-200 rounded-xl px-6 py-4 shadow-sm">
                    <div className="flex items-center gap-4">
                      <div className="loading-dots">
                        <div></div>
                        <div></div>
                        <div></div>
                      </div>
                      <span className="text-gray-600 font-medium">Analyzing documents...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input Section - Fixed at bottom */}
      <div className="border-t border-gray-100 bg-white">
        <div className="max-w-3xl mx-auto px-6 py-6">
          <div className="relative">
            <div className="relative bg-white border border-gray-300 rounded-3xl shadow-lg hover:shadow-xl transition-shadow duration-300">
              <div className="flex items-end gap-3 p-4">
                <div className="flex-1 min-h-[56px] flex items-center">
                  <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage(inputValue);
                      }
                    }}
                    placeholder="Message Alberta Perspectives..."
                    className="w-full bg-transparent text-gray-900 placeholder-gray-500 border-none outline-none resize-none text-lg leading-7 min-h-[24px] max-h-48"
                    rows={1}
                    style={{ 
                      height: 'auto',
                      minHeight: '24px'
                    }}
                    onInput={(e) => {
                      const target = e.target as HTMLTextAreaElement;
                      target.style.height = 'auto';
                      target.style.height = Math.min(target.scrollHeight, 192) + 'px';
                    }}
                  />
                </div>
                <button
                  onClick={() => handleSendMessage(inputValue)}
                  disabled={!inputValue.trim() || isLoading}
                  className={`p-3 rounded-full transition-all duration-200 ${
                    inputValue.trim() && !isLoading
                      ? 'bg-black hover:bg-gray-800 text-white shadow-lg hover:shadow-xl transform hover:scale-105'
                      : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
            <div className="text-center text-sm text-gray-500 mt-4 font-medium">
              Alberta Perspectives can make mistakes. Check important info.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
