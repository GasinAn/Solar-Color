mkdir .\star_catalog
mkdir .\star_data
mkdir .\star_data\original
mkdir .\star_data\decompressed
mkdir .\star_data\normalized
mkdir .\sun_data
mkdir .\sun_data\normalized
cd .\sun_data
python .\convolute_solar_spec.py
copy .\lumda_spec.npy .\sun_spec.npy
cd ..
python .\solar_color.py
