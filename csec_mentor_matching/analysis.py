# NOTE: A lot of the analysis here involves heuristic values and is by no means 100% scientifically backed.

import numpy as np
import itertools as it
import random

MENTOR_INTEREST_FULL = 'Cryptography, Web Exploitation, Reverse Engineering, Binary Exploitation (Pwning), Digital Forensics, OSINT, Game Hacking, Blockchain Hacking, Bug Bounty, Pentesting, Malware Analysis'.split(', ')

MENTEE_INTEREST_FULL = 'Cryptography, Web Exploitation, Reverse Engineering, Binary Exploitation (Pwning), Digital Forensics, OSINT, Game Hacking, Blockchain, Bug Bounty, Pentesting, Malware Analysis'.split(', ')

def parse_interests(full, selected) :
    mask = 0
    ctr = 0
    for field in full :
        if field in selected :
            mask |= 1<<ctr
        ctr += 1
    return mask

def mentor_analysis(mentors) :
    # strip off the unnecessary fields
    mentors = mentors[1:]
    emails      = [i[1] for i in mentors]
    names       = [i[2] for i in mentors]
    interests   = list( map( lambda x: parse_interests(MENTOR_INTEREST_FULL, x[4]), mentors) )
    proficiency = list( map( lambda x: int(x[5]), mentors) )

    return (emails, names, interests, proficiency)

def mentee_analysis(mentees) :
    # strip off the unnecessary fields
    mentees = mentees[1:]
    emails      = [i[1] for i in mentees]
    names       = [i[2] for i in mentees]
    interests   = list( map( lambda x: parse_interests(MENTEE_INTEREST_FULL, x[8]), mentees) )

    return (emails, names, interests)

# the cost with number of matching subjects
dot_cost = np.exp(np.arange(12)/2.0)
dot_cost[0] += 1e+20

# cost with number of extra subjects that dont match with mentor
extra_cost = np.exp(np.arange(12)/2.0)


def count_bits(x) :
    t = 0
    while x > 0 :
        t += x & 1
        x >>= 1
    return t

def eval_cost(x) :
    tee, (tor, pro) = x
    U = int('1'*11, 2)

    # 0 common very high cost, less common low cost, more chances of matching.
    # lot of matches considered superflous.
    common    = dot_cost[count_bits(tee & tor)]

    # more the tee extra more the cost, less chances of matching.
    # giving the mentee something else to explore.
    tee_extra = extra_cost[count_bits(tee & (~tor & U))]

    # The more proficient the mentor the higher the cost,
    # lower the chances of getting that mentor.
    # More focussed the mentor on particular topics, the
    # lesser the chance of getting the mentor.
    pro_cost  = np.exp(100*(pro/10.0)* (1.0/count_bits(tor)))

    # random luck
    luck      = random.uniform(50.0, 275.0)

    return common + tee_extra + pro_cost + luck

def costs(multi, mentee_int, mentor_int, proficiency) :
    # the matcher is a minimum cost matching algorithm
    # Make the costs higher to decrease the possibility of matching.
    
    # add dummy candidates with very high weight
    mentee_int.extend([0] * (multi - len(mentee_int)))
    costs = list(it.product(mentee_int, list(zip(mentor_int, proficiency))))

    costs = list(map( eval_cost, costs))
    return costs

