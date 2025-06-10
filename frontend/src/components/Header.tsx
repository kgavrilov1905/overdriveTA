import { Brain, FileText, Database, Sparkles } from 'lucide-react';

export function Header() {
  return (
    <header className="glass-strong sticky top-0 z-50 border-b border-white/10">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="gradient-alberta p-3 rounded-2xl shadow-glow">
                <Brain className="w-7 h-7 text-white" />
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 gradient-success rounded-full pulse-glow"></div>
            </div>
            <div>
              <h1 className="text-2xl font-bold gradient-text">
                Alberta Perspectives
              </h1>
              <p className="text-white/70 text-sm font-medium">
                AI-Powered Economic Research Assistant
              </p>
            </div>
          </div>

          {/* Modern Status Indicators */}
          <div className="flex items-center space-x-6">
            <div className="hidden md:flex items-center space-x-6">
              <div className="glass px-4 py-2 rounded-xl flex items-center space-x-3">
                <div className="gradient-alberta p-2 rounded-lg">
                  <FileText className="w-4 h-4 text-white" />
                </div>
                <div>
                  <div className="text-white font-semibold text-sm">2 Documents</div>
                  <div className="text-white/60 text-xs">Knowledge Base</div>
                </div>
              </div>
              
              <div className="glass px-4 py-2 rounded-xl flex items-center space-x-3">
                <div className="gradient-success p-2 rounded-lg">
                  <Database className="w-4 h-4 text-white" />
                </div>
                <div>
                  <div className="text-white font-semibold text-sm">155 Chunks</div>
                  <div className="text-white/60 text-xs">Vector Store</div>
                </div>
              </div>
            </div>

            {/* System Status */}
            <div className="glass px-4 py-2 rounded-xl flex items-center space-x-3">
              <div className="relative">
                <div className="w-3 h-3 gradient-success rounded-full pulse-glow"></div>
                <div className="absolute inset-0 w-3 h-3 gradient-success rounded-full animate-ping opacity-20"></div>
              </div>
              <div className="hidden sm:block">
                <div className="text-white font-semibold text-sm">Online</div>
                <div className="text-white/60 text-xs">All Systems</div>
              </div>
            </div>

            {/* AI Status Indicator */}
            <div className="gradient-alberta p-2 rounded-xl">
              <Sparkles className="w-5 h-5 text-white animate-pulse" />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
} 