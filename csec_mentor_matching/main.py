#!/usr/bin/python3

### REFERENCES
#   https://pbpython.com/pandas-google-forms-part1.html

from __future__ import print_function

import auth
import analysis
import matcher

import pandas as pd
import numpy as np
from functools import reduce
import sys

MENTEE_SPREADSHEET = '1byO5GRxBVTaDVXNR_JeykVWwA9LrirKhmjjn_8TIUXk'
MENTOR_SPREADSHEET = '1SMl0cjfrLgU6D2iYtiQwdl1O5kHTdGdyDqWdysdwTWg'
MENTOR_YEAR_SPREADSHEET = '15sDdZuQmdCkCgJEI2tXgRahDH2s0_GfXaG4kVIz9gsU'

OUTPUT_FILE = "./matching.xlsx"

service = auth.get_service('../../client_secret.json')

mentors_year = auth.get_sheet_data(service, MENTOR_YEAR_SPREADSHEET) 
mentees = auth.get_sheet_data(service, MENTEE_SPREADSHEET) 
mentors = auth.get_sheet_data(service, MENTOR_SPREADSHEET) 

print('+' * 80)

mentors = analysis.mentor_analysis((mentors, mentors_year))
mentees = analysis.mentee_analysis(mentees)

print('+' * 80)

analysis.detect_duplicates(mentors, mentees)

mentee_set1, mentee_set2 = analysis.arrange_mentees(mentees, len(mentors[0]))


#mentors = list(mentors)
#mentors.append([np.zeros((len(mentors[0]),))])
#mentors = tuple(mentors)

#mentors_temp = list( map( lambda x: np.asarray(x, dtype=type(x[0])), mentors ) )
#mentees = tuple( list( map( lambda x: np.asarray(x, dtype=type(x[0])), mentees ) ) )
#mentors_split = []
#mx = max(mentors[4])
#multi = 0
#for i in range(mx, -1, -1) :
#    mask = (mentors_temp[4] == i)
#    temp = mentors_temp[0][mask] 
#    len_mentors = len(temp)
#    len_mentees = np.sum(np.asarray(mentees[3]) <= i)
#    # len_mentees is obviously non-zeros because it's set of all mentees irrespective of year
#    if len_mentors != 0 :
#        factor = (int(len_mentees / len_mentors) + (1 if len_mentees % len_mentors else 0)) + 1
#    else:
#        factor = 1
#    temp = [temp, mentors_temp[1][mask], mentors_temp[2][mask], mentors_temp[3][mask], mentors_temp[4][mask]]
#    temp = list( map( lambda x : np.repeat(x, factor), temp ) )
#    multi += len_mentors*factor
#    print(f"Value of multi: {multi}")
#    mentors_split += [temp]

## all this fucking banana reduce for just merging the individual lists into a mega list
#mentors = reduce(lambda x, y: [np.append(u[0], u[1]) for u in zip(x, y)], mentors_split, [[] for _ in mentors_split[0]])
#mentors = list( map( list, mentors ) )

print('+' * 80)

# mentees should be a perfect multiple of mentor numbers
# this is necessitated by the matching API
mentees = mentee_set1
multi = len(mentees[0]) 
costs = analysis.costs(multi, mentees[2], mentees[3], mentors[2], mentors[3], mentors[4])
temp = matcher.match(multi, len(mentors[0]), costs)
temp = list( zip(temp[:len(mentees[0])], list(range(len(mentees[0])))) )

assignment = list(map( lambda x : (mentors[0][x[0]], mentors[1][x[0]], mentors[4][x[0]], mentees[0][x[1]], mentees[1][x[1]], mentees[3][x[1]]), temp))

print('+' * 80)

mentees = mentee_set2
multi = len(mentors[0])
costs = analysis.costs(multi, mentees[2], mentees[3], mentors[2], mentors[3], mentors[4])
temp = matcher.match(multi, len(mentors[0]), costs)
temp = list( zip(temp[:len(mentees[0])], list(range(len(mentees[0])))) )

assignment += list(map(lambda x : (mentors[0][x[0]], mentors[1][x[0]], mentors[4][x[0]], mentees[0][x[1]], mentees[1][x[1]], mentees[3][x[1]]), temp))
assignment = pd.DataFrame(assignment)

print('+' * 80, file=sys.stderr)
assignment.columns = ['Mentor Email', 'Mentor Name', 'Mentor Year', 'Mentee Email', 'Mentee Name', 'Mentee Year']
print(assignment)


# some checks before saving!
print('+' * 80)
print(set(mentees[0]) - set(assignment['Mentee Email']))
assert len(set(assignment['Mentee Email'])) == len(mentees[0]) , "Not all mentees have been alotted mentors!"
print("The assertion that all mentors have at least one mentee: Passed")

print('+' * 80)
assert len(set(assignment['Mentor Email'])) == len(mentors[0]) , "Not all mentors have been alotted mentees!"
print("The assertion that all mentors have at least one mentee: Passed")

print('+' * 80)
temp = np.asarray(assignment.groupby(['Mentor Email', 'Mentor Name']).size())
assert (temp >= 3).all() , "Of all mentors, not all have been alotted >= 3 mentees!"
print("The assertion that all mentors have at least >= 3 mentees: Passed")

print("The assertion that Mentor Year >= Mentee Year: " + ("Failed" if np.all(assignment['Mentor Year'] >= assignment['Mentee Year'] ) else "Passed"))

assignment = assignment.sort_values(['Mentor Email', 'Mentor Name'])
assignment.style.hide_index()

exit(42)

print('+' * 80)
prompt = "Please Enter your choice to save to {} [y/n] ".format(OUTPUT_FILE)
print(prompt, end="")
c = input()
while(c[0] != 'y' and c[0] != 'n'):
    print("Unrecognized Choice!!!")
    print(prompt, end="")
    c = input()

if c[0] == 'y' :
    #assignment.to_excel(OUTPUT_FILE, sheet_name="mentee allotment", index=False)
    assignment[['Mentor Email', 'Mentor Name', 'Mentee Email', 'Mentee Name']].to_excel(OUTPUT_FILE, sheet_name="mentee allotment", index=False)

service.close()
