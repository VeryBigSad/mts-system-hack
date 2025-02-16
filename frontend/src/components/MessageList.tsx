import React from 'react';
import { Message } from '../types';

interface MessageListProps {
  messages: Message[];
}

const formatText = (text: string) => {
  return text.replace(/_(.*?)_/g, '<i>$1</i>');
};

const isCameraCheckMessage = (text: string): boolean => {
  return text.includes('🎥');
};

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => {
        const isCamera = message.sender === 'assistant' && isCameraCheckMessage(message.text);
        
        return (
          <div
            key={message.id}
            className={`flex ${
              message.sender === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                message.sender === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-900'
              }`}
            >
              <p dangerouslySetInnerHTML={{ __html: formatText(message.text) }} />
              {isCamera && (
                <div className="mt-3 aspect-video">
                  <iframe 
                    id='fp_embed_player' 
                    src='https://demo.flashphoner.com:8888/embed_player?urlServer=wss://demo.flashphoner.com:8443&streamName=rtsp%3A%2F%2Fwebstream%3Awebstream2000%4091.211.195.78%3A3125%2Fcam%2Frealmonitor%3Fchannel%3D1%26subtype%3D0%261&mediaProviders=WebRTC,MSE' 
                    frameBorder='0' 
                    width='100%' 
                    height='100%' 
                    scrolling='no' 
                    allowFullScreen
                    className="rounded"
                  />
                </div>
              )}
              <span className="text-xs opacity-70">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};