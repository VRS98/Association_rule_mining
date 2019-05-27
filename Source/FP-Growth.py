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
count[1].pop('nan')

#Storing transactions as lists without infrequent items
a=list(count[1])
item=[list() for i in range(len(data))]
c=0
for i in range(0,len(items)):
    for j in range(len(items[i])):
        if(a.__contains__(items[i][j])!=0):
            item[i].append(items[i][j])

#Function to sort list to support
def sort(a):
    for i in range(len(a)-1):
        for j in range(len(a)-i-1):
            if(count[1][a[j]]<count[1][a[j+1]]):
                a[j],a[j+1]=a[j+1],a[j]
        
#Call function to sort all transactions in descending order of their support
for i in range(0,len(data)):
    if(len(item[i])>1):
        sort(item[i])

#Tree class for FP-Tree
class tree:
    def __init__(self, name, sup, parent):
        self.name = name
        self.sup = sup
        self.nodeLink = None
        self.parent = parent
        self.children = []

#Function to check if the node is present is a child of the current node
def ispresent(node,name):
    f=-1
    for i in node.children:
        f=f+1
        if(i.name==name):
            return f
    return -1

#HeaderTable which stores the reference of last/first occurence of an item. Used as a linked list to generate candidate trees 
lastocc=count[1].copy()
for i in lastocc:
    lastocc[i]=None

#Function to create FP-tree
root = tree("root",-1,None)
z=0
for i in item:
    current=root
    for j in range(len(i)):
        if(ispresent(current,i[j])>=0):
            current=current.children[ispresent(current,i[j])]
            current.sup=current.sup+1
        else:
            child=tree(i[j],1,current)
            current.children.append(child)
            t=current
            current=current.children[ispresent(current,i[j])]
            current.parent=t
            if(lastocc[current.name]==None):
                lastocc[current.name]=current
            else:
                current.nodeLink=lastocc[current.name]
                lastocc[current.name]=current

#Function to extract single item set from a tuple
def value(a):
    a=str(a)
    a=a[:-2]
    a=a[2:]
    a=a[:-1]
    return a

#Function to get frequent itemsets with suffix 'node' and length n
def singlepath(node,n):
    c=0
    sup=node.sup
    path=[]
    pathname=[]
    current=node
    
    #Get the path from current node to root
    while(current.parent!=None):
        path.append(current)
        pathname.append(current.name)
        current=current.parent  
    path.remove(node)
    pathname.remove(node.name)
    candidatepath=[]
    temp_candidatepath=[]
    #Generate combinations of length n in the path
    a =(list(combinations(pathname,n)))
    for j in a:
        temp_candidatepath.append(tuple(sorted(j)))
    #Append the suffix 'node.name' to the above paths
    for j in temp_candidatepath:
        j=list(j)
        j.append(node.name)
        candidatepath.append(sorted(j))
    #Update counts of the generated itemsets
    for j in candidatepath:
        j=tuple(j)
        if j in count[n+1]:
            count[n+1][j]=count[n+1][j]+sup
        else:
            count[n+1][j]=sup
            
    #Iterating in the candidate tree recursively 
    if(node.nodeLink!=None):
        node=node.nodeLink
        singlepath(node,i)
    
#Check if itemset is frequent
def frequent(n):
    f=0
    for i in count[n]:
        if(count[n][i]>=minsup):
            f=1
    if(f==1):
        return 1
    else:
        return 0

#Call singlepath function for all frequent nodes
for i in range(1,len(data.values[0])+1): 
    if(frequent(i)==1):
        for j in lastocc:
            singlepath(lastocc[j],i)

#Remove infrequent itemsets
for z in range(len(data.values[0])+1):            
    for i in count[z].copy():
            if(count[z][i]<minsup):
                count[z].pop(i)

#Get 'q', the length of the longest itemset
i=2
while(len(count[i-1])!=0):
    i=i+1
q=i-2

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
                                print(n,"(",ant[l][n],")","--->",r2,"(",ant[len(r)][r2],")", " - conf(",(ant[len(j)][j]/ant[l][n]),")")
                            else:
                                print(n,"(",ant[l][n],")","--->",r,"(",ant[len(r)][r],")", " conf(",(ant[len(j)][j]/ant[l][n]),")")

