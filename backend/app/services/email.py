import logging
from app.models.user import User
from app.models.finance import Invoice

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    async def send_welcome_email(user: User, raw_password: str):
        """
        Mocks sending a welcome email to a newly provisioned user.
        """
        email_content = f"""
        ======================================================================
        TO: {user.email}
        SUBJECT: Welcome to SmartERP!
        
        Hello {user.first_name},
        
        Your administrator has created an account for you on SmartERP.
        
        Role: {user.role}
        Temporary Password: {raw_password}
        
        Please login and change your password as soon as possible.
        
        Best regards,
        The SmartERP Team
        ======================================================================
        """
        # In a real app, you would use smtplib or an API like SendGrid here.
        # For now, we mock it by printing to the console/logger.
        print(email_content)
        logger.info(f"Mock email sent to {user.email}")

    @staticmethod
    async def send_invoice_reminder(invoice: Invoice, to_email: str):
        """
        Mocks sending an invoice reminder.
        """
        email_content = f"""
        ======================================================================
        TO: {to_email}
        SUBJECT: Invoice Reminder - {invoice.invoice_number}
        
        Hello,
        
        This is a reminder that invoice {invoice.invoice_number} for the amount of 
        ${invoice.total_amount:,.2f} is due on {invoice.due_date}.
        
        Current Balance Due: ${(invoice.total_amount - invoice.amount_paid):,.2f}
        
        Please remit payment at your earliest convenience.
        
        Best regards,
        The SmartERP Finance Team
        ======================================================================
        """
        print(email_content)
        logger.info(f"Mock invoice reminder sent to {to_email}")
