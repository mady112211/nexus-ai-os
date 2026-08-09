import httpx
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('OPENROUTER_API_KEY')

r = httpx.get(
    'https://openrouter.ai/api/v1/models',
    headers={'Authorization': f'Bearer {key}'}
)

models = r.json()['data']
free = [m for m in models if m.get('pricing', {}).get('prompt') == '0']

print('AVAILABLE FREE MODELS:')
print('=' * 80)

for m in free[:30]:
    model_id = m['id']
    context = m.get('context_length', 0)
    print(f'{model_id:60} | Context: {context}')