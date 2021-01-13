from re import search
from requests import get

URL = "http://dr6.lamost.org/v2/catdl?name=dr6_v2_stellar_LRS.fits.gz"

try:
    r = get(URL, stream=True)
    r.raise_for_status()
    content_disposition = r.headers["Content-disposition"]
    filename = search("filename=(.*)", content_disposition).group(1)
    with open(f"star_catalog\\{filename}", "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
except:
    print(f"dr6_v2_stellar_LRS.fits.gz X!")
