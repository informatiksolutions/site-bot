import os, json, typesense
from collections import defaultdict

client = typesense.Client({
  'nodes': [{ 'host': os.getenv('TYPESENSE_HOST','localhost'), 'port': int(os.getenv('TYPESENSE_PORT','8108')), 'protocol': 'http' }],
  'api_key': os.getenv('TYPESENSE_API_KEY','changeme'),
  'connection_timeout_seconds': 5
})

schema = {
  'name': 'pages',
  'fields': [
    {'name':'id','type':'string'},
    {'name':'url','type':'string'},
    {'name':'title','type':'string'},
    {'name':'content','type':'string'},
  ],
  'default_sorting_field': 'id'
}

try:
    client.collections['pages'].delete()
except Exception:
    pass
client.collections.create(schema)

with open('data/chunks.jsonl', encoding='utf-8') as f:
    docs = [json.loads(l) for l in f]

by_url = defaultdict(list)
for d in docs:
    by_url[d['url']].append(d)

bulk = []
for url, parts in by_url.items():
    title = parts[0]['title']
    snippet = ' '.join(p['content'][:200] for p in parts[:3])
    bulk.append({
        'id': parts[0]['id'],
        'url': url,
        'title': title,
        'content': snippet
    })

client.collections['pages'].documents.import_(bulk, {'action': 'upsert'})
print("Typesense importiert:", len(bulk))
