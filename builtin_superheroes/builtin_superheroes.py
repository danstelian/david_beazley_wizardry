"""
David Beazley Wizardry
Builtin Superheroes - PyData Chicago 2016

Excellent talk about Python as a personal
productivity tool.
Also, a great example of list, (default)dict,
Counter and comprehensions collaboration.
"""


import csv
import re
from collections import Counter, defaultdict
from urllib.request import urlopen


# to download the csv file from the internets
u = urlopen('https://data.cityofchicago.org/api/views/4ijn-s7e5/rows.csv?accessType=DOWNLOAD')
data = u.read()
f = open('Food_Inspections.csv', 'wb')
f.write(data)
f.close()


# food = list(csv.DictReader(open('Food_Inspections.csv')))
# or the longer alternative

with open('Food_Inspections.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    food = list(csv_reader)  # food is a (long) list of OrderedDict type objects

length = len(food)  # 165768 entries

# let's look at the first entry
# remember that food[0] is in essence a dictionary
# for elm, dat in food[0].items():
#     print(f'{elm}: {dat}')

# how about a collection of possible outcomes
# a set comprehension, we need unique entries
print('Possible outcomes:', end=' ')
outcome = {el['Results'] for el in food}
print(outcome, end='\n\n')

# collect all the failed ones
fail = [row for row in food if row['Results'] == 'Fail']

print('Number of failed inspections: ', len(fail), end='\n\n')  # 32103 entries


# i'll use a Counter type object to find out who failed the most
# let's say top 5
print('Who failed the most:\n####################')
bad = Counter([row['DBA Name'] for row in fail])
for name, times in bad.most_common(5):
    print(f'{name}: {times}')
print()
# MCDONALD'S and MCDONALDS?
# some cleaning is required
bad = Counter([row['DBA Name'].replace("'", '').upper() for row in fail])
for name, times in bad.most_common(5):
    print(f'{name}: {times}')
print()


# how about the worst possible street to eat on
# another Counter, different filter
print('Worst street to eat on:\n#######################')
worst_street = Counter([row['Address'] for row in fail])
for name, times in worst_street.most_common(10):
    print(f'{name}: {times}')
print()
# 11601 W TOUHY AVE : 267


# group the inspections by year and count fails per street
# this needs special attention, took some time to understand
by_year = defaultdict(Counter)
for row in fail:
    by_year[row['Inspection Date'][-4:]][row['Address']] += 1

# worst street to eat on in 2017
print('Worst street to eat on in 2017:\n###############################')
for address, fails in by_year['2017'].most_common(5):
    print(f'{address}: {fails}')
print()


# all the inspections done at a certain address
ohare = [row for row in fail if row['Address'].startswith('11601 W TOUHY')]
print('Inspections at Ohare Airport:', len(ohare), end='\n\n')

# again, who are these businesses
print('All the businesses at Ohare Airport:\n####################################')
who_ohare = {row['DBA Name'] for row in ohare}
for name in sorted(who_ohare):
    print(name)
print()


# identify the worst terminal/gate in ohare airport
print('Worst terminal:')
pattern = re.compile(r'\(.+\)')  # an overkill in this context

# split the name of the place in two, grab the second part and slice out the terminal name
worst_place = Counter([row['AKA Name'].split('(')[1][:2] for row in ohare if pattern.findall(row['AKA Name'])])
for name, times in worst_place.most_common(5):
    print(f'{name}: {times}')
print()
# this worked pretty well
# soh, T3: 95


"""
# worst gates?
worst_gate = Counter([row['AKA Name'].split(' ')[-1][:-1] for row in ohare if pattern.findall(row['AKA Name'])])

# what a mess, needs a lot more work
for n, d in worst_gate.most_common(9):
    if '-' in n:
        n = n.split('-')[-1]  # a little more cleaning
    print(f'{n}: {d}')
print()
"""


# maybe I can find out who got the most fail inspections
# for every business I will save a list of inspections
inspections = defaultdict(list)
for row in ohare:
    inspections[row['DBA Name']].append(row['Inspection ID'])
count = 0
for key, value in sorted(inspections.items(), key=lambda v: len(v[1]), reverse=True):
    print(f'{key}: {len(value)}')
    count += 1
    if count == 5:
        break
print()


# what is the most common health code violation
print('Most common health code violations:')
violations = Counter()
for row in ohare:
    for viol in row['Violations'].split('|'):  # splitting the violations in a list
        violations[viol.split('.')[0].strip()] += 1  # using the number as a key and counting how many times it appears
for key, count in violations.most_common(5):
    print(f'{key}: {count}')
