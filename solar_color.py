from re import search
from requests import get
from sklearn.manifold import TSNE

def get_star_data():
    with open("url.txt", "r") as f:
        urls = f.readlines()
    for url in urls:
        try:
            r = get(url[:-1])
            r.raise_for_status()
            content_disposition = r.headers["Content-disposition"]
            filename = search("filename=(.*)", content_disposition).group(1)
            with open(f"star_data\\{filename}", 'w') as f:
                f.write(r.text)
        except:
            print(f"{url} X!")

def t_SNE(data, perplexity=30.0):
    """
    data: [spec_0, spec_1,...], has shape (N_data, N_lambda)
    perplexity: perplexity
    Return 2D points after t-SNE
    """
    return TSNE(n_components=2, perplexity=perplexity).fit_transform(data)

get_star_data()
