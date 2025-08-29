// src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
// Importamos los componentes básicos de Material UI para el tema
import { ThemeProvider, createTheme } from '@mui/material/styles';
// CssBaseline normaliza los estilos CSS entre diferentes navegadores
import CssBaseline from '@mui/material/CssBaseline';
import './index.css'

// Creamos un tema personalizado para Material UI con nuestra paleta de colores
const theme = createTheme({
  palette: {
    primary: {
      main: '#4338ca', // Color principal: Indigo
    },
    secondary: {
      main: '#0891b2', // Color secundario: Cyan
    },
  },
  // Configuración de tipografía para toda la aplicación
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

// Renderizamos la aplicación dentro del ThemeProvider para aplicar nuestro tema
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline /> {/* Normaliza los estilos entre navegadores */}
      <App />
    </ThemeProvider>
  </React.StrictMode>,
)