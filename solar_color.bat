cd .\solar_data
python .\convolute_solar_spec.py
copy .\lumda_spec.npy .\sun_spec.npy
cd ..
python .\solar_color.py
