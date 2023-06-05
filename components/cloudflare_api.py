"""
This class contains the functions needed to collect and update data at Cloudflare
"""
import logging
import socket
import requests


class CloudflareAPI:
    """
    This class contains the functions needed to collect and update data at Cloudflare
    """

    def __init__(self, mail, api_key) -> None:
        self.logger = logging.getLogger(__name__)

        self.url = 'https://api.cloudflare.com/client/v4/'
        self.mail = mail
        self.api_key = api_key

    def check_connection(self):
        """
        Checks internet connection

        Returns:
            _type_: Returns True if the connection is established
        """
        try:
            hostname = socket.gethostbyname("www.cloudflare.com")
            socket.create_connection((hostname, 80), 3)
            return True
        except socket.gaierror:
            return False

    def get_public_ip(self, ip_check_service: list, timeout: int = 30):
        """_summary_

        Args:
            ip_check_service (list): Service List to validate your Public IP
            timeout (int, optional): Set the connection timeout. Defaults to 30.

        Returns:
            _type_: Return your Public IP
        """
        for service in ip_check_service:
            try:
                response = requests.get(service, timeout=timeout)
                if response.status_code == 200:
                    return response.text.strip()
            except requests.exceptions.RequestException:
                continue
        return None

    def get_dns_ip(self, zone_id: str, domain_name: str, timeout: int = 30):
        """
        Get current DNS record for the specified domain

        Args:
            zone_id (str): Zone ID to your Domain
            domain_name (str): Domain Name
            timeout (int, optional): _description_. Defaults to 30.

        Returns:
            _type_: Return zone informations
        """
        headers = {
            'X-Auth-Email': self.mail,
            'X-Auth-Key': self.api_key,
            'Content-Type': 'application/json',
        }

        params = {
            'name': domain_name,
        }

        response = requests.get(f'{self.url}zones/{zone_id}/dns_records',
                                headers=headers,
                                params=params,
                                timeout=timeout)

        if response.status_code == 200:
            records = response.json()['result']
            if records:
                return records[0]
        return None

    def update_dns(self, record_id: str, zone_id: str, name: str,
                   record_type: str, content: str, **kwargs):
        """
        Realiza o update do IP na Cloudflare

        Args:
            record_id (str): Record ID
            zone_id (str): Zone ID
            name (str): Domain Name
            record_type (str): DNS Record type
            content (str): New Public IP
            ttl (int, optional): _description_. Defaults to 120.
            proxied (bool, optional): _description_. Defaults to True.
            timeout (int, optional): _description_. Defaults to 30.
        """
        ttl = kwargs.get("ttl", 120)
        proxied = kwargs.get('proxied', True)
        timeout = kwargs.get("timeout", 30)

        headers = {
            'X-Auth-Email': self.mail,
            'X-Auth-Key': self.api_key,
            'Content-Type': 'application/json',
        }

        data = {
            'type': record_type,
            'name': name,
            'content': content,
            'ttl': ttl,
            'proxied': proxied,
        }

        response = requests.put(f'{self.url}zones/{zone_id}/dns_records/{record_id}',
                                json=data,
                                headers=headers,
                                timeout=timeout)

        if response.status_code == 200:
            self.logger.info("DNS record updated successfully: %s (%s) -> %s",
                             name,
                             record_type,
                             content)

        else:
            self.logger.error(
                "Failed to update DNS record: %s", response.json())
