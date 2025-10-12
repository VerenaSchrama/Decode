/**
 * Toast Context
 * Provides global toast notification functionality throughout the app
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import { Toast, ToastType } from '../components/Toast';

interface ToastData {
  id: string;
  message: string;
  type: ToastType;
  duration?: number;
  onPress?: () => void;
}

interface ToastContextType {
  showToast: (message: string, type: ToastType, duration?: number, onPress?: () => void) => void;
  hideToast: (id: string) => void;
  hideAllToasts: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

interface ToastProviderProps {
  children: React.ReactNode;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastData[]>([]);

  const showToast = useCallback((
    message: string,
    type: ToastType,
    duration = 3000,
    onPress?: () => void
  ) => {
    const id = Date.now().toString();
    const newToast: ToastData = {
      id,
      message,
      type,
      duration,
      onPress,
    };

    setToasts(prev => [...prev, newToast]);
  }, []);

  const hideToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const hideAllToasts = useCallback(() => {
    setToasts([]);
  }, []);

  const contextValue: ToastContextType = {
    showToast,
    hideToast,
    hideAllToasts,
  };

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      {toasts.map(toast => (
        <Toast
          key={toast.id}
          visible={true}
          message={toast.message}
          type={toast.type}
          duration={toast.duration}
          onPress={toast.onPress}
          onHide={() => hideToast(toast.id)}
        />
      ))}
    </ToastContext.Provider>
  );
};
