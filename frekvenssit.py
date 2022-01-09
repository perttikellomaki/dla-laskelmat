#!/usr/bin/python3

import csv
import re

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

yksittaiset = 'yksittäiset'
parit = 'parit'
kaikkihaplot = 'kaikkihaplot'
kaikkiparit = 'kaikkiparit'
homotsygootit = 'homotsygootit'

HAPLOT = [1, 2, 3, 4, 5, 6, 7]
HAPLOPARIT = [(h1, h2) for h1 in HAPLOT for h2 in range(h1, HAPLOT[-1]+1)]

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
        return (int(m.group(1)), int(m.group(2)))

def lisaaHaplot(vuosi_haplot, vuosi, haplot):
    if haplot:
        h1, h2 = haplot
        if vuosi not in vuosi_haplot.keys():
            vuosi_haplot[vuosi] = {yksittaiset: [], parit: []}
        vuosi_haplot[vuosi][yksittaiset].append(h1)
        vuosi_haplot[vuosi][yksittaiset].append(h2)
        vuosi_haplot[vuosi][parit].append((min(h1, h2), max(h1, h2)))

def kanoninen(koira):
    return re.sub(r'[^A-Za-z]', '', koira).lower()

def vuosiHaplot(skipattavat=[]):
    skipattavat_kanoniset = [kanoninen(x) for x in skipattavat]
    vuosi_haplot = {}
    with open('DLA-tyypatut-2021-01-15.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for koira, rekkari, haplot, isa, ema in reader:
            if kanoninen(koira) in skipattavat_kanoniset:
                print('Skipattu %s' % koira)
            else:
                print(rekkari, vuosi(rekkari), haplot, parsiHaplot(haplot))
                lisaaHaplot(vuosi_haplot, vuosi(rekkari), parsiHaplot(haplot))
    return vuosi_haplot

def laskeVuosiKoosteet(vuosi_haplot):
    kooste = {}
    for vuosi in vuosi_haplot.keys():
        frekvenssit = {}
        kooste[vuosi] = frekvenssit
        frekvenssit[kaikkihaplot] = 0
        frekvenssit[homotsygootit] = 0
        for haplo in HAPLOT:
            n = vuosi_haplot[vuosi][yksittaiset].count(haplo)
            frekvenssit[haplo] = n
            frekvenssit[kaikkihaplot] = frekvenssit[kaikkihaplot] + n
        for h1, h2 in HAPLOPARIT:
            frekvenssit[(h1, h2)] = vuosi_haplot[vuosi][parit].count((h1, h2))
            if h1 == h2:
                n = vuosi_haplot[vuosi][parit].count((h1, h2))
                frekvenssit[homotsygootit] = frekvenssit[homotsygootit] + n
    return kooste

def vuodetFrekvenssitHaplo(data, haplo):
    vuodet = []
    frekvenssit = []
    for vuosi in sorted(data.keys()):
        vuodet.append(vuosi)
        frekvenssit.append(100*data[vuosi][haplo] / data[vuosi][kaikkihaplot])
    return (vuodet, frekvenssit)

def vuodetFrekvenssitPari(data, pari):
    vuodet = []
    frekvenssit = []
    for vuosi in sorted(data.keys()):
        vuodet.append(vuosi)
        frekvenssit.append(100*data[vuosi][pari] / data[vuosi][kaikkiparit])
    return (vuodet, frekvenssit)

def kumulatiivinenVuosiData(ikkuna, skipattavat=[]):
    kumulatiivinen = {}
    vuosi_data = laskeVuosiKoosteet(vuosiHaplot(skipattavat=skipattavat))
    datan_alku = sorted(vuosi_data.keys())[0]
    alkuvuosi = sorted(vuosi_data.keys())[0] + ikkuna - 1
    loppuvuosi = sorted(vuosi_data.keys())[-1] + 1
    for vuosi in range(datan_alku, loppuvuosi):
        if vuosi >= alkuvuosi:
            kumulatiivinen[vuosi] = {}
            kumulatiivinen[vuosi][kaikkihaplot] = 0
            kumulatiivinen[vuosi][kaikkiparit] = 0
            for v in range(vuosi-ikkuna+1, vuosi+1):
                if v in vuosi_data:
                    print("## v", v, vuosi_data[v])
                else:
                    print("## v", v)
            for alkio in HAPLOT + HAPLOPARIT + [homotsygootit]:
                kumulatiivinen[vuosi][alkio] = 0
                for v in range(vuosi-ikkuna+1, vuosi+1):
                    n = vuosi_data[v][alkio] if v in vuosi_data else 0
                    #print("### v, h", v, alkio)
                    kumulatiivinen[vuosi][alkio] = kumulatiivinen[vuosi][alkio] + n
                    if alkio in HAPLOT:
                        kumulatiivinen[vuosi][kaikkihaplot] = kumulatiivinen[vuosi][kaikkihaplot] + n
                    elif alkio in HAPLOPARIT:
                        kumulatiivinen[vuosi][kaikkiparit] = kumulatiivinen[vuosi][kaikkiparit] + n
            print("#### kum", vuosi, kumulatiivinen[vuosi])
    return kumulatiivinen

def suhteellistenHaplotyyppienKuvaaja():
    ikkuna = 10
    data = kumulatiivinenVuosiData(ikkuna)
    fig, ax = plt.subplots()
    for haplo in HAPLOT:
        x, y = vuodetFrekvenssitHaplo(data, haplo)
        ax.plot(x, y, label=haplo, linewidth=5)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend()
    plt.title("%s edellisenä vuonna syntyneiden kumulatiiviset haplotyypit (%%)" % ikkuna)
    plt.savefig("tulokset/%s-vuoden-ikkuna.png" % ikkuna)
    plt.show()

def suhteellistenHomotsygoottienKuvaaja():
    ikkuna = 10
    data = kumulatiivinenVuosiData(ikkuna)
    fig, ax = plt.subplots()
    for pari in HAPLOPARIT:
        h1, h2 = pari
        if h1 == h2:
            x, y = vuodetFrekvenssitPari(data, pari)
            ax.plot(x, y, label=pari, linewidth=5)
    x, y = vuodetFrekvenssitPari(data, homotsygootit)
    ax.plot(x, y, label='kaikki', linewidth=5)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend()
    plt.title("%s edellisenä vuonna syntyneiden kumulatiiviset homotsygoottimäärät (%%)" % ikkuna)
    plt.savefig("tulokset/%s-vuoden-ikkuna-homotsygootit.png" % ikkuna)
    plt.show()

def testattujenLukumaarat():
    data = laskeVuosiKoosteet(vuosiHaplot())
    fig, ax = plt.subplots(figsize=(8,4))
    x = sorted(data.keys())
    y = [int(data[v][kaikkihaplot]/2) for v in x]
    ax.bar([("%s" % v)[2:] for v in x], y)
    plt.title('Testatut koirat syntymävuosittain (yhteensä %d kpl)' % sum(y))
    plt.savefig("tulokset/testattujen-lukumaarat.png")
    plt.show()

def testattujenJaRekisteroityjenLukumaarat():
    width = 0.5
    rekisteroinnit = {}
    with open('rekisteroinnit.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for vuosi,lukumaara in reader:
            rekisteroinnit[int(vuosi)] = int(lukumaara)
    data = laskeVuosiKoosteet(vuosiHaplot())
    x = sorted(data.keys())
    testatut = [int(data[v][kaikkihaplot]/2) for v in x]
    rekisteroidyt = [rekisteroinnit[v] for v in x]
    n = len(x)
    r = np.arange(n)
    plt.bar(r, rekisteroidyt, width=width, label='rekisteröidyt')
    plt.bar(r + width, testatut, width=width, label='testatut')
    plt.xticks(r + width/2, [("%s" % v if v % 5 == 0 else "") for v in x])
    plt.title('Testatut koirat syntymävuosittain (yhteensä %d kpl)' % sum(testatut))
    plt.savefig("tulokset/testattujen-ja-rekisteroityjen-lukumaarat.png")
    plt.legend()
    plt.show()

def uusienTestattujenFrekvenssit():
    skipattavat = []
    with open('testatut-2010.csv') as testatut:
        for line in testatut:
            skipattavat.append(line.strip())
    haplot = vuosiHaplot(skipattavat=skipattavat)
    koosteet = laskeVuosiKoosteet(haplot)
    kumulatiivinen = kumulatiivinenVuosiData(20, skipattavat=skipattavat)
    vuosi21 = kumulatiivinen[2021]
    with open('tulokset/vuosina-2010-2021-testattujen-frekvenssit.txt', 'w') as f:
        f.write('Vuosina 2010-2021 testattujen koirien haplotyyppien frekvenssit\n')
        for haplo in HAPLOT:
            f.write('Parta%s:  %.2f\n' %
                    (haplo,
                     100.0 * vuosi21[haplo] / vuosi21[kaikkihaplot]))

suhteellistenHaplotyyppienKuvaaja()
suhteellistenHomotsygoottienKuvaaja()
testattujenLukumaarat()
testattujenJaRekisteroityjenLukumaarat()
uusienTestattujenFrekvenssit()
