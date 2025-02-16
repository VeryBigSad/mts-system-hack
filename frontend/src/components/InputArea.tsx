import React, { useState, useRef, forwardRef, useImperativeHandle, useEffect } from 'react';
import Webcam from 'react-webcam';
import { Send, Mic, Camera, StopCircle, Hand } from 'lucide-react';
import { processText, processSpeech, processGesture, textToSpeech, API_BASE_URL } from '../api';
import { translations } from '../translations';

interface InputAreaProps {
  mode: 'text' | 'voice' | 'sign';
  onSendMessage: (text: string, sender: 'user' | 'assistant') => void;
}

export interface InputAreaHandle {
  setText: (text: string) => void;
  submitForm: () => void;
}

const formatBotResponse = (response: any): string => {
  try {
    if (typeof response === 'string') {
      response = JSON.parse(response);
    }

    if (response.status !== 'success') {
      return translations.processingError;
    }

    const task = response.task;
    const params = response.parameters;

    switch (task) {
      case 'call_elevator':
        const direction = params.direction === 'up' ? '⬆️' : '⬇️';
        return `${direction} Вызываю лифт на ${params.floor} этаж`;
      
      case 'check_camera':
        return `🎥 Проверяю камеру ${params.camera_id} (${params.location})`;
      
      case 'check_snow':
        return `❄️ Проверяю уровень снега: ${params.location}`;
      
      case 'create_ticket':
        const priority = params.priority === 'high' ? '🔴' : params.priority === 'normal' ? '🟡' : '🟢';
        return `${priority} Создаю заявку: ${params.description}`;
      
      case 'submit_readings':
        return `📊 Передаю показания ${params.meter_type}: ${params.value}`;
      
      case 'pay_utilities':
        return `💳 Оплата ${params.service_type}: ${params.amount} руб.`;
      
      case 'check_obstacles':
        return `🚧 Проверка препятствий: ${params.location}, ${params.floor} этаж`;
      
      default:
        return JSON.stringify(response, null, 2);
    }
  } catch (error) {
    console.error('Error formatting bot response:', error);
    return JSON.stringify(response, null, 2);
  }
};

export const InputArea = forwardRef<InputAreaHandle, InputAreaProps>(({ mode, onSendMessage }, ref) => {
  const [text, setText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const webcamRef = useRef<Webcam>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const formRef = useRef<HTMLFormElement>(null);
  const streamIntervalRef = useRef<number>();

  useEffect(() => {
    // Cleanup interval on unmount or mode change
    return () => {
      if (streamIntervalRef.current) {
        clearInterval(streamIntervalRef.current);
        streamIntervalRef.current = undefined;
      }
    };
  }, [mode]);

  useImperativeHandle(ref, () => ({
    setText: (newText: string) => setText(newText),
    submitForm: () => formRef.current?.requestSubmit()
  }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim()) {
      let textCopy = text;
      setIsProcessing(true);
      setText('');
      try {
        onSendMessage(textCopy, 'user');
        const response = await processText(textCopy);
        const formattedResponse = formatBotResponse(response);
        onSendMessage(formattedResponse, 'assistant');
        await playTextToSpeech(formattedResponse);
      } catch (error) {
        const errorMessage = translations.processingError;
        onSendMessage(errorMessage, 'assistant');
        await playTextToSpeech(errorMessage);
      } finally {
        setIsProcessing(false);
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
            onSendMessage("_Голосовое сообщение_", 'user');
            const response = await processSpeech(audioBlob);
            const formattedResponse = formatBotResponse(response);
            onSendMessage(formattedResponse, 'assistant');
            await playTextToSpeech(formattedResponse);
          } catch (error) {
            const errorMessage = translations.voiceProcessingError;
            onSendMessage(errorMessage, 'assistant');
            await playTextToSpeech(errorMessage);
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
        onSendMessage(translations.microphoneError, 'assistant');
      });
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const toggleGestureStream = async () => {
    if (!isRecording && webcamRef.current) {
      // Start streaming
      setIsRecording(true);
      onSendMessage("_Распознавание жестов активировано_", 'user');

      streamIntervalRef.current = window.setInterval(async () => {
        try {
          const screenshot = webcamRef.current?.getScreenshot();
          if (screenshot) {
            const response = await processGesture(screenshot);
            if (response.status === 'success') {
              const formattedResponse = formatBotResponse(response);
              onSendMessage(formattedResponse, 'user');
              await playTextToSpeech(formattedResponse);
            }
          }
        } catch (error) {
          console.error('Error processing gesture:', error);
          if (streamIntervalRef.current) {
            clearInterval(streamIntervalRef.current);
            streamIntervalRef.current = undefined;
            setIsRecording(false);
            const errorMessage = translations.processingError;
            onSendMessage(errorMessage, 'user');
            await playTextToSpeech(errorMessage);
          }
        }
      }, 1500);
    } else {
      // Stop streaming
      if (streamIntervalRef.current) {
        clearInterval(streamIntervalRef.current);
        streamIntervalRef.current = undefined;
        setIsRecording(false);
        onSendMessage("_Распознавание жестов остановлено_", 'user');
      }
    }
  };

  const playTextToSpeech = async (text: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'audio/mp3'
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('Failed to get audio');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      
      // Create a new Audio element each time
      const audio = new Audio(url);
      
      // Append the audio element to the document to ensure it isn't removed prematurely
      document.body.appendChild(audio);
      
      await audio.play();
      
      // Clean up after playback ends
      audio.onended = () => {
        URL.revokeObjectURL(url);
        document.body.removeChild(audio);
      };
    } catch (error) {
      console.error('Failed to play TTS:', error);
    }
  };

  if (mode === 'sign') {
    return (
      <div className="relative">
        <Webcam
          ref={webcamRef}
          audio={false}
          screenshotFormat="image/jpeg"
          className="w-full h-48 rounded-lg"
        />
        <button
          className={`absolute bottom-4 right-4 p-4 rounded-full ${
            isRecording ? 'bg-red-600' : 'bg-blue-600'
          } text-white ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
          onClick={toggleGestureStream}
          disabled={isProcessing}
          title={isRecording ? 'Нажмите, чтобы остановить' : 'Нажмите, чтобы начать распознавание'}
        >
          {isRecording ? <StopCircle size={24} /> : <Hand size={24} />}
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
    <form ref={formRef} onSubmit={handleSubmit} className="flex gap-2">
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
});