// src/utils/errorStorage.ts
// Utilidad simple para almacenar/recuperar errores de login entre renderizados

// Almacenar el error en sessionStorage (se mantiene hasta que se cierre la pestaña)
export const storeLoginError = (error: string) => {
  sessionStorage.setItem('login_error', error);
};

// Obtener el error almacenado
export const getLoginError = (): string | null => {
  return sessionStorage.getItem('login_error');
};

// Limpiar el error
export const clearLoginError = () => {
  sessionStorage.removeItem('login_error');
};