export const API_BASE_URL = 'https://fak0yd-ip-93-120-241-234.tunnelmole.net';

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
  const response = await fetch(`${API_BASE_URL}/api/v1/ai/raspalcovka`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ image: imageData }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to process gesture');
  }
  
  return response.json();
}