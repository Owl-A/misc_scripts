# NOTE: A lot of the analysis here involves heuristic values and is by no means 100% scientifically backed.

import numpy as np
import itertools as it
import random
import warnings

gap = 10
HIGH_CAP = -1
LOW_CAP = -1
multiples = 2

def get_optimal_dummies(len_mentees, len_mentors) :
    mn = (np.lcm(len_mentees, len_mentors), 0, 0)
    for i in range(gap) :
        for j in range(gap) :
            lcm = np.lcm(len_mentees + i, len_mentors + j)
            
            # - get an lcm that is lowest AND

            ### The next two are later assumptions!
            # - make sure every mentee is matched with at least one legitimate mentor, 
            #   in other words, `number of mentors per mentee` > `number of superflous mentors` AND 
            # - every mentor gets at least LOW_CAP mentees,
            #   in other words, `every mentor gets replecated more than `

            if mn[0] > lcm :
                mn = (lcm, i, j) 

    return mn

warnings.filterwarnings('error')

MENTOR_YEAR_FULL = list(enumerate('1st BTech, 2nd BTech, 3rd BTech, 4th BTech, extension student, 5th DD, 1st MTech, 2nd MTech, 3rd MTech, PhD, Alumni'.split(', ')))

MENTEE_YEAR_FULL = list(enumerate('1st BTech/BSc/DD, 2nd BTech/BSc/DD, 3rd BTech/BSc/DD, 4th BTech/BSc/DD, extension student, 5th DD, 1st MTech/MSc, 2nd MTech/MSc, 3rd MTech/MSc, PhD'.split(', ')))


MENTOR_INTEREST_FULL = 'Cryptography, Web Exploitation, Reverse Engineering, Binary Exploitation (Pwning), Digital Forensics, OSINT, Game Hacking, Blockchain Hacking, Bug Bounty, Pentesting, Malware Analysis'.split(', ')

MENTEE_INTEREST_FULL = 'Cryptography, Web Exploitation, Reverse Engineering, Binary Exploitation (Pwning), Digital Forensics, OSINT, Game Hacking, Blockchain, Bug Bounty, Pentesting, Malware Analysis'.split(', ')

def set_caps(len_mentees, len_mentors, low_cap) :
    global HIGH_CAP, LOW_CAP
    HIGH_CAP = np.ceil(len_mentees/len_mentors)
    LOW_CAP = low_cap
    return HIGH_CAP

def parse_interests(full, selected) :
    mask = 0
    ctr = 0
    for field in full :
        if field in selected :
            mask |= 1<<ctr
        ctr += 1
    return mask

def parse_years(full, selected) :
    for i in full :
        if i[1] in selected :
            return i[0]
    return len(full) 

def mentor_analysis(mentors_data) :
    # strip off the unnecessary fields
    mentors, mentors_year = mentors_data
    mentors = mentors[1:]

    emails      = [i[3].strip() for i in mentors]
    mask        = [ emails.index(x[1]) == x[0] for x in enumerate(emails)]
    emails      = list( np.asarray(emails)[mask] )

    names       = list( np.asarray([i[2].strip() for i in mentors])[mask] )
    interests   = list( np.asarray(list( map( lambda x: parse_interests(MENTOR_INTEREST_FULL, x[4]), mentors) ) )[mask] )
    proficiency = list( np.asarray(list( map( lambda x: int(x[5]), mentors) ))[mask] )

    years = []
    for i in emails :
        temp = []
        for j in mentors_year :
            if i == j[1].strip() or i == j[3].strip() :
                temp += [j[6]]
        if len(temp) > 1:
            print(str(j) + " Probably filled the form twice." )
        elif len(temp) == 0:
            print( names[emails.index(i)]+ " <"+ i + "> Did not fill the form yet.")
            # people who did'nt fill the form will be alloted 1st year BTech status
            # and will be unable to take any mentees other than 1st year BTech
            years += [0]
            continue
        years += [parse_years(MENTOR_YEAR_FULL, temp[0])]

    return (emails, names, interests, proficiency, years)

