#!/usr/bin/env bash
# Выгрузка каталога дилерского магазина Berlin Tires (WooCommerce Store API).
# Данные дилерские, поэтому в публичный репозиторий кладём только в зашифрованном виде (ключ расшифровки только у нас).
set -u
mkdir -p /tmp/shop && cd /tmp/shop
p=1
while :; do
  curl -sS -A "Mozilla/5.0 (Rehvo catalog sync)" --max-time 120 -D h.txt -o "p$p.json" "https://berlintires.shop/wp-json/wc/store/v1/products?per_page=100&page=$p" || break
  tp=$(grep -i '^x-wp-totalpages:' h.txt | tr -dc 0-9)
  echo "page $p of ${tp:-?}"
  [ -z "$tp" ] && break
  [ "$p" -ge "$tp" ] && break
  p=$((p+1)); sleep 1
done
# варианты (размеры/цвета) с ценой и остатком
p=1
while :; do
  curl -sS -A "Mozilla/5.0 (Rehvo catalog sync)" --max-time 120 -D h.txt -o "v$p.json" "https://berlintires.shop/wp-json/wc/store/v1/products?type=variation&per_page=100&page=$p" || break
  tp=$(grep -i '^x-wp-totalpages:' h.txt | tr -dc 0-9)
  echo "variations page $p of ${tp:-?}"
  [ -z "$tp" ] && break
  [ "$p" -ge "$tp" ] && break
  p=$((p+1)); sleep 1
done
python3 - <<'PY'
import json,glob
def load(prefix):
    out=[]
    for f in sorted(glob.glob(f'/tmp/shop/{prefix}*.json'), key=lambda x:int(x.split('/'+prefix)[-1][:-5])):
        try: out+=json.load(open(f))
        except Exception as e: print('bad',f,e)
    return out
items=load('p'); vars_=load('v')
json.dump({'products':items,'variations':vars_},open('/tmp/shop/all.json','w'))
print(len(items),'products',len(vars_),'variations')
PY
gzip -9 -f /tmp/shop/all.json
openssl rand -hex 32 > /tmp/shop/k
openssl enc -aes-256-cbc -pbkdf2 -salt -in /tmp/shop/all.json.gz -out "$GITHUB_WORKSPACE/rehvo/tools/data/shop.json.gz.enc" -pass file:/tmp/shop/k
openssl pkeyutl -encrypt -pubin -inkey "$GITHUB_WORKSPACE/rehvo/tools/pub.pem" -in /tmp/shop/k -out "$GITHUB_WORKSPACE/rehvo/tools/data/shop.key.enc"
