"""
gmail_integration.py

Display Gmail messages in HUD panel
"""

import logging
import datetime
import base64
import re
import email
from email.header import decode_header

logger = logging.getLogger("GmailIntegration")
logger.setLevel(logging.INFO)

class GmailIntegration:
    def __init__(self, api_manager):
        """
        Initialize Gmail integration
        
        Args:
            api_manager: GoogleAPIManager instance
        """
        self.api_manager = api_manager
        self.gmail_service = None
        self.cached_messages = None
        self.cache_time = None
    
    def initialize(self):
        """Initialize the Gmail service"""
        self.gmail_service = self.api_manager.get_gmail_service()
        return self.gmail_service is not None
    
    def get_messages(self, max_results=20, force_refresh=False):
        """Get list of recent email messages"""
        try:
            if not self.gmail_service:
                if not self.initialize():
                    return []
            
            # Return cached messages if available and not expired
            if (not force_refresh and self.cached_messages and self.cache_time and 
                (datetime.datetime.now() - self.cache_time).total_seconds() < 300):  # 5 minutes cache
                return self.cached_messages
            
            # Get list of messages
            response = self.gmail_service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q='is:inbox'
            ).execute()
            
            messages = []
            for msg_data in response.get('messages', []):
                # Get full message details
                msg = self.gmail_service.users().messages().get(
                    userId='me',
                    id=msg_data['id']
                ).execute()
                
                # Process message
                processed_msg = self._process_message(msg)
                if processed_msg:
                    messages.append(processed_msg)
            
            # Cache results
            self.cached_messages = messages
            self.cache_time = datetime.datetime.now()
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting Gmail messages: {str(e)}")
            if self.cached_messages:
                return self.cached_messages
            return []
    
    def get_unread_count(self):
        """Get count of unread messages"""
        try:
            if not self.gmail_service:
                if not self.initialize():
                    return 0
            
            # Get list of unread messages
            response = self.gmail_service.users().messages().list(
                userId='me',
                q='is:inbox is:unread'
            ).execute()
            
            return len(response.get('messages', []))
            
        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            return 0
    
    def get_message_content(self, message_id):
        """Get the full content of a message"""
        try:
            if not self.gmail_service:
                if not self.initialize():
                    return None
            
            # Get message data
            msg = self.gmail_service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Process message
            return self._process_message(msg, get_body=True)
            
        except Exception as e:
            logger.error(f"Error getting message content: {str(e)}")
            return None
    
    def _process_message(self, msg, get_body=False):
        """Process a message from the API into a simplified format"""
        try:
            message_id = msg['id']
            thread_id = msg['threadId']
            
            # Extract headers
            headers = {}
            for header in msg['payload']['headers']:
                headers[header['name'].lower()] = header['value']
            
            # Get from, to, subject, date
            from_header = headers.get('from', '')
            to_header = headers.get('to', '')
            subject = headers.get('subject', '(No Subject)')
            date_str = headers.get('date', '')
            
            # Clean name from email
            from_name = self._extract_name_from_email_header(from_header)
            
            # Create message object
            message = {
                'id': message_id,
                'thread_id': thread_id,
                'from': from_header,
                'from_name': from_name,
                'to': to_header,
                'subject': subject,
                'date': date_str,
                'snippet': msg.get('snippet', ''),
                'unread': 'UNREAD' in msg.get('labelIds', []),
                'important': 'IMPORTANT' in msg.get('labelIds', [])
            }
            
            # Get message body if requested
            if get_body:
                message['body'] = self._get_message_body(msg)
                message['attachments'] = self._get_message_attachments(msg)
            
            return message
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return None
    
    def _extract_name_from_email_header(self, header):
        """Extract the name part from an email header"""
        if not header:
            return ''
        
        # Look for pattern: "Name <email@example.com>"
        match = re.match(r'"?([^"<]+)"?\s*(?:<[^>]+>)?', header)
        if match:
            name = match.group(1).strip()
            return name
        
        # Just use the part before @ if no match
        return header.split('@')[0] if '@' in header else header
    
    def _get_message_body(self, msg):
        """Extract the message body from the message"""
        try:
            if 'payload' not in msg:
                return ''
            
            if 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                # Handle simple messages
                data = msg['payload']['body']['data']
                decoded_data = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
                return decoded_data
            
            # Handle multipart messages
            if 'parts' in msg['payload']:
                return self._get_text_from_parts(msg['payload']['parts'])
            
            return ''
            
        except Exception as e:
            logger.error(f"Error getting message body: {str(e)}")
            return ''
    
    def _get_text_from_parts(self, parts):
        """Get text content from message parts"""
        text = ''
        
        for part in parts:
            if part.get('mimeType') == 'text/plain' and 'body' in part and 'data' in part['body']:
                data = part['body']['data']
                decoded_data = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
                text += decoded_data
            
            # Check for nested parts
            if 'parts' in part:
                text += self._get_text_from_parts(part['parts'])
        
        return text
    
    def _get_message_attachments(self, msg):
        """Get list of attachments from a message"""
        attachments = []
        
        try:
            if 'payload' not in msg:
                return attachments
            
            # Check for attachments in parts
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if 'filename' in part and part['filename']:
                        attachments.append({
                            'id': part.get('body', {}).get('attachmentId', ''),
                            'filename': part['filename'],
                            'mime_type': part.get('mimeType', ''),
                            'size': part.get('body', {}).get('size', 0)
                        })
            
            return attachments
            
        except Exception as e:
            logger.error(f"Error getting message attachments: {str(e)}")
            return attachments