def mentee_analysis(mentees) :
    # strip off the unnecessary fields
    mentees = mentees[1:]
    mentees = list( filter( lambda x : len(x) > 0, mentees ) )
    emails      = [i[1].strip() for i in mentees]
    names       = [i[2].strip() for i in mentees]
    interests   = list( map( lambda x: parse_interests(MENTEE_INTEREST_FULL, x[8]), mentees) )
    years       = list( map( lambda x: parse_years(MENTEE_YEAR_FULL, x[6]), mentees))

    return (emails, names, interests, years)

# the cost with number of matching subjects
dot_cost = np.exp(np.arange(12)/3.0)[::-1]

# cost with number of extra subjects that dont match with mentor
extra_cost = np.exp(np.arange(12)/3.0)


def count_bits(x) :
    t = 0
    while x > 0 :
        t += x & 1
        x >>= 1
    return t

def eval_cost(x) :
    # remember more the cost, less chances of matching
    (tee_int, tee_year, tee_spoof) , (tor_int, pro, tor_year) = x
    # superflous mentee and mentors, very preferable to match!
    if tee_spoof < 0 and pro < 0 :
        return 0.0

    U = int('1'*11, 2)
    tor_int = int(tor_int)

    # 0 common very high cost, less common low cost, more chances of matching.
    # lot of matches considered superflous.
    x = count_bits(tee_int & tor_int)
    common    = dot_cost[x]

    # more the tee extra more the cost, less chances of matching.
    # giving the mentee something else to explore.
    if tee_spoof < 0 :
        tee_extra = extra_cost[count_bits(U)]
    else:
        tee_extra = extra_cost[count_bits(tee_int & (~tor_int & U))]

    # The more proficient the mentor the higher the cost,
    # lower the chances of getting that mentor.
    # More focussed the mentor on particular topics, the
    # lesser the chance of getting the mentor.
    if pro < 0 :
        pro_cost = np.exp(2)
    else:
        pro_cost  = np.exp(pro* (0.40/count_bits(tor_int)))

    # Chances of matching a mentor in lower year than you
    # should be negligible
    year_cost = 100.0 if tee_year > tor_year else 0

    # random luck
    luck      = random.uniform(3.0, 9.0)

    """
    print()
    print(f"common {common}")
    print(f"tee_extra {tee_extra}")
    print(f"pro_cost {pro_cost}")
    print(f"year_cost {year_cost}")
    print(f"luck {luck}")
    #"""
    return np.log(common + tee_extra + pro_cost + year_cost + luck)

def costs(multi, mentee_s, mentor_s, mentee_int, mentee_year, mentor_int, proficiency, mentor_year) :
    # the matcher is a minimum cost matching algorithm
    # Make the costs higher to decrease the possibility of matching.
    
    # add dummy candidates with very high weight
    times_mentee = int(multi / ( mentee_s + len(mentee_int))) * multiples

    mentee_spoof = (([0] * len(mentee_int)) +  [-1] * (mentee_s)) * times_mentee
    mentee_int   = (mentee_int  +  [0] * (mentee_s)) * times_mentee
    mentee_year  = (mentee_year +  [len(MENTOR_YEAR_FULL) + 1] * (mentee_s)) * times_mentee

    times_mentor = int(multi / ( mentor_s + len(mentor_int))) * multiples

    mentor_int  = (mentor_int  + ([0]  * (mentor_s))) * times_mentor 
    mentor_year = (mentor_year + ([-1] * (mentor_s))) * times_mentor
    proficiency = (proficiency + ([-1] * (mentor_s))) * times_mentor
    print("length of mentor after extension : " + str(len(mentor_int)))

    costs = list(it.product(list(zip(mentee_int, mentee_year, mentee_spoof)), list(zip(mentor_int, proficiency, mentor_year))))

    costs = list(map( eval_cost, costs))
    return (multi* multiples), costs

def detect_duplicates(mentors, mentees) :
    for pt in (set(mentors[0]) & set(mentees[0])) :
        n = mentors[0].index(pt)
        print( mentors[1][n] + " <" + pt + "> Filled both mentor and mentee forms.")
