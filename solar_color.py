# BnuAstro SpecGroup 1 Solar Color Research
# Resourse:
# VizieR J/A+A/587/A65, spvis.dat.gz.fits (Sun Spectrum)
# LAMOST DR6 v2, Classification="STAR", subclass="G2", FITS (Star Spectra)
# LAMOST DR6 v2, LRS A, F, G and K Star Catalog, FITS (Star Catalog)

import numpy as np
from astropy.io import fits
from gzip import GzipFile
from os import listdir
from pandas import DataFrame
from re import search
from requests import get
import warnings

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
            with open(f"star_data\\original\\{filename}", "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except:
            print(f"{url[:-1]} X!")

def decompress_star_data():
    """
    Decompress star data
    Print gzip filename if fail, then decompress next one
    Actually only used for test whether OK to read gzip file 
    """
    fits_dir, gzip_dir = "star_data\\decompressed", "star_data\\origin\\"
    gzip_filename_list = listdir("star_data\\original")
    for gzip_filename in gzip_filename_list:
        try:
            fits_filename = gzip_filename.replace(".gz", "")
            with open(f"{fits_dir}{fits_filename}", "wb") as f_fits:
                with GzipFile(f"{gzip_dir}{gzip_filename}", "rb") as f_gzip:
                    fits_content = f_gzip.read()
                f_fits.write(fits_content)
        except:
            print(f"{gzip_filename} X!")

def select_star_data():
    """
    Use T_eff, log(g) and [Fe/H] in catalog to select sun-like star data, with:
    |T_eff-5770|<200 & |log(g)-4.43775|<0.2 & |[Fe/H]|<0.5
    """
    star_params = ("tff", "tff_err", "logg", "logg_err", "feh", "feh_err")
    with fits.open("star_catalog\\dr6_v2_stellar_LRS.fits.gz") as hdul:
        catalog = hdul[1].data
    catalog = catalog[catalog["subclass"]=="G2"]
    catalog = catalog[abs(catalog["logg"]-4.43775)<0.2]
    catalog = catalog[abs(catalog["feh"])<0.5]
    catalog = catalog[abs(catalog["teff"]-5770)<200]
    obsid = catalog["obsid"]
    obsid2index = {}
    for index in range(len(catalog["obsid"])):
        obsid2index[obsid[index]] = index
    for star_param in star_params:
        exec(f"{star_param}=catalog['{star_param}']")
    star_data_filenames = listdir("star_data\\original")
    for filename in star_data_filenames:
        with fits.open(f"star_data\\original\\{filename}") as hdul:
            if hdul[0].header["OBSID"] in obsid:
                index = obsid2index[hdul[0].header["OBSID"]]
                for star_param in star_params:
                    exec(f"hdul[0].header['{star_param}']={star_param}[index]")
                hdul.writeto(f"star_data\\selected\\{filename}")

def normalize_star_data():
    """
    Normalize star data
    """
    flist = listdir("star_data\\selected")
    stableindex = np.array([0,200,2001,1771,841,540,339,228,2506,2472,-201,-1])
    pm = np.array([-5,-4,-3,-2,-1,+1,+2,+3,+4,+5])
    warnings.filterwarnings("ignore")
    for fname in flist:
        with fits.open(f"star_data\\selected\\{fname}") as hdul:
            odata = hdul[0].data[0]
            good_data_indexs = range(200, odata.size-200)
            for i in good_data_indexs:
                if (hdul[0].data[[4,3],i]!=0).any():
                    odata[i] = np.mean(odata[i+pm])
            n_deal = 0
            need_deal = True
            while need_deal:
                need_deal = False
                for i in good_data_indexs:
                    odata_i = odata[i]
                    odata_near = odata[i+pm]
                if np.std(odata_near, ddof=1)*3<(odata_i-np.mean(odata_near)):
                    need_deal = True
                    odata_i = np.mean(odata_near)
                n_deal += 1
                if n_deal >= 3:
                    break
            selectedindex = []
            for i in good_data_indexs:
                if (odata[i+pm]<odata[i]).all():
                    selectedindex.append(i)
            selectedindex = np.concatenate((stableindex, selectedindex))
            ndata = np.full(odata.size, np.nan)
            ndata[selectedindex] = odata[selectedindex]
            pandas_dataframe = DataFrame(data=ndata)
            pandas_dataframe.index = hdul[0].data[2]
            pandas_dataframe = pandas_dataframe.interpolate(method="values")
            ndata = pandas_dataframe.to_numpy().reshape(odata.size)
            hdul[0].data[0] = odata/ndata
            hdul.writeto(f"star_data\\normalized\\{fname}")

def normalize_sun_data():
    """
    Normalize sun data
    """
    odata = np.load("solar_data\\sun_spec.npy")
    pm = np.array([-5,-4,-3,-2,-1,+1,+2,+3,+4,+5])
    selectedindex = [0,-1]
    for i in range(5, odata.shape[1]-5):
        if (odata[1][i+pm]<odata[1][i]).all():
            selectedindex.append([i])
    ndata = np.full(odata.shape[1], np.nan)
    ndata[selectedindex] = odata[1][selectedindex]
    pandas_dataframe = DataFrame(data=ndata)
    pandas_dataframe.index = odata[0]
    pandas_dataframe = pandas_dataframe.interpolate(method="values")
    ndata = pandas_dataframe.to_numpy().reshape(odata.shape[1])
    odata[1] /= ndata
    np.save("solar_data\\normalized\\normal_sun_spec.npy", odata)
    hdu = fits.PrimaryHDU(odata)
    hdu.header["ROW1"] = "WAVELENGTH"
    hdu.header["ROW2"] = "FLUX"
    hdul = fits.HDUList([hdu])
    hdul.writeto("solar_data\\normalized\\normal_sun_spec.fits")

if __name__ == "__main__":
    whether_get = input("Download star data?([Y]/N)")
    if whether_get.upper() == "" or whether_get.upper() == "Y":
        print("Download!")
        get_star_data()
        print("OK!")
    else:
        print("Pass!")
    whether_decompress = input("Decompress star data?(Y/[N])")
    if whether_decompress.upper() == "" or whether_decompress.upper() == "N":
        print("Decompress!")
        decompress_star_data()
        print("OK!")
    else:
        print("Pass!")
    input("Press [Enter] to continue.")
    print("Selecting star data...")
    select_star_data()
    print("OK!")
    print("Normalizing star data...")
    normalize_star_data()
    print("OK!")
    print("Normalizing sun data...")
    normalize_sun_data()
    print("OK!")
