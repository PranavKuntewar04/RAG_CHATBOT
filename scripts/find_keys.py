import json

def search(d, t):
    if isinstance(d, dict):
        for k, v in d.items():
            if t in str(v):
                print('Found in dict key:', k)
            search(v, t)
    elif isinstance(d, list):
        for x in d:
            search(x, t)

if __name__ == '__main__':
    data = json.load(open('scripts/next_data.json', encoding='utf-8'))
    search(data, 'HDFC Mid Cap Fund Direct Growth')
