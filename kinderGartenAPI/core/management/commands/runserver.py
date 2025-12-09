from django.core.management.commands.runserver import Command as BaseRunserverCommand
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file
ENV_PATH = Path(__file__).resolve().parent.parent.parent.parent / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


class Command(BaseRunserverCommand):
    def handle(self, addrport="", *args, **options):
        # Get server address from environment or use default
        dev_server_address = os.environ.get("DEV_SERVER_ADDRESS", "127.0.0.1:8000")

        # If no address provided, use the environment setting
        if not addrport:
            addrport = dev_server_address

        return super().handle(addrport, *args, **options)
