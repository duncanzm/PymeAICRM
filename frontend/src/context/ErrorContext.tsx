// src/context/ErrorContext.tsx
import React, { createContext, useContext, useState } from 'react';

// Definir el tipo de contexto
const ErrorContext = createContext<{
  loginError: string | null;
  setLoginError: (error: string | null) => void;
  clearLoginError: () => void;
} | undefined>(undefined);

// Proveedor sin tipado explícito
export const ErrorProvider = ({ children }: any) => {
  const [loginError, setLoginError] = useState<string | null>(null);

  const clearLoginError = () => {
    setLoginError(null);
  };

  return (
    <ErrorContext.Provider value={{ loginError, setLoginError, clearLoginError }}>
      {children}
    </ErrorContext.Provider>
  );
};

// Hook para usar el contexto
export const useError = () => {
  const context = useContext(ErrorContext);
  if (context === undefined) {
    throw new Error('useError must be used within an ErrorProvider');
  }
  return context;
};