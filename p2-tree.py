#!/usr/bin/env python
# coding: utf-8

# In[1]:


# project: p2
# submitter: tzhao86
# partner: none
# hours: 12


# In[2]:


import csv
import json
from zipfile import ZipFile
from io import TextIOWrapper
import pandas as pd


# In[3]:


class ZippedCSVReader:
    def __init__(self, zipFile):
        self.zipFile = zipFile
        self.paths = []
        with ZipFile(zipFile) as zf:
            for file in zf.namelist():
                self.paths.append(file)
            
    def rows(self, givenFile = None):
        with ZipFile(self.zipFile) as zf:
            if givenFile != None:
                with zf.open(givenFile, "r") as f:
                    tio = TextIOWrapper(f)
                    for data in csv.DictReader(tio):
                        yield data
            else:
                all_csv_data = []
                for file in self.paths:
                    with zf.open(file, "r") as f:
                        tio = TextIOWrapper(f)
                        for data in csv.DictReader(tio):
                            yield data


# In[4]:


class Loan:
    def __init__(self, amount, purpose, race, sex, income, decision):
        self.amount = amount
        self.purpose = purpose
        self.race = race
        self.sex = sex
        if income == '': self.income = 0
        else: self.income = income
        self.decision = decision

    def __repr__(self):
        return f"Loan({self.amount}, '{self.purpose}', '{self.race}', '{self.sex}', {self.income}, '{self.decision}')"

    def __getitem__(self, lookup):
        if lookup == 'amount':
            return self.amount
        if lookup == 'purpose':
            return self.purpose
        if lookup == 'race':
            return self.race
        if lookup == 'sex':
            return self.sex
        if lookup == 'income':
            return self.income
        if lookup == 'decision':
            return self.decision
        if (lookup == self.amount or lookup == self.purpose or lookup == self.race 
            or lookup == self.sex or lookup == self.income or lookup == self.decision):
            return 1
        else:
            return 0


# In[5]:


class Bank:
    def __init__(self, name, reader):
        self.name = name
        self.reader = reader
    
    def loans(self):
        for row in self.reader.rows():
            if row['agency_abbr'] != self.name and self.name != None:
                continue
            if row['action_taken'] == '1':
                decision = "approve"
            else:
                decision = "deny"
            if row['loan_amount_000s'] == '':
                amount = 0
            else:
                amount = row['loan_amount_000s']
            yield Loan(amount, row['loan_purpose_name'], row['applicant_race_name_1'],
                       row['applicant_sex_name'], row['applicant_income_000s'], decision)      


# In[6]:


def get_bank_names(reader):
    bank_names = set()
    for row in reader.rows():
        bank_names.add(row['agency_abbr'])
    return sorted(list(bank_names))


# In[7]:


class SimplePredictor():
    def __init__(self):
        self.approved = 0
        self.denied = 0

    def predict(self, loan):
        if loan.purpose == "Refinancing":
            self.approved += 1
            return True
        else:
            self.denied += 1
            return False
        
    def get_approved(self):
        return self.approved

    def get_denied(self):
        return self.denied  


# In[8]:


class Node(SimplePredictor):
    def __init__(self, field, threshold, left, right):
        super().__init__()
        self.field = field
        self.threshold = threshold
        self.left = left
        self.right = right

    def dump(self, indent=0):
        if self.field == "class":
            line = "class=" + str(self.threshold)
        else:
            line = self.field + " <= " + str(self.threshold)
        print("  "*indent+line)
        if self.left != None:
            self.left.dump(indent+1)
        if self.right != None:
            self.right.dump(indent+1)
    
    def node_count(self):
        count = 1
        if self.left != None:
            count += self.left.node_count()
        if self.right != None:
            count += self.right.node_count()
        return count
        
    def predict(self, loan):
        result = self.predict_helper(loan)
        if result:
            self.approved += 1
        else:
            self.denied += 1
        return result
    
    def predict_helper(self, loan):
        if self.field == 'class':
            if self.threshold == '1': 
                return True
            else:
                return False
        if float(loan[self.field]) > float(self.threshold):
            return self.right.predict(loan)
        else:
            return self.left.predict(loan)


# In[9]:


def build_tree(rows, root_idx=0):
    row = rows[root_idx]  
    if int(row['left']) != -1:
        left = build_tree(rows, int(row['left']))
    else:
        left = None
    if int(row['right']) != -1:
        right = build_tree(rows, int(row['right']))
    else:
        right = None
    curNode = Node(row['field'], row['threshold'], left, right) 
    return curNode


# In[10]:


def bias_test(bank, predictor, field, value_override):
    loans = list(bank.loans())
    changed = 0
    for loan in loans:
        prev = predictor.predict(loan)
        if field == "race": loan.race = value_override
        else: loan.sex = value_override
        if prev != predictor.predict(loan):
            changed += 1
    return changed / len(loans)

