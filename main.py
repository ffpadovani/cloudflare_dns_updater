"""
Script that updates the public IP in a Cloudflare zone
"""
import os
import logging
import logging.config
import argparse
import json
import time
import schedule

from components.cloudflare_api import CloudflareAPI


def check_update_dns():
    """
    Main function from script that updates the public IP in a Cloudflare zone
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--api_key",
                        help="Your Cloudflare API Key",
                        required=True)
    parser.add_argument("-d", "--domains",
                        help='Exemple: {"zone_id": "id", "domain": "exemple.com", "proxied": True}',
                        action='append',
                        required=True)
    parser.add_argument("-e", "--email",
                        help="Your email",
                        required=True)
    parser.add_argument("-i", "--ip_checker",
                        help="List of Services for Public IP Query",
                        default=['https://adresameaip.ro/ip', 'https://api.ipify.org'])
    args = parser.parse_args()

    conn = CloudflareAPI(mail=args.email, api_key=args.api_key)

    if not conn.check_connection():
        logger.error("No internet connection. Skipping check and update.")
        return

    public_ip = conn.get_public_ip(ip_check_service=args.ip_checker)

    if not public_ip:
        logger.error(
            "Failed to retrieve public IP. Skipping check and update.")
        return

    for domain in args.domains:
        domain = json.loads(domain.replace("\'", "\""))

        zone_id = domain['zone_id']
        domain_name = domain['domain']
        proxied = domain['proxied']

        record = conn.get_dns_ip(zone_id=zone_id, domain_name=domain_name)

        if not record:
            logger.error("DNS record for %s not found.", domain_name)
            return

        if public_ip == record['content']:
            logger.info(
                "IP addresses are the same for %s. No update needed.", domain_name)
            return

        conn.update_dns(record_id=record['id'],
                        zone_id=record['zone_id'],
                        name=domain_name,
                        record_type=record['type'],
                        content=public_ip,
                        proxied=proxied)


if __name__ == "__main__":
    PATH = os.path.dirname(os.path.abspath(__file__))
    logging.config.fileConfig(f"{PATH}/logging.conf")
    logger = logging.getLogger(__name__)

    schedule.every(5).minutes.do(check_update_dns).run()

    while True:
        schedule.run_pending()
        time.sleep(1)
