# BnuAstro SpecGroup 1 Solar Color Research
# Resourse:
# VizieR J/A+A/587/A65, spvis.dat.gz.fits (Sun Spectrum)
# LAMOST DR6 v2, Classification="STAR", subclass="G2", FITS (Star Spectra)
# LAMOST DR6 v2, LRS A, F, G and K Star Catalog, FITS (Star Catalog)

from astropy.io import fits
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
    with open("urls.txt", "r") as f:
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

def get_sun_like_star_data():
    """
    Use T_eff, log(g) and [Fe/H] in catalog to get sun-like star data, with:
    |T_eff-5770|<200 & |log(g)-4.43775|<0.2 & |[Fe/H]|<0.5
    Return (sun-like star file names, sun-like star spec obsids)
    """
    star_filenames = listdir("star_data")[1:]
    with fits.open("star_catalog\\dr6_v2_stellar_LRS.fits") as hdul:
        catalog = hdul[1].data
    catalog = catalog[catalog["subclass"]=="G2"]
    catalog = catalog[abs(catalog["logg"]-4.43775)<0.2]
    catalog = catalog[abs(catalog["feh"])<0.5]
    catalog = catalog[abs(catalog["teff"]-5770)<200]
    selected_spec_obsids = catalog["obsid"]
    selected_star_filenames = []
    for filename in star_filenames:
        with fits.open(f"star_data\\{filename}") as hdul:
            if hdul[0].header["OBSID"] in selected_spec_obsids:
                selected_star_filenames.append(filename)
    return selected_star_filenames, selected_spec_obsids

def t_SNE(data, perplexity=30.0):
    """
    data: [spec_0, spec_1,...], has shape (N_data, N_lambda)
    perplexity: perplexity
    Return 2D points after t-SNE
    """
    return TSNE(n_components=2, perplexity=perplexity).fit_transform(data)

# get_star_data()
# decompress_star_data()
# star_filenames, spec_obsids = get_sun_like_star_data()
