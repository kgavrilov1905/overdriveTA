'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, FileText, Brain, BarChart3, Building2, Sparkles, Zap, TrendingUp, Globe } from 'lucide-react';
import { ChatMessage } from '@/components/ChatMessage';
import { MessageInput } from '@/components/MessageInput';
import { Header } from '@/components/Header';

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
  {
    icon: BarChart3,
    text: "What are the key findings about skills training in Alberta?",
    gradient: "from-blue-500 to-cyan-500",
    iconBg: "bg-blue-500"
  },
  {
    icon: Building2,
    text: "What are Alberta businesses most concerned about?",
    gradient: "from-emerald-500 to-teal-500",
    iconBg: "bg-emerald-500"
  },
  {
    icon: FileText,
    text: "What are Alberta's top priorities for the provincial government?",
    gradient: "from-purple-500 to-pink-500",
    iconBg: "bg-purple-500"
  },
  {
    icon: TrendingUp,
    text: "What percentage of organizations report skills shortages?",
    gradient: "from-orange-500 to-red-500",
    iconBg: "bg-orange-500"
  }
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
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

    try {
      // Call our backend API
      const response = await fetch('http://localhost:8000/api/chat/query', {
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
    handleSendMessage(question);
  };

  return (
    <div className="min-h-screen animated-bg">
      <Header />
      
      <main className="flex-1 flex flex-col max-w-5xl mx-auto w-full">
        {/* Chat Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-8 space-y-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] space-y-12">
              {/* Hero Section */}
              <div className="text-center space-y-8 max-w-4xl fade-in">
                <div className="relative">
                  <div className="absolute inset-0 blur-3xl opacity-30">
                    <div className="w-32 h-32 mx-auto gradient-alberta rounded-full"></div>
                  </div>
                  <div className="relative glass-strong p-6 rounded-3xl inline-block shadow-modern">
                    <div className="gradient-alberta p-4 rounded-2xl">
                      <Brain className="w-12 h-12 text-white mx-auto" />
                    </div>
                  </div>
                  <div className="absolute -top-2 -right-2">
                    <Sparkles className="w-8 h-8 text-yellow-400 animate-pulse" />
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h1 className="text-5xl md:text-6xl font-bold gradient-text leading-tight">
                    Welcome to Alberta Perspectives
                  </h1>
                  <p className="text-xl md:text-2xl text-white/80 font-light leading-relaxed">
                    Your next-generation AI research assistant for 
                    <span className="gradient-text font-semibold"> Alberta economic insights</span> and 
                    <span className="gradient-text font-semibold"> business intelligence</span>
                  </p>
                </div>

                {/* Features */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
                  <div className="glass p-4 rounded-2xl text-center">
                    <Zap className="w-8 h-8 mx-auto mb-2 text-yellow-400" />
                    <div className="text-white font-semibold">Lightning Fast</div>
                    <div className="text-white/60 text-sm">Instant AI responses</div>
                  </div>
                  <div className="glass p-4 rounded-2xl text-center">
                    <Brain className="w-8 h-8 mx-auto mb-2 text-blue-400" />
                    <div className="text-white font-semibold">AI-Powered</div>
                    <div className="text-white/60 text-sm">Google Gemini 2.0</div>
                  </div>
                  <div className="glass p-4 rounded-2xl text-center">
                    <Globe className="w-8 h-8 mx-auto mb-2 text-green-400" />
                    <div className="text-white font-semibold">Alberta Focus</div>
                    <div className="text-white/60 text-sm">Local expertise</div>
                  </div>
                </div>
              </div>

              {/* Sample Questions */}
              <div className="w-full max-w-4xl space-y-6 slide-up">
                <div className="text-center">
                  <h3 className="text-2xl font-bold text-white mb-2">Get Started</h3>
                  <p className="text-white/70 font-medium">Try one of these popular questions:</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {SAMPLE_QUESTIONS.map((question, index) => {
                    const IconComponent = question.icon;
                    return (
                      <button
                        key={index}
                        onClick={() => handleSampleQuestion(question.text)}
                        className="group glass-strong p-6 text-left rounded-2xl hover:scale-105 transition-all duration-300 shadow-modern hover:shadow-glow"
                      >
                        <div className="flex items-start space-x-4">
                          <div className={`p-3 rounded-xl bg-gradient-to-r ${question.gradient} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                            <IconComponent className="w-6 h-6 text-white" />
                          </div>
                          <div className="flex-1">
                            <p className="text-white font-medium leading-relaxed group-hover:text-white/90 transition-colors">
                              {question.text}
                            </p>
                            <div className="mt-2 text-white/50 text-sm">
                              Click to ask →
                            </div>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-8 pb-8">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isLoading && (
                <div className="flex items-center justify-center py-8">
                  <div className="glass-strong px-6 py-4 rounded-2xl flex items-center space-x-4">
                    <div className="loading-dots">
                      <div></div>
                      <div></div>
                      <div></div>
                    </div>
                    <span className="text-white/80 font-medium">AI is thinking...</span>
                    <Brain className="w-5 h-5 text-blue-400 animate-pulse" />
                  </div>
                </div>
              )}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="glass-strong border-t border-white/10 p-6 mx-6 mb-6 rounded-2xl">
          <MessageInput onSendMessage={handleSendMessage} disabled={isLoading} />
        </div>
      </main>
    </div>
  );
}
