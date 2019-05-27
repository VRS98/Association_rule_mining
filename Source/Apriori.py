import csv
import pandas as pd
from itertools import combinations

#Read data from CSV
data = pd.read_csv('../groceries.csv')

#Parameters
minsup=float(input("Enter Support-Threshold: "))
minsup=minsup*len(data)
minconf=float(input("Enter Confidence-Threshold: "))

#Add all data in a list of lists
items = []  
for i in range(0, len(data)):  
    items.append([str(data.values[i,j]) for j in range(0, len(data.values[0]))])

#Creating a list of dictionaries
count = [dict() for x in range(len(data.values[0])+1)]


#Count support for each individual items
s=[]
for i in items:
    for j in i:
        s.append(j)
for i in s:
    #If item is present in dictionary, increment its count by 1
    if i in count[1]:
        count[1][i] = count[1][i] + 1
    #If item is not present in dictionary, set its count to 1
    else:
        count[1][i] = 1


#Remove infrequent and empty items
for i in count[1].copy():
    if(count[1][i]<minsup):
        count[1].pop(i)
count[1].pop("nan")

#Generate frequent two item sets
slist=[list() for x in range(33)]
a=[]
a=combinations(count[1],2)
for j in a:
    slist[2].append(tuple(sorted(j)))
# slist[2]=list(combinations(count[1],2))
candidates=[]
for i in slist[2]:
    candidates.append(i)
for i in candidates:
    for k in items:
        f=0
        for l in i:
            if(k.__contains__(l)==0):
                f=1
                break
        if(f==0):
            if i in count[2]:
                count[2][i]=count[2][i]+1
            else:
                count[2][i]=1
for i in count[2].copy():
    if(count[2][i]<minsup):
        count[2].pop(i)

#Generate frequent itemsets of length z from z-1
def freq(z):
    for i in count[z-1]:
        for j in count[z-1]:
            a=set(i)
            b=set(j)
            #Generate z length itemsets from z-1 length frequent itemsets which have z-2 intersection elements
            if(len(a.intersection(b))==z-2):
                #Check if all subsets are in frequent z-1 itemsets, otherwise cannot be frequent
                t=list(combinations(sorted(a.union(b)), z-1))
                c=0
                for n in t:
                    for m in count[z-1]:
                        if((n)==m):
                            c=c+1
                if(c==z):
                    flag=0
                    for h in slist[z]:
                        if(sorted(list(a.union(b)))==sorted(h)):
                            flag=1
                    if(flag==0):
                        slist[z].append(tuple(sorted(list(a.union(b)))))
    #Calculate support
    candidates=[]
    for i in slist[z]:
        candidates.append(tuple(i))
    for i in candidates:
        for k in items:
            f=0
            for l in i:
                if(k.__contains__(l)==0):
                    f=1
                    break
            #If the complete item is present in the transaction, we increase it's support
            if(f==0):
                #If already present in dictionary then increment by 1
                if i in count[z]:
                    count[z][i]=count[z][i]+1
                #Else add it to dictionary
                else:
                    count[z][i]=1
    for i in count[z].copy():
        if(count[z][i]<minsup):
            count[z].pop(i)

#Call function to generate frequent itemssets
i=3
while(len(count[i-1])!=0):
    freq(i)
    i=i+1
q=i-2

#Function to extract single item set from a tuple
def value(a):
    a=str(a)
    a=a[:-2]
    a=a[2:]
    n=a[:-1]
    return n

#Find maximal and closed itemsets
maximal=[]
closed=[]
for i in range(1,q):
    for j in count[i]:
        fm=0
        fc=0
        for k in count[i+1]:
            a=set(list([j]))
            b=set(list(k))
            #Set is maximal if no immediate superset is frequent
            if(a.intersection(b)==a):
                fm=1
                #Set is closed if none of its immediate supersets have equal support
                if(count[i][j]==count[i+1][k]):
                    fc=1
        if(fm==0):
            maximal.append(j)
        if(fc==0):
            closed.append(j)
#All sets at the top of the tree are automatically maximal and closed
for i in count[q]:
    maximal.append(i)
    closed.append(i)

#Find Association Rules 
print("ASSOCIATION RULES")
c=0
ant=count.copy()
for i in range(q,0,-1):
    for j in ant[i]:
        for k in range(i-1,0,-1):
            s=list(combinations(list(j),k))      
            #Traverse through list of all combinations of antecedants
            for n in s:
                #Sorting to prevent duplicate itemsets 
                r=tuple(sorted(set(j).difference(set(n))))
                l=len(n)
                #Check if len(n)==1 to be able to extract key to search in the support dictionary. 
                if(l==1):
                    n=value(n)
                    l=1
                if(len(r)==1):
                    r2=value(r)
                if(n!=None):
                    #If rule's confidence is greater than minconfidence, then print the rule
                    if((ant[len(j)][j]/ant[l][n])>=minconf):
                    	#Rule is only significant if it is present in CLOSED, otherwise it is redundant
                        if(closed.__contains__((n))):
                            c=c+1
                            if(len(r)==1):
                                print(n,"(",ant[l][n],")","--->",r2,"(",ant[len(r)][r2],")", " confidence = ",(ant[len(j)][j]/ant[l][n]))
                            else:
                                print(n,"(",ant[l][n],")","--->",r,"(",ant[len(r)][r],")", " confidence = ",(ant[len(j)][j]/ant[l][n]))
