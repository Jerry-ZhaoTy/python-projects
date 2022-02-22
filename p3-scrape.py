#!/usr/bin/env python
# coding: utf-8

# In[1]:


# project: p3
# submitter: tzhao86
# partner: none
# hours: 8


# In[2]:


import os, zipfile
from collections import deque

class GraphScraper:
    def __init__(self):
        self.visited = set()
        self.BFSorder = []
        self.DFSorder = []

    def go(self, node):
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        if node not in self.visited:
            self.visited.add(node)
            for child_node in self.go(node):
                self.dfs_search(child_node)

    def bfs_search(self, node):
        queue = deque([node])
        while len(queue) != 0:
            cur_node = queue.popleft()
            if cur_node not in self.visited:
                self.visited.add(cur_node)
                queue.extend(self.go(cur_node))        

class FileScraper(GraphScraper):    
    def go(self, node):
        file_name = node + ".txt"
        path = os.path.join("file_nodes", file_name)
        file = open(path, "r")
        lines = file.readlines()
        self.BFSorder.append(lines[2].strip().split(" ")[1])
        self.DFSorder.append(lines[3].strip().split(" ")[1])
        return lines[1].strip().split(" ")


# In[52]:


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time
import pandas as pd


class WebScraper(GraphScraper):
    # required
    def __init__(self, driver=None):
        super().__init__()
        self.driver = driver

    # these three can be done as groupwork
    def go(self, url):
        self.driver.get(url)
        bfs_btn = self.driver.find_element_by_id("BFS")
        dfs_btn = self.driver.find_element_by_id("DFS")
        bfs_btn.click()
        dfs_btn.click()
        self.BFSorder.append(bfs_btn.text)
        self.DFSorder.append(dfs_btn.text)
        links = self.driver.find_elements_by_tag_name("a")
        child_urls = []
        for link in links:
            child_urls.append(link.get_attribute("href"))
        return child_urls
        
    def dfs_pass(self, start_url):
        self.visited = set()
        self.DFSorder = []
        self.dfs_search(start_url)
        return "".join(self.DFSorder)

    def bfs_pass(self, start_url):
        self.visited = set()
        self.BFSorder = []
        self.bfs_search(start_url) 
        return "".join(self.BFSorder)
                
    # write the code for this one individually
    def protected_df(self, url, password):
        self.driver.get(url)
        btn = self.driver.find_element_by_id("btnclear")
        btn.click()
        for letter in str(password):
            btn = self.driver.find_element_by_id("btn" + letter)
            btn.click()
        btn = self.driver.find_element_by_id("attempt-button")
        btn.click()
        time.sleep(0.5)
        source = None
        updated_source = self.driver.page_source
        while source != updated_source:
            source = updated_source
            btn = self.driver.find_element_by_id("more-locations-button")
            btn.click()
            time.sleep(0.5)
            updated_source = self.driver.page_source
        time.sleep(0.5)
        page = BeautifulSoup(self.driver.page_source, "html.parser")
        trs = page.find("table").find_all("tr")
        header = [cell.get_text() for cell in trs[0].find_all("th")]
        rows = []
        for tr in trs[1:]:
            row = [cell.get_text() for cell in tr.find_all("td")]
            rows.append(row)
        df = pd.DataFrame(rows, columns = header)
        return df


# In[ ]:




