from re import search
from requests import get
from sklearn.manifold import TSNE

def get_star_data():
    """
    Download star data from LAMOST(DR6_v2, STAR:G2)
    Need URLs of data, in url.txt
    """
    with open("url.txt", "r") as f:
        urls = f.readlines()
    for url in urls:
        try:
            r = get(url[:-1], stream=True)
            r.raise_for_status()
            content_disposition = r.headers["Content-disposition"]
            filename = search("filename=(.*)", content_disposition).group(1)
            with open(f"star_data\\origin\\{filename}", "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except:
            print(f"{url[:-1]} X!")

def t_SNE(data, perplexity=30.0):
    """
    data: [spec_0, spec_1,...], has shape (N_data, N_lambda)
    perplexity: perplexity
    Return 2D points after t-SNE
    """
    return TSNE(n_components=2, perplexity=perplexity).fit_transform(data)

#get_star_data()
