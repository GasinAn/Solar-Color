from re import search
from requests import get

URL = "https://cdsarc.unistra.fr/viz-bin/nph-Cat/"
URL += "fits?J/A+A/587/A65/spvis.dat.gz"

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
    print(f"J_A+A_587_A65_spvis.dat.gz.fits X!")
