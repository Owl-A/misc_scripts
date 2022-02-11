#!/usr/bin/python3

import auth
import analysis
import matcher
from data import *

import pandas as pd
from functools import reduce
import numpy as np
from math import ceil
import sys

OUTPUT_FILE = "./updates.xlsx"

service = auth.get_service('../../client_secret.json')

matching = auth.get_sheet_data(service, MATCHING_FINAL, sheet_name='Mentor - Mentee Mapping') 
((m_mentor_email, m_mentee_count), m_matched_mentees) = analysis.matching_analysis(matching)

mentors_year = auth.get_sheet_data(service, MENTOR_YEAR_SPREADSHEET) 
mentees = auth.get_sheet_data(service, MENTEE_SPREADSHEET) 
mentors = auth.get_sheet_data(service, MENTOR_SPREADSHEET) 

mentors = analysis.mentor_analysis((mentors, mentors_year))
mentees = analysis.mentee_analysis(mentees)

um_mentors = [[mentors[0][i], mentors[1][i], mentors[2][i], mentors[3][i], mentors[4][i]] for i in range(len(mentors[0])) if mentors[0][i] not in m_mentor_email]
um_mentees = [[mentees[0][i], mentees[1][i], mentees[2][i], mentees[3][i]] for i in range(len(mentees[0])) if mentees[0][i] not in m_matched_mentees]

print("+" * 80)
print(pd.DataFrame(um_mentors))
print("+" * 80)
print(pd.DataFrame(um_mentees))

um_mentors = reduce(lambda x, y: [np.append(u[0], u[1]) for u in zip(x, y)], um_mentors, [[] for _ in um_mentors[0]])
um_mentees = reduce(lambda x, y: [np.append(u[0], u[1]) for u in zip(x, y)], um_mentees, [[] for _ in um_mentees[0]])

assignment = []

if len(um_mentors[0]) > 0 :
    current_max = max(m_mentee_count)
    current_num = max(set(m_mentee_count) - set([current_max]))

    multi = len(um_mentees[0]) 
    len_um_mentors = len(um_mentors[0])
    
    multi = ceil(multi/len_um_mentors)
    multi = min(multi, current_num) * len_um_mentors

    costs = analysis.costs(multi, um_mentees[2], um_mentees[3], um_mentors[2], um_mentors[3], um_mentors[4])
    temp = matcher.match(multi, len(um_mentors[0]), costs)
    temp = list( zip(temp[:len(um_mentees[0])], list(range(len(um_mentees[0])))) )

    assignment = list(map( lambda x : [um_mentors[0][x[0]], um_mentors[1][x[0]], um_mentors[4][x[0]], um_mentees[0][x[1]], um_mentees[1][x[1]], um_mentees[3][x[1]]], temp))
    assign_T = np.transpose(np.asarray(assignment))

    um_mentees = [[um_mentees[0][i], um_mentees[1][i], um_mentees[2][i], um_mentees[3][i]] for i in range(len(um_mentees[0])) if um_mentees[0][i] not in assign_T[0]]
    # At this point all mentors must be matched otherwise the next if will not trigger.

if len(um_mentees[0]) > 0 :
    tmp_mentors, tmp_counts = analysis.count_mentors([x[0] for x in assignment])
    m_mentor_email += tmp_mentors
    m_mentee_count += tmp_counts
#((m_mentor_email, m_mentee_count), m_matched_mentees) = analysis.matching_analysis(matching)

    tmp_mentors = [[]] * 5
    for i in range(len(m_mentor_email)) :
        t = mentors[0].index(m_mentor_email[i])
        tmp_mentors = list(map( lambda x : x[1] + ([mentors[x[0]][t]] * (current_max - m_mentee_count[i])) , list(enumerate(tmp_mentors))))
    um_mentees = reduce(lambda x, y: [np.append(u[0], u[1]) for u in zip(x, y)], um_mentees, [[] for _ in um_mentees[0]])
        
    mentors = tmp_mentors
    mentees = um_mentees
    multi = ceil(len(mentees[0])/len(mentors[0])) * len(mentors[0])
    costs = analysis.costs(multi, mentees[2], mentees[3], mentors[2], mentors[3], mentors[4])

    temp = matcher.match(multi, len(mentors[0]), costs)
    temp = list( zip(temp[:len(mentees[0])], list(range(len(mentees[0])))) )

    assignment += list(map(lambda x : (mentors[0][x[0]], mentors[1][x[0]], mentors[4][x[0]], mentees[0][x[1]], mentees[1][x[1]], mentees[3][x[1]]), temp))
    assignment = pd.DataFrame(assignment)

print('+' * 80, file=sys.stderr)
assignment.columns = ['Mentor Email', 'Mentor Name', 'Mentor Year', 'Mentee Email', 'Mentee Name', 'Mentee Year']
print("The assertion that Mentor Year >= Mentee Year: " + ("Failed" if np.all(assignment['Mentor Year'] >= assignment['Mentee Year'] ) else "Passed"))

assignment = assignment.sort_values(['Mentor Email', 'Mentor Name'])
assignment.style.hide_index()

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
