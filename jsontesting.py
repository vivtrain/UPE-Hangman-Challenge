import json, urllib
url = "http://upe.42069.fun/Bhocy"
response = urllib.urlopen(url)
data = json.loads(response.read())
print json.dumps(data, sort_keys=True, indent=4)
