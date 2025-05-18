
from django.core.management.base import BaseCommand
from Tradingbot.utility import utility
import asyncio
from concurrent.futures import ThreadPoolExecutor
class Command(BaseCommand):
    help = 'Start shoonya'
    def handle(self, *args, **kwargs):
        obj= utility(1)

        
        t= ThreadPoolExecutor(max_workers=2)
        # t.submit(obj.shoonyawebsocket)
        t.submit(obj.angelwebsocket())
        self.stdout.write(
                self.style.SUCCESS('successful')
            )

