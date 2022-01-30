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
import z3

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


print('+' * 80)

osts = analysis.costs(len(mentees[0]), mentees[2], mentees[3], mentors[2], mentors[3], mentors[4])

opt = z3.Optimize()

tee_tor_vars = [[Bool(f'var_{i}_{j}') for j in range(len(mentees[0]))] for i in range(len(mentors[0]))]

opt.add(analysis.mentor_count_constraint(tee_tor_vars, costs, 3))

res = analysis.matching(opt, tee_tor_vars, costs)

assert res == sat

m = opt.model()

assignment = []
for i in range(len(mentors[0])):
    for j in range(len(mentees[0])):
        if (m[tee_tor_vars[i][j]]):
            assignment.append((i,j))

assignment = list(map( lambda x : (mentors[0][x[0]], mentors[1][x[0]], mentors[4][x[0]], mentees[0][x[1]], mentees[1][x[1]], mentees[3][x[1]]), assignment))
assignment = pd.DataFrame(assignment)
assignment.columns = ['Mentor Email', 'Mentor Name', 'Mentor Year', 'Mentee Email', 'Mentee Name', 'Mentee Year']
print("The assertion that Mentor Year >= Mentee Year: " + ("Failed" if np.all(assignment['Mentor Year'] >= assignment['Mentee Year'] ) else "Passed"))

assignment = assignment.sort_values(['Mentor Email', 'Mentor Name'])
assignment.style.hide_index()

print('+' * 80)
assert len(set(assignment['Mentor Email'])) == len(mentors[0]) , "Not all mentors have been alotted mentees!"
print("The assertion that all mentors have at least one mentee: Passed")

print('+' * 80)
temp = np.asarray(assignment.groupby(['Mentor Email', 'Mentor Name']).size())
assert (temp >= 3).all() , "Of all mentors, not all have been alotted >= 3 mentees!"
print("The assertion that all mentors have at least >= 3 mentees: Passed")

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
