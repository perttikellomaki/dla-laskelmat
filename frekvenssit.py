#!/usr/bin/python3

import csv
import re

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

HAPLOT = ['1', '2', '3', '4', '5', '6', '7']

def vuosiKahdestaDigitista(rekkari):
    m = re.match( '[A-Za-z]*[0-9]*/([0-9][0-9])', rekkari.replace(' ', ''))
    if m:
        if int(m.group(1)) > 30:
            return 1900 + int(m.group(1))
        else:
            return 2000 + int(m.group(1))

def vuosiNeljastaDigitista(rekkari):
    m = re.match('[A-Za-z]*[0-9]*/([0-9][0-9][0-9][0-9])', rekkari.replace(' ', ''))
    if m:
        return int(m.group(1))

def vuosi(rekkari):
    return (vuosiNeljastaDigitista(rekkari)
            or vuosiKahdestaDigitista(rekkari)
            or 0)

def parsiHaplot(haplot):
    m = re.match('[a-zA-Z]*([0-9])[:-][a-zA-Z]*([0-9])', haplot.replace(' ', ''))
    if m:
        return (m.group(1), m.group(2))

def lisaaHaplot(vuosi_haplot, vuosi, haplot):
    if haplot:
        h1, h2 = haplot
        if vuosi not in vuosi_haplot.keys():
            vuosi_haplot[vuosi] = []
        vuosi_haplot[vuosi].append(h1)
        vuosi_haplot[vuosi].append(h2)

def vuosiHaplot():
    vuosi_haplot = {}
    with open('DLA-tyypatut-2021-01-15.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for koira, rekkari, haplot, isa, ema in reader:
            print(rekkari, vuosi(rekkari), haplot, parsiHaplot(haplot))
            lisaaHaplot(vuosi_haplot, vuosi(rekkari), parsiHaplot(haplot))
    return vuosi_haplot

def laskeVuosiKoosteet():
    kooste = {}
    vuosi_haplot = vuosiHaplot()
    for vuosi in vuosi_haplot.keys():
        frekvenssit = {}
        kooste[vuosi] = frekvenssit
        frekvenssit['kaikki'] = 0
        for haplo in HAPLOT:
            n = vuosi_haplot[vuosi].count(haplo)
            frekvenssit[haplo] = n
            frekvenssit['kaikki'] = frekvenssit['kaikki'] + n
    return kooste

def vuodetFrekvenssit(data, haplo):
    vuodet = []
    frekvenssit = []
    for vuosi in sorted(data.keys()):
        vuodet.append(vuosi)
        frekvenssit.append(100*data[vuosi][haplo] / data[vuosi]['kaikki'])
    return (vuodet, frekvenssit)

def kumulatiivinenVuosiData(ikkuna):
    kumulatiivinen = {}
    vuosi_data = laskeVuosiKoosteet()
    datan_alku = sorted(vuosi_data.keys())[0]
    alkuvuosi = sorted(vuosi_data.keys())[0] + ikkuna - 1
    loppuvuosi = sorted(vuosi_data.keys())[-1] + 1
    for vuosi in range(datan_alku, loppuvuosi):
        if vuosi >= alkuvuosi:
            kumulatiivinen[vuosi] = {}
            kumulatiivinen[vuosi]['kaikki'] = 0
            for v in range(vuosi-ikkuna+1, vuosi+1):
                print("## v", v, vuosi_data[v])
            for haplo in HAPLOT:
                kumulatiivinen[vuosi][haplo] = 0
                for v in range(vuosi-ikkuna+1, vuosi+1):
                    #print("### v, h", v, haplo)
                    kumulatiivinen[vuosi][haplo] = kumulatiivinen[vuosi][haplo] + vuosi_data[v][haplo]
                    kumulatiivinen[vuosi]['kaikki'] = kumulatiivinen[vuosi]['kaikki'] + vuosi_data[v][haplo]
            print("#### kum", vuosi, kumulatiivinen[vuosi])
    return kumulatiivinen

def suhteellistenHaplotyyppienKuvaaja():
    ikkuna = 10
    data = kumulatiivinenVuosiData(ikkuna)
    fig, ax = plt.subplots()
    for haplo in HAPLOT:
        x, y = vuodetFrekvenssit(data, haplo)
        ax.plot(x, y, label=haplo, linewidth=5)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend()
    plt.title("%s edellisenä vuonna syntyneiden kumulatiiviset haplotyypit (%%)" % ikkuna)
    plt.savefig("tulokset/%s-vuoden-ikkuna.png" % ikkuna)
    plt.show()

def testattujenLukumaarat():
    data = laskeVuosiKoosteet()
    fig, ax = plt.subplots(figsize=(8,4))
    x = sorted(data.keys())
    y = [int(data[v]['kaikki']/2) for v in x]
    ax.bar([("%s" % v)[2:] for v in x], y)
    plt.title('Testatut koirat syntymävuosittain (yhteensä %d kpl)' % sum(y))
    plt.savefig("tulokset/testattujen-lukumaarat.png")
    plt.show()

suhteellistenHaplotyyppienKuvaaja()
testattujenLukumaarat()
