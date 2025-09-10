# backend/app/utils/email.py
# Crea este archivo si no existe

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional

from app.core.config import settings

# Configura el logger
logger = logging.getLogger(__name__)

def send_email(
    email_to: str,
    subject: str,
    html_content: str,
    text_content: str,
) -> None:
    """
    Envía un correo electrónico utilizando SMTP
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAILS_FROM_EMAIL
    message["To"] = email_to

    # Añadir el contenido del correo en formato texto y HTML
    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")
    message.attach(part1)
    message.attach(part2)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            
            server.sendmail(
                settings.EMAILS_FROM_EMAIL,
                email_to,
                message.as_string()
            )
            
            logger.info(f"Correo enviado correctamente a {email_to}")
    except Exception as e:
        logger.error(f"Error al enviar correo a {email_to}: {e}")
        raise

def send_reset_password_email(
    email_to: str,
    username: str,
    reset_url: str
) -> None:
    """
    Envía un correo de restablecimiento de contraseña
    """
    subject = f"PymeAI - Restablece tu contraseña"
    
    # Versión en texto plano
    text_content = f"""
    Hola {username},
    
    Has solicitado restablecer tu contraseña en PymeAI. 
    
    Para crear una nueva contraseña, por favor sigue este enlace:
    {reset_url}
    
    Este enlace es válido por 24 horas. Si no solicitaste restablecer tu contraseña, puedes ignorar este correo.
    
    Saludos,
    El equipo de PymeAI
    """
    
    # Versión en HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Restablece tu contraseña</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            .header h1 {{ color: #4F46E5; }}
            .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; }}
            .button {{ display: inline-block; background-color: #4F46E5; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; margin: 20px 0; }}
            .footer {{ margin-top: 20px; font-size: 12px; color: #777; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>PymeAI</h1>
                <p>Optimización de ventas para PYMEs</p>
            </div>
            <div class="content">
                <p>Hola {username},</p>
                <p>Has solicitado restablecer tu contraseña en PymeAI.</p>
                <p>Para crear una nueva contraseña, por favor haz clic en el siguiente botón:</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Restablecer contraseña</a>
                </p>
                <p>O copia y pega esta URL en tu navegador:</p>
                <p>{reset_url}</p>
                <p>Este enlace es válido por 24 horas. Si no solicitaste restablecer tu contraseña, puedes ignorar este correo.</p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
                <p>&copy; 2025 PymeAI. Todos los derechos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(
        email_to=email_to,
        subject=subject,
        html_content=html_content,
        text_content=text_content
    )