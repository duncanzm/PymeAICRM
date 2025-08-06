# backend/app/services/email_service.py
import logging
from fastapi import BackgroundTasks
from pydantic import EmailStr

logger = logging.getLogger(__name__)

class EmailService:
    """
    Servicio para enviar correos electrónicos.
    En desarrollo, simplemente registra el correo en los logs.
    En producción, se conectaría a un servicio real de correo.
    """
    
    @staticmethod
    async def send_password_reset_email(
        background_tasks: BackgroundTasks,
        email: EmailStr,
        token: str,
        username: str
    ):
        """
        Envía un correo electrónico con un enlace para restablecer la contraseña.
        
        Args:
            background_tasks: Para enviar el correo en segundo plano
            email: Correo del destinatario
            token: Token de restablecimiento
            username: Nombre del usuario
        """
        # En producción, usaríamos algo como SMTP, SendGrid, etc.
        # Por ahora, simplemente simulamos el envío
        reset_link = f"http://localhost:3000/reset-password?token={token}"
        
        # Añadir la tarea en segundo plano
        background_tasks.add_task(
            EmailService._send_email_background,
            email=email,
            subject="Restablecer contraseña - PymeAI",
            content=f"""
            Hola {username},
            
            Has solicitado restablecer tu contraseña en PymeAI. 
            Para hacerlo, haz clic en el siguiente enlace (válido por 24 horas):
            
            {reset_link}
            
            Si no solicitaste este cambio, puedes ignorar este correo.
            
            Saludos,
            El equipo de PymeAI
            """
        )
    
    @staticmethod
    async def send_invitation_email(
        background_tasks: BackgroundTasks,
        email: EmailStr,
        token: str,
        inviter_name: str,
        organization_name: str,
        role: str
    ):
        """
        Envía un correo electrónico con una invitación para unirse a una organización.
        
        Args:
            background_tasks: Para enviar el correo en segundo plano
            email: Correo del destinatario
            token: Token de invitación
            inviter_name: Nombre de quien invita
            organization_name: Nombre de la organización
            role: Rol asignado
        """
        # En producción, usaríamos algo como SMTP, SendGrid, etc.
        # Por ahora, simplemente simulamos el envío
        invitation_link = f"http://localhost:3000/join-team?token={token}"
        
        # Añadir la tarea en segundo plano
        background_tasks.add_task(
            EmailService._send_email_background,
            email=email,
            subject=f"Invitación para unirse a {organization_name} en PymeAI",
            content=f"""
            Hola,
            
            {inviter_name} te ha invitado a unirse a {organization_name} en PymeAI con el rol de {role}.
            
            Para aceptar esta invitación, haz clic en el siguiente enlace (válido por 7 días):
            
            {invitation_link}
            
            Si no esperabas esta invitación, puedes ignorar este correo.
            
            Saludos,
            El equipo de PymeAI
            """
        )
    
    @staticmethod
    async def _send_email_background(email: EmailStr, subject: str, content: str):
        """
        Simulación de envío de correo en segundo plano.
        """
        logger.info(f"[EMAIL] Destinatario: {email}")
        logger.info(f"[EMAIL] Asunto: {subject}")
        logger.info(f"[EMAIL] Contenido: {content}")
        logger.info(f"[EMAIL] SIMULADO - En producción, este correo sería enviado realmente.")