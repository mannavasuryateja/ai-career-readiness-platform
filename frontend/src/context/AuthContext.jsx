import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [quota, setQuota] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchQuota = useCallback(async (authToken) => {
    const activeToken = authToken || token || localStorage.getItem('access_token') || localStorage.getItem('token');
    if (!activeToken) return;

    try {
      const response = await axios.get(`${API_BASE_URL}/api/auth/quota`, {
        headers: {
          Authorization: `Bearer ${activeToken}`,
        },
      });
      setQuota(response.data);
    } catch (err) {
      console.warn('Failed to fetch quota:', err);
    }
  }, [token]);

  // Initialize auth from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('access_token') || localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setToken(storedToken);
        setUser(parsedUser);
        axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
        fetchQuota(storedToken);
      } catch (e) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }

    setLoading(false);
  }, [fetchQuota]);

  const register = async (email, password, fullName) => {
    try {
      setError(null);
      const response = await axios.post(`${API_BASE_URL}/api/auth/register`, {
        email,
        password,
        full_name: fullName,
      });

      const { access_token, user_id, full_name } = response.data;

      // Store auth data
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify({
        user_id,
        email,
        full_name,
      }));

      // Set axios header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      setToken(access_token);
      setUser({ user_id, email, full_name });
      fetchQuota(access_token);

      return { success: true };
    } catch (err) {
      const message = err.response?.data?.detail || 'Registration failed';
      setError(message);
      return { success: false, error: message };
    }
  };

  const login = async (email, password) => {
    try {
      setError(null);
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        email,
        password,
      });

      const { access_token, user_id, full_name } = response.data;

      // Store auth data
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify({
        user_id,
        email,
        full_name,
      }));

      // Set axios header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      setToken(access_token);
      setUser({ user_id, email, full_name });
      fetchQuota(access_token);

      return { success: true };
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed';
      setError(message);
      return { success: false, error: message };
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await axios.post(`${API_BASE_URL}/api/auth/logout`, {}, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      }
    } catch (err) {
      console.warn('Logout notification error:', err);
    } finally {
      // Clear local storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('token');
      localStorage.removeItem('user');

      // Clear axios header
      delete axios.defaults.headers.common['Authorization'];

      setToken(null);
      setUser(null);
      setQuota(null);
    }
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      setError(null);
      await axios.post(
        `${API_BASE_URL}/api/auth/change-password`,
        {
          current_password: currentPassword,
          new_password: newPassword,
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      return { success: true };
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to change password';
      setError(message);
      return { success: false, error: message };
    }
  };

  const updateProfile = async (profileData) => {
    try {
      setError(null);
      const response = await axios.put(
        `${API_BASE_URL}/api/auth/profile`,
        profileData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      const updatedUser = response.data;
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
      return { success: true, user: updatedUser };
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to update profile';
      setError(message);
      return { success: false, error: message };
    }
  };

  const deleteMyData = async () => {
    try {
      setError(null);
      await axios.delete(`${API_BASE_URL}/api/auth/my-data`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      // Clear session after data wipe
      await logout();
      return { success: true };
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to delete data';
      setError(message);
      return { success: false, error: message };
    }
  };

  const isAuthenticated = !!token && !!user;

  const value = {
    user,
    token,
    quota,
    loading,
    error,
    isAuthenticated,
    register,
    login,
    logout,
    changePassword,
    updateProfile,
    deleteMyData,
    fetchQuota,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};


export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
