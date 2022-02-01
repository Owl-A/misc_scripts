# NOTE: A lot of the analysis here involves heuristic values and is by no means 100% scientifically backed.

import numpy as np
import itertools as it
import random
import warnings
import z3

#warnings.filterwarnings('error')

MENTOR_YEAR_FULL = list(enumerate('1st BTech, 2nd BTech, 3rd BTech, 4th BTech, extension student, 5th DD, 1st MTech, 2nd MTech, 3rd MTech, PhD, Alumni'.split(', ')))

MENTEE_YEAR_FULL = list(enumerate('1st BTech/BSc/DD, 2nd BTech/BSc/DD, 3rd BTech/BSc/DD, 4th BTech/BSc/DD, extension student, 5th DD, 1st MTech/MSc, 2nd MTech/MSc, 3rd MTech/MSc, PhD'.split(', ')))


MENTOR_INTEREST_FULL = 'Cryptography, Web Exploitation, Reverse Engineering, Binary Exploitation (Pwning), Digital Forensics, OSINT, Game Hacking, Blockchain Hacking, Bug Bounty, Pentesting, Malware Analysis'.split(', ')

MENTEE_INTEREST_FULL = 'Cryptography, Web Exploitation, Reverse Engineering, Binary Exploitation (Pwning), Digital Forensics, OSINT, Game Hacking, Blockchain, Bug Bounty, Pentesting, Malware Analysis'.split(', ')

def arrange_mentees(mentees, len_mentor) :
    len_1 =(len(MENTOR_YEAR_FULL)) 
    temp = np.asarray(mentees[2]) * len_1 + np.asarray(mentees[3])
    keys, counts = np.unique(temp, return_counts=True)
    
    temp = list(zip(keys, counts))
    temp.sort(key=lambda x : x[1], reverse=True)
    keys = list(map(lambda x: x[0], temp))
    counts = list(map(lambda x: x[1], temp))
    
    temp = dict(zip(keys, counts))
    keys = list(map(lambda x: (int(x/len_1), x % len_1), keys))

    front = [[]] * 4
    back  = [[]] * 4
    mid   = [[]] * 4

    mentees = list(map(lambda x: np.asarray(x, dtype=type(x[0])), mentees))
    for i in keys :
        sat = np.argwhere(np.logical_and(mentees[2] == i[0], mentees[3] == i[1]))
        """
        print('[' * 40 + ']' * 40)
        print(f'sat    : {sat}')
        print(f'key    : {i}')
        print(f'counts : {temp[i[0]*len_1 + i[1]]}')
        print('[' * 40 + ']' * 40)
        input()
        #"""
        len_2 = int(len(sat)/2)

        front = [front[i] +      list(mentees[i][sat[:len_2]].flatten()) for i in range(len(mentees))]
        back  = [list((mentees[i][sat[-len_2:]] if len_2 > 0 else np.asarray([])).flatten())      + back[i] for i in range(len(mentees))]
        mid   = [list(mentees[i][sat[len_2:-len_2] if len_2 > 0 else sat[:]].flatten()) + mid[i]  for i in range(len(mentees))]
        """
        print('=' * 80)
        print(f'front : {len(front[0])}')
        print(f'mid   : {len(mid[0])}')
        print(f'back  : {len(back[0])}')
        print('=' * 80)
        input()
        #"""

    len_back = len(back[0])
    """
    print('=' * 80)
    print(f'front : {len(front[0])}')
    print(f'mid   : {len(mid[0])}')
    print(f'back  : {len(back[0])}')
    print('=' * 80)
    #"""
    cum = [front[i] + mid[i] + back[i] for i in range(len(mentees))]

    len_mentee = len(mentees[0])
    len_trunc_tee = int(len_mentee/len_mentor) * len_mentor
    
    """
    print(f'len mentee           : {len_mentee}')
    print(f'len truncated mentee : {len_trunc_tee}')

    print('=' * 80)
    #"""

    if len_mentee - len_trunc_tee > len_back :
        warnings.warn("Warning......................Suitable substitutes not found!, the results will be approximate")
    
    set_1 = list(map(lambda x: x[:len_trunc_tee], cum))
    set_2 = list(map(lambda x: x[len_trunc_tee:], cum))

    return (set_1, set_2)

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
    (tee_int, tee_year) , (tor_int, pro, tor_year) = x

    U = int('1'*11, 2)
    tor_int = int(tor_int)
    tee_int = int(tee_int)

    # match to anybody if the mentee is superfluous
    if count_bits(tee_int) == 0 :
        return 0.0

    # 0 common very high cost, less common low cost, more chances of matching.
    common    = dot_cost[count_bits(tee_int & tor_int)]

    # more the tee extra more the cost, less chances of matching.
    # giving the mentee something else to explore.
    tee_extra = extra_cost[count_bits(tee_int & (~tor_int & U))]

    # The more proficient the mentor the higher the cost,
    # lower the chances of getting that mentor.
    # More focussed the mentor on particular topics, the
    # lesser the chance of getting the mentor.
    pro_cost  = np.exp((1/pro) * (1/count_bits(tor_int)))

    # Chances of matching a mentor in lower year than you
    # should be negligible
    year_cost = 100 if tee_year > tor_year else (20 if tee_year == tor_year else 0)

    # random luck
    luck      = random.uniform(2.0, 10.0)

    """
    print("=" * 80)
    print(f'Common           : {common}')
    print(f'mentee extras    : {tee_extra}')
    print(f'proficiency cost : {pro_cost}')
    print(f'year cost        : {year_cost}')
    print(f'luck             : {luck}')
    input()
    print("=" * 80)
    #"""

    return np.log(common + tee_extra + pro_cost + year_cost + luck)

