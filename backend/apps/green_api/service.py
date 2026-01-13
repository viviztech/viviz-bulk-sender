"""
Green API service for WhatsApp integration.
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class GreenAPIService:
    """Service for interacting with Green API."""
    
    BASE_URL = 'https://api.green-api.com'
    
    def __init__(self, id_instance, api_token):
        self.id_instance = id_instance
        self.api_token = api_token
    
    def _request(self, method, endpoint, data=None, files=None):
        """Make a request to Green API."""
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                files=files,
                timeout=settings.GREEN_API_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Green API error: {e}")
            raise
    
    def get_instance_status(self):
        """Get instance status."""
        return self._request('GET', f'/waInstance{self.id_instance}/getStateInstance')
    
    def get_qr_code(self):
        """Get QR code for WhatsApp pairing."""
        return self._request('GET', f'/waInstance{self.id_instance}/getQRCode')
    
    def send_message(self, phone, message):
        """Send a text message."""
        data = {
            'chatId': f"{phone}@c.us",
            'message': message
        }
        return self._request('POST', f'/waInstance{self.id_instance}/sendMessage', data)
    
    def send_file(self, phone, file_url, file_name, caption=''):
        """Send a file message."""
        data = {
            'chatId': f"{phone}@c.us",
            'urlFile': file_url,
            'fileName': file_name,
            'caption': caption
        }
        return self._request('POST', f'/waInstance{self.id_instance}/sendFileByUrl', data)
    
    def send_image(self, phone, image_url, caption=''):
        """Send an image message."""
        data = {
            'chatId': f"{phone}@c.us",
            'urlFile': image_url,
            'caption': caption
        }
        return self._request('POST', f'/waInstance{self.id_instance}/sendImage', data)
    
    def send_video(self, phone, video_url, caption=''):
        """Send a video message."""
        data = {
            'chatId': f"{phone}@c.us",
            'urlFile': video_url,
            'caption': caption
        }
        return self._request('POST', f'/waInstance{self.id_instance}/sendVideo', data)
    
    def send_message_to_group(self, group_id, message):
        """Send a message to a group."""
        data = {
            'chatId': group_id,
            'message': message
        }
        return self._request('POST', f'/waInstance{self.id_instance}/sendMessage', data)
    
    def get_webhook_settings(self):
        """Get webhook settings."""
        return self._request('GET', f'/waInstance{self.id_instance}/getSettings')
    
    def set_webhook(self, webhook_url):
        """Set webhook URL."""
        data = {'webhookUrl': webhook_url}
        return self._request('POST', f'/waInstance{self.id_instance}/setSettings', data)


def get_green_api_service(tenant):
    """Get Green API service instance for a tenant."""
    creds = tenant.get_green_api_credentials()
    return GreenAPIService(
        id_instance=creds['instance_id'],
        api_token=creds['token']
    )
