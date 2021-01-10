from gzip import GzipFile
from os import listdir
from re import search
from requests import get
from sklearn.manifold import TSNE

def get_star_data():
    """
    Download star data from LAMOST(DR6_v2, STAR:G2)
    Need URLs of data, in url.txt
    Print URL if fail, then download next one 
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

def decompress_star_data():
    """
    Decompress star data
    Print gzip filename if fail, then decompress next one
    """
    fits_dir, gzip_dir = "star_data\\", "star_data\\origin\\"
    gzip_filename_list = listdir("star_data\\origin")
    for gzip_filename in gzip_filename_list:
        try:
            fits_filename = gzip_filename.replace(".gz", "")
            with open(f"{fits_dir}{fits_filename}", "wb") as f_fits:
                with GzipFile(f"{gzip_dir}{gzip_filename}", "rb") as f_gzip:
                    fits_content = f_gzip.read()
                f_fits.write(fits_content)
        except:
            print(f"{gzip_filename} X!")

def t_SNE(data, perplexity=30.0):
    """
    data: [spec_0, spec_1,...], has shape (N_data, N_lambda)
    perplexity: perplexity
    Return 2D points after t-SNE
    """
    return TSNE(n_components=2, perplexity=perplexity).fit_transform(data)

#get_star_data()
#decompress_star_data()
