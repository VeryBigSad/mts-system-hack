import React, { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import { Send, Mic, Camera, StopCircle } from 'lucide-react';
import { processText, processSpeech } from '../api';
import { translations } from '../translations';

interface InputAreaProps {
  mode: 'text' | 'voice' | 'sign';
  onSendMessage: (text: string) => void;
}

export const InputArea: React.FC<InputAreaProps> = ({ mode, onSendMessage }) => {
  const [text, setText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const webcamRef = useRef<Webcam>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim()) {
      setIsProcessing(true);
      try {
        onSendMessage(text);
        const response = await processText(text);
        onSendMessage(JSON.stringify(response, null, 2));
      } catch (error) {
        onSendMessage(translations.processingError);
      } finally {
        setIsProcessing(false);
        setText('');
      }
    }
  };

  const startRecording = () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        const mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'audio/webm'
        });
        mediaRecorderRef.current = mediaRecorder;
        chunksRef.current = [];

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            chunksRef.current.push(e.data);
          }
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
          try {
            setIsProcessing(true);
            const response = await processSpeech(audioBlob);
            onSendMessage(JSON.stringify(response, null, 2));
          } catch (error) {
            onSendMessage(translations.voiceProcessingError);
          } finally {
            setIsProcessing(false);
          }
          stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        setIsRecording(true);
      })
      .catch(error => {
        console.error('Error accessing microphone:', error);
        onSendMessage(translations.microphoneError);
      });
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  if (mode === 'sign') {
    return (
      <div className="relative">
        <Webcam
          ref={webcamRef}
          audio={false}
          className="w-full h-48 rounded-lg"
        />
        <button
          className="absolute bottom-4 right-4 bg-blue-600 text-white p-2 rounded-full"
          onClick={() => onSendMessage(translations.signLanguageDetected)}
          disabled={isProcessing}
        >
          <Camera size={24} />
        </button>
      </div>
    );
  }

  if (mode === 'voice') {
    return (
      <div className="flex justify-center">
        <button
          className={`p-4 rounded-full ${
            isRecording ? 'bg-red-600' : 'bg-blue-600'
          } text-white ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
          onMouseDown={startRecording}
          onMouseUp={stopRecording}
          onMouseLeave={stopRecording}
          disabled={isProcessing}
          title={isRecording ? 'Удерживайте для записи' : 'Нажмите и удерживайте для записи'}
        >
          {isRecording ? <StopCircle size={24} /> : <Mic size={24} />}
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={translations.typeMessage}
        className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:border-blue-500"
        disabled={isProcessing}
      />
      <button
        type="submit"
        className={`bg-blue-600 text-white p-2 rounded-lg ${
          isProcessing ? 'opacity-50 cursor-not-allowed' : ''
        }`}
        disabled={!text.trim() || isProcessing}
        title="Отправить"
      >
        <Send size={24} />
      </button>
    </form>
  );
};