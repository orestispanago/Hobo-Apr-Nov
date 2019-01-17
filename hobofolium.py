import folium
import glob
import pandas as pd
import numpy as np
import base64
from folium import IFrame
import matplotlib.pyplot as plt
import os

# Use this to avoid displaying all plots
import matplotlib

matplotlib.use('Agg')

cwd = os.getcwd()
outdir = cwd + '/output/'
if not os.path.exists(outdir):
    os.makedirs(outdir)

csvfiles = glob.glob(cwd + '/raw/*.csv')
hobonames = [os.path.split(i)[1][:3] for i in csvfiles]


def load_dataset():
    """ Reads hobo files to list of multiindex dataframes, concatenates them
    and makes timeseries"""
    dflist = []
    for fname, hname in zip(csvfiles, hobonames):
        df = pd.read_csv(fname, usecols=(1, 2, 3), skiprows=2, index_col=0,
                         parse_dates=True)
        df.columns = pd.MultiIndex.from_tuples([(hname, 'T'), (hname, 'RH')])
        df = df.dropna()# dumps rows with NaNs
        dflist.append(df)
    dfout = pd.concat(dflist, axis=1)
    # dfout = dfout.dropna()
    dfout = dfout.asfreq('30min')
    return dfout


class Hobo:
    stations = []
    locations = [["H26", "LapUp", 38.291969, 21.788156],
                 ["H27", "Aritis", 38.284469, 21.765306],
                 ["H28", "Zakynthou", 38.259222, 21.746347],
                 ["H31", "Gounari", 38.244875, 21.731675],
                 ["H32", "Fintiou", 38.234419, 21.735664],
                 ["H29", "Isaiou", 38.225647, 21.733011],
                 ["H52", "Dimaion", 38.211322, 21.716844],
                 ["H53", "Mintilogli", 38.186581, 21.706458]]

    def __init__(self, name, alias, coords):
        self.name = name
        self.alias = alias
        self.coords = coords  # list: [lat,lon]
        Hobo.stations.append(self)



def save_jpg(h):
    plt.style.use('seaborn')
    fig = plt.figure()
    temps[h.name].plot(figsize=(8, 3))
    plt.title(h.alias)
    plt.xlabel('Date - time, UTC')
    plt.tight_layout()
    plt.savefig(outdir + h.name + '.jpg')


def jpg2popup(h):
    encoded = base64.b64encode(
        open(outdir + h.name + '.jpg', 'rb').read()).decode()
    html = '<img src="data:image/jpeg;base64,{}">'.format
    resolution, width, height = 20, 40, 17
    iframe = IFrame(html(encoded), width=(width * resolution) + 20,
                    height=(height * resolution) + 20)
    popup = folium.Popup(iframe, max_width=1000)
    fgn.add_child(
        folium.CircleMarker(location=hobo.coords, radius=8, color='grey',
                            fill_color='green', fill_opacity=0.8, popup=popup))



for i in Hobo.locations:
    Hobo(i[0], i[1], i[2:])

large = load_dataset()

temps = large.xs('T', axis=1, level=1, drop_level=True)
# temps = temps.resample('W').mean()
rh = large.xs('RH', axis=1, level=1, drop_level=True)

map = folium.Map(location=[38.234419, 21.735664], zoom_start=12,
                 tiles="OpenStreetMap")
map.add_child(folium.TileLayer(name="CartoDB.DartMatter",
                               tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                               attr='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'))
fg = folium.FeatureGroup(name="Station aliases")
fgn = folium.FeatureGroup(name="Temperature graphs")

# for hobo in Hobo.stations:
#     fg.add_child(folium.CircleMarker(location=hobo.coords, radius=7,color='red', fill_color='green', fill_opacity=0.8,popup=hobo.alias))

for hobo in Hobo.stations:
    save_jpg(hobo)
    jpg2popup(hobo)

map.add_child(fg)
map.add_child(fgn)
map.add_child(folium.LayerControl())
map.save(outdir + 'map3.html')
