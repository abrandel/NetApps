import wolframalpha


msg = input('Please enlighten me with your query : ')
app_id = 'TT9UUE-5LUGPTWK2J'
client = wolframalpha.Client(app_id)

res = client.query(msg)

print(next(res.results).text)