def costs(mentee_int, mentee_year, mentor_int, proficiency, mentor_year) :
    # the matcher is a minimum cost matching algorithm
    # Make the costs higher to decrease the possibility of matching.
    
    # add dummy candidates with very high weight
    # multi is number of mentees
#    mentee_int = np.append(mentee_int, np.asarray([0] * (multi - len(mentee_int))))
#    mentee_year = np.append(mentee_year, np.asarray([len(MENTEE_YEAR_FULL)+1] * (multi - len(mentee_year))))
    costs = list(it.product(list(zip(mentee_int, mentee_year)), list(zip(mentor_int, proficiency, mentor_year))))

    costs = list(map( eval_cost, costs))
    mat = []
    for i in range(len(mentor_int)):
        mat.append(list(map(lambda x : int(x), costs[i::len(mentor_int)])))
    return mat

def detect_duplicates(mentors, mentees) :
    for pt in (set(mentors[0]) & set(mentees[0])) :
        n = mentors[0].index(pt)
        print( mentors[1][n] + " <" + pt + "> Filled both mentor and mentee forms.")

# to encode matching as SAT; every mentee-mentor pair will have a cost and a boolean var to denote whether they are picked or not
# min cost matching = optimise cost of chosen pairs + choose only one edge per mentee
# other constraints to be added separately

# vars have mentor as first index and mentee as second
def mentor_count_constraint(tee_tor_vars, costs, min_cnt):
    l = []
    for i in range(len(tee_tor_vars)):
        l.append(z3.AtLeast(*tee_tor_vars[i], min_cnt))
    return z3.And(l)

def matching(optimiser, tee_tor_vars, costs):
    for j in range(len(tee_tor_vars[0])):
        optimiser.add(z3.simplify(z3.PbEq([(tee_tor_vars[i][j],1) for i in range(len(tee_tor_vars))], 1)))
    
    v = 0
    for i in range(len(tee_tor_vars)):
        for j in range(len(tee_tor_vars[0])):
            optimiser.add_soft(tee_tor_vars[i][j], costs[i][j])
#    optimiser.minimize(v)

    print(optimiser)

    return optimiser.check()
