import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = '!'
DATA_FILE = 'compras.json'
BACKUP_DIR = 'backups'

COLORS = {
    'success': 0x2ecc71,  
    'error': 0xe74c3c,    
    'info': 0x3498db      
}

ITEMS_PER_PAGE = 10

MESSAGES = {
    'item_added': '✅ Item adicionado com sucesso!',
    'item_removed': '🗑️ Item removido com sucesso!',
    'item_not_found': '❌ Esse item não foi encontrado na lista.',
    'empty_list': '📭 Nenhum item encontrado para esta lista.',
    'invalid_format': '❌ Formato inválido! Use: {}'
} 