import csv
import networkx as nx
import pandas as pd
import itertools
from collections import Counter

clicks = []
with open('clicks.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')

    first = True

    for row in reader:
        if first:
            first = False
            continue
        clicks.append({"pageId": int(row[1]),
                       "visitId": int(row[2]),
                       "pageName": row[3],
                       "catName": row[4],
                       "catId": int(row[5]),
                       "extCat": row[6],
                       "extCatId": int(row[7]),
                       "topicName": row[8],
                       "topidId": int(row[9]),
                       "timeOnPage": int(row[10]),
                       "pageScore": int(row[11]),
                       "sequenceNumber": int(row[12])})


# referrers = {}
# with open('search_engine_map.csv', 'r') as csvfile:
#     reader = csv.reader(csvfile, delimiter=',', quotechar='"')
#
#     first = True
#
#     for row in reader:
#         if first:
#             first = False
#             continue
#         referrers[row[0]] = {"referrerType": row[1]}


visitors = {}
with open('visitors.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')

    first = True

    for row in reader:
        if first:
            first = False
            continue
        visitors[int(row[0])] = {"referrer": row[1],
                            "day": row[2],
                            "hour": int(row[3]),
                            "lengthSeconds": int(row[4]),
                            "lengthPagecount": int(row[5])}


visits = []
for click in clicks:
    if clicks[click]["visitId"] in visitors:
        visitor = visitors[clicks[click]["visitId"]]

        if visitor["referrer"] in referrers:
            referrer = referrers[visitor["referrer"]]
        else:
            referrer = {"referrerType": None}

    else:
        continue

    click = clicks[click]

    visit = click.copy()
    visit.update(visitor)
    visit.update(referrer)

    conversions = ['APPLICATION', 'CATALOG', 'DISCOUNT', 'HOWTOJOIN', 'INSURANCE', 'WHOWEARE']

    if (visit['pageName'] in conversions):
        conversion = visit['pageName']
    else:
        conversion = ''

    visit.update({'conversion': conversion})
    visits.append(visit)


for visit in visits:
    if visit["lengthSeconds"] < 10 or visit["timeOnPage"] < 10:
        visits.remove(visit)


# Export to CSV
with open('export.csv', 'w') as csvfile:
    fieldnames = visits[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(visits)







# Association rules




# Clustering
G = nx.Graph()

for index1, visit1 in enumerate(visits):
    if index1 > 10000:
        break
    G.add_node(visit1["pageName"])

    for index2, visit2 in enumerate(visits):
        if index2 > 10000:
            break
        G.add_node(visit2["pageName"])

        if visit1["visitId"] == visit2["visitId"] and visit1 is not visit2:
            G.add_edge(visit1["pageName"], visit2["pageName"])

nx.write_gexf(G, "export.gexf")