const API_BASE_URL = 'http://localhost:8000';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export const sendMessage = async (message: string): Promise<ApiResponse<{ response: string }>> => {
  try {
    console.log('Sending message to backend:', { message });
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });
    
    console.log('Response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'No error details');
      console.error('API error response:', {
        status: response.status,
        statusText: response.statusText,
        error: errorText
      });
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json().catch(async (e) => {
      const text = await response.text();
      console.error('Failed to parse JSON response. Raw response:', text);
      throw new Error(`Invalid JSON response: ${e.message}`);
    });
    
    console.log('API response data:', data);
    return { data };
  } catch (error) {
    console.error('Error in sendMessage:', {
      error,
      message: error instanceof Error ? error.message : 'Unknown error'
    });
    return { error: error instanceof Error ? error.message : 'Failed to send message' };
  }
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
};
