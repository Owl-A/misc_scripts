#!/usr/bin/python3

### REFERENCES
#   https://pbpython.com/pandas-google-forms-part1.html

from __future__ import print_function

import auth
import analysis
import matcher

import pandas as pd

MENTEE_SPREADSHEET = '1byO5GRxBVTaDVXNR_JeykVWwA9LrirKhmjjn_8TIUXk'
MENTOR_SPREADSHEET = '1SMl0cjfrLgU6D2iYtiQwdl1O5kHTdGdyDqWdysdwTWg'

OUTPUT_FILE = "./matching.xlsx"

service = auth.get_service('../../client_secret.json')

mentees = auth.get_sheet_data(service, MENTEE_SPREADSHEET) 
mentors = auth.get_sheet_data(service, MENTOR_SPREADSHEET) 

# mentees should be a perfect multiple of mentor numbers
# this is necessitated by the matching API
mentors = analysis.mentor_analysis(mentors)
mentees = analysis.mentee_analysis(mentees)

multi = (int(len(mentees[0])/len(mentors[0])) + (1 if len(mentees[0]) % len(mentors[0]) else 0))*len(mentors[0])
costs = analysis.costs(multi, mentees[2], mentors[2], mentors[3])
assignment = matcher.match(multi, len(mentors[0]), costs)
#print(assignment)

assignment = list( zip(assignment[:len(mentees[0])], list(range(len(mentees[0])))) )

assignment = list(map( lambda x : (mentors[0][x[0]], mentors[1][x[0]], mentees[0][x[1]], mentees[1][x[1]]), assignment))
assignment = pd.DataFrame(assignment)
assignment.columns = ['Mentor Email', 'Mentor Name', 'Mentee Email', 'Mentee Name']

assignment = assignment.sort_values(['Mentor Email', 'Mentor Name'])
assignment.style.hide_index()

c = input("Please Enter your choice to save to {} [y/n]".format(OUTPUT_FILE))
while(c[0] != 'y' and c[0] != 'n'):
    print("Unrecognized Choice!!!")
    c = input("Please Enter your choice to save to {} [y/n]".format(OUTPUT_FILE))

if c[0] == 'y' :
    assignment.to_excel(OUTPUT_FILE, sheet_name="mentee allotment", index=False)
