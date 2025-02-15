import React, { useState, useRef, useEffect } from 'react';
import { Message } from '../types';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import { ActionPanel } from './ActionPanel';
import { Camera, Mic, Type } from 'lucide-react';
import { translations } from '../translations';

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: translations.welcome,
      sender: 'assistant',
      timestamp: new Date(),
    }
  ]);
  const [inputMode, setInputMode] = useState<'text' | 'voice' | 'sign'>('text');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (text: string, sender: 'user' | 'assistant' = 'user') => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <div className="flex-1 overflow-hidden">
        <div className="h-full flex flex-col">
          <ActionPanel />
          <MessageList messages={messages} />
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      <div className="border-t border-gray-200 bg-white p-4">
        <div className="flex gap-2 mb-2 justify-center">
          <button
            onClick={() => setInputMode('text')}
            className={`p-2 rounded-full ${inputMode === 'text' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100'}`}
            title="Текстовый ввод"
          >
            <Type size={20} />
          </button>
          <button
            onClick={() => setInputMode('voice')}
            className={`p-2 rounded-full ${inputMode === 'voice' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100'}`}
            title="Голосовой ввод"
          >
            <Mic size={20} />
          </button>
          <button
            onClick={() => setInputMode('sign')}
            className={`p-2 rounded-full ${inputMode === 'sign' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100'}`}
            title="Язык жестов"
          >
            <Camera size={20} />
          </button>
        </div>
        <InputArea mode={inputMode} onSendMessage={handleSendMessage} />
      </div>
    </div>
  );
};