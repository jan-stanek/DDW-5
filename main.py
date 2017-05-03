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
        clicks.append({
            "localId": int(row[0]),
            "pageId": int(row[1]),
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
            "sequenceNumber": int(row[12])
        })


referrers = {}
with open('search_engine_map.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')

    first = True

    for row in reader:
        if first:
            first = False
            continue
        referrers[row[0]] = {
            "referrerType": row[1]
        }


visits = []
with open('visitors.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')

    first = True

    for row in reader:
        if first:
            first = False
            continue

        visitId = int(row[0])
        lengthSeconds = int(row[4])

        if lengthSeconds <= 60:
            continue

        conversions = {
            'APPLICATION': False,
            'CATALOG': False,
            'DISCOUNT': False,
            'HOWTOJOIN': False,
            'INSURANCE': False,
            'WHOWEARE': False
        }

        for click in clicks:
            if click['visitId'] == visitId and click['pageName'] in conversions:
                conversions[click['pageName']] = True

        visits.append({
            "visitId": visitId,
            "referrerType": referrers[row[1]]['referrerType'] if row[1] in referrers else None,
            "day": row[2],
            "hour": int(row[3]),
            "lengthSeconds": lengthSeconds,
            "lengthPagecount": int(row[5]),
            "application": 'TRUE' if conversions['APPLICATION'] else 'FALSE',
            "catalog": 'TRUE' if conversions['CATALOG'] else 'FALSE',
            "discount": 'TRUE' if conversions['DISCOUNT'] else 'FALSE',
            "howtojoin": 'TRUE' if conversions['HOWTOJOIN'] else 'FALSE',
            "insurance": 'TRUE' if conversions['INSURANCE'] else 'FALSE',
            "whoweare": 'TRUE' if conversions['WHOWEARE'] else 'FALSE'
        })


# Export to CSV
with open('export.csv', 'w') as csvfile:
    fieldnames = visits[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(visits)


# Association rules (source: https://edux.fit.cvut.cz/courses/MI-DDW.16/tutorials/05/start)
def frequentItems(transactions, support):
    counter = Counter()
    for trans in transactions:
        counter.update(frozenset([t]) for t in trans)
    return set(item for item in counter if counter[item] / len(transactions) >= support), counter

def generateCandidates(L, k):
    candidates = set()
    for a in L:
        for b in L:
            union = a | b
            if len(union) == k and a != b:
                candidates.add(union)
    return candidates

def filterCandidates(transactions, itemsets, support):
    counter = Counter()
    for trans in transactions:
        subsets = [itemset for itemset in itemsets if itemset.issubset(trans)]
        counter.update(subsets)
    return set(item for item in counter if counter[item] / len(transactions) >= support), counter

def apriori(transactions, support):
    result = list()
    resultc = Counter()
    candidates, counter = frequentItems(transactions, support)
    result += candidates
    resultc += counter
    k = 2
    while candidates:
        candidates = generateCandidates(candidates, k)
        candidates, counter = filterCandidates(transactions, candidates, support)
        result += candidates
        resultc += counter
        k += 1
    resultc = {item: (resultc[item] / len(transactions)) for item in resultc}
    return result, resultc

def genereateRules(frequentItemsets, supports, minConfidence):
    rules = []
    for I in frequentItemsets:
        for m in range(1, len(I)):
            for C in itertools.combinations(I, m):
                confidence = supports[I] / supports[I.difference(C)]
                if (confidence >= minConfidence):
                    lift = supports[I] / (supports[frozenset(C)] * supports[I.difference(C)])
                    rules.append({'antecedent': set(I.difference(C)), 'consequent': C[0], 'support': supports[I], 'confidence': confidence, 'lift': lift})
    return rules

def printRules(rules):
    for rule in rules:
        print(rule['antecedent'], end=' => ')
        print(rule['consequent'], end=', ')
        print(rule['support'], end=', ')
        print(rule['confidence'], end=', ')
        print(rule['lift'])


df = pd.read_csv("export.csv")
del df["visitId"]

dataset = []
for index, row in df.iterrows():
    row = [col + "=" + str(row[col]) for col in list(df)]
    dataset.append(row)
frequentItemsets, supports = apriori(dataset, 0.3)
rules = genereateRules(frequentItemsets, supports, 0.5)

rules = sorted(rules, key=lambda k: k['confidence'], reverse=True)

printRules(rules)



# Visualization
G = nx.Graph()

for index1, click1 in enumerate(clicks):
    if index1 > 10000:
        break
    G.add_node(click1["pageName"])

    for index2, click2 in enumerate(clicks):
        if index2 > 10000:
            break
        G.add_node(click2["pageName"])

        if click1["visitId"] == click2["visitId"] and click1["localId"] != click2["localId"]:
            G.add_edge(click1["pageName"], click2["pageName"])

nx.write_gexf(G, "export.gexf")