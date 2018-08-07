# run this with python3 to download IERS into
# $HOME/.astropy/cache/download/py3
from astropy.time import Time
t = Time('2016:001')
t.ut1
