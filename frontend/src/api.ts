export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function processText(text: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/ai/text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to process text');
  }
  
  return response.json();
}

export async function processSpeech(audioBlob: Blob): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/ai/speech`, {
    method: 'POST',
    headers: {
      'Content-Type': 'audio/webm',
    },
    body: audioBlob,
  });
  
  if (!response.ok) {
    throw new Error('Failed to process speech');
  }
  
  return response.json();
}

export async function processGesture(imageData: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/translator/raspalcovka`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ image: imageData.split(',')[1] }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to process gesture');
  }
  
  return response.json();
}

export const textToSpeech = async (text: string): Promise<Blob> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/tts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error('Failed to convert text to speech');
  }

  return response.blob();
};