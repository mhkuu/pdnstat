import pdn
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
 
def by_year(games):  
    years = list()
    for game in games:
        if game.date != '?':
            years.append(game.date[:4])
            
    return Counter(years)

def by_event(games):  
    events = list()
    for game in games:
        events.append(game.event)
            
    return Counter(events).most_common() 

def by_author(games):  
    authors = list()
    for game in games:
        authors.append(game.white)
            
    return Counter(authors).most_common()  
    
def hamming_distance(s1, s2):
    #Return the Hamming distance between equal-length sequences
    if len(s1) != len(s2):
        raise ValueError("Undefined for sequences of unequal length")
    return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))
    
def plot(x): 
    labels, values = zip(*x)

    indexes = np.arange(len(labels))
    width = 1

    plt.bar(indexes, values, width)
    plt.xticks(indexes + width * 0.5, labels, rotation='vertical')
    plt.show()

#with open('motieven\\manoury.pdn') as fn: 
    #pdn_text = fn.read()
    #games = pdn.loads(pdn_text)
    
    #y = sorted(by_year(games).items())
    #for n in sorted(y):
    #    print n, y[n]
    #plot(y)
        
    #e = by_event(games)
    #for n in sorted(e):
        #print n, e[n]
    #plot(e)
        
    #a = by_author(games)
     
    #print check_relation(games)