import { Brain } from 'lucide-react';

export function Header() {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
      <div className="max-w-3xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Simple Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="bg-gray-100 p-2 rounded-lg">
              <Brain className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">
                Alberta Perspectives
              </h1>
              <p className="text-gray-500 text-xs">
                AI-Powered Economic Research Assistant
              </p>
            </div>
          </div>

          {/* Simple Status */}
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            <div className="hidden sm:flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Online</span>
            </div>
            <div className="hidden md:block">
              2 Documents • 155 Chunks
            </div>
          </div>
        </div>
      </div>
    </header>
  );
} 