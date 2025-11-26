import { useAuth } from '@clerk/clerk-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

export const useApi = () => {
  const { getToken } = useAuth();

  const fetchWithAuth = async (endpoint, options = {}) => {
    try {
      const token = await getToken();
      
      const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  };

  return { fetchWithAuth };
};