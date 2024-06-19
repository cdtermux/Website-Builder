import http.client

conn = http.client.HTTPSConnection("pay-api.binjie.fun")
payload = ''
headers = {
   'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
}
conn.request("GET", "/api/getKeyInfo?key=%E4%BD%A0%E8%B4%AD%E4%B9%B0%E7%9A%84key", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))