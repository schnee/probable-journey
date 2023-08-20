from urllib.parse import urlparse
from urllib.parse import parse_qs
urlparse("scheme://netloc/path;parameters?query#fragment")

o = urlparse("http://docs.python.org:80/3/library/urllib.parse.html?"
             "highlight=params#url-parsing")
print(o)
print(o.query)


o = urlparse("https://maps.google.com/maps?q=40.719484,-74.047266")
print(o)
qdict = parse_qs(o.query)
print(qdict.get('q'))

latlng = qdict.get('q')[0]
num1_str, num2_str = latlng.split(",")
latitude = float(num1_str.strip())
longitude = float(num2_str.strip())
print(latitude,longitude)

o = urlparse('1,2')
print(o)

def get_latlng(url):
    o = urlparse(url)
    if o.scheme:
        qdict = parse_qs(o.query)
        latlng = qdict.get('q')[0]
    else:
        latlng = url
    return latlng

print(get_latlng("1,2"))
print(get_latlng("https://maps.google.com/maps?q=40.719484,-74.047266"))
