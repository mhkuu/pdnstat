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

def check_relation(games): 
    result = list()
    for n, game1 in enumerate(games):
        for game2 in games[n+1:]:
            l = pdn_hamming(game1, game2)
            #if l < 10: 
            result.append([game1, game2, l])
    return result
    
def pdn_hamming(game1, game2):    
    string1 = game1.fen_string
    string2 = game2.fen_string
    return hamming_distance(string1, string2)
    
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