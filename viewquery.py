import requests
import re
import concurrent.futures as futures
import pandas as pd
import webbrowser
import numpy as np
from lxml import etree
from stqdm import stqdm
from datetime import date


def RepuScore_html(pub_id): # Get reputation score from html
    
	payload = f"https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid={pub_id}"
	# print(pub_id,"\n")
	page = requests.get(payload, timeout=(4,3))
	html_doc = page.text
	# print(re.findall(r"(<span class=\"value\">\d+</span>)", html_doc), pub_id)
	total = re.findall(r"<span class=\"value\">(\d+)</span>", html_doc)
	# print(html_doc)
	if len(total) > 0:
		# print(pub_id, total[0])
		return int(total[0])-1
	else:
		tree = etree.HTML(html_doc)
		message = tree.xpath('//*[@id="article-top-actions-bar"]/div/div/div[1]/span/text()')[0]
		# print(message)
		num_one = re.search(r"Found (\d+) result for", message).group(1)
		# print(num_one)
		if num_one == '1':
			return 0
		else:
			raise Exception("Can't find")

# print(RepuScore_html("36836348"))

def Breakline(string, num_char):

	chra = [*string]
	# print(chra)

	space_pos = [i for i in range(len(string)) if string[i] == " "]
	# print(space_pos)

	slices = []
	start = num_char
	for index, pos in enumerate(space_pos):
		if pos > start:
			slices.append(space_pos[index-1])
			start += num_char
	slices.insert(0, 0)
	slices.append(len(string))
	# print(slices)

	bucket = []
	for i in range(len(slices)-1):
		bucket.append(string[slices[i]:slices[i+1]].lstrip())
	return "\n".join(bucket)
# print(Breakline("Engineered Saccharomyces cerevisiae for lignocellulosic valorization: a review and perspectives on bioethanol production.", 70))

class pub_search():
	def __init__(self, query, val_get):
		self.query = query

		esum_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
		payload = {"db":"pubmed", "term":query,
								'retmax':val_get, 'sort':"pub_date", 'usehistory':"y"}
		while True:
			try:
				handle = requests.get(esum_url,params=payload, timeout=10)
				#print(handle.url)
			except:
				continue
			break
		records = handle.text
		#print(records)

		self.query_key = re.search(r'<QueryKey>(\d+)</QueryKey>', records).group(1)
		#print(query_key)
		self.wed_env = re.search(r'<WebEnv>(\w+)</WebEnv>', records).group(1)
		#print(wed_env)
		self.counts = re.search(r"<Count>(\d+)</Count>", records).group(1)
		#print(counts)
		self.pub_ids = re.findall(r"<Id>(\d+)</Id>", records)
		#print(pub_ids)

		esumma_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
		payload = {'db':'pubmed', 'query_key':f'{self.query_key}',
				 'WebEnv':f'{self.wed_env}', 'retmax':val_get}
		while True:
			try:
				handle = requests.get(esumma_url, params=payload, timeout=20)
				#print(handle.url)
			except:
				continue
			break

		records = handle.text
		#print(records)
		title_list = re.findall(r"<Item Name=\"Title\" Type=\"String\">(.*?)</Item>", records)
		# print(title_list)
		self.title = title_list

		self.years = re.findall(r"<Item Name=\"PubDate\" Type=\"Date\">(\d{4}).*?<\/Item>", records)
	# Summa("1.1.1.6")

	def reputation(self, val_get):

		bucket = self.pub_ids.copy()
		# print(bucket)
		reputation = []
		pbar = stqdm(total = min([int(val_get), int(self.counts)]))

		while len(bucket) > 0:
			
			with futures.ThreadPoolExecutor() as executor:
				future_to_ids = {executor.submit(RepuScore_html, ids): ids for ids in bucket}

				for future in futures.as_completed(future_to_ids):
					ids = future_to_ids[future]
					try:
						data = future.result()
						reputation.append((ids, data))
						bucket.remove(ids)
						pbar.update(1)
					except:
						continue
				# print(bucket)
		pbar.close()
		return reputation

def CountScore(score, year):
	current_year = date.today().year
	a = current_year - year
	if a == 0:
		return np.float64("nan")
	else:
		return round(score/(current_year-year),2)


def load_data(query, val_get):
	handle = pub_search(query, val_get)

	counts = handle.counts
	# print(f'Total of papers: {counts}\n')

	pub_id = handle.pub_ids
	# print(pub_id)

	titles = handle.title
	# print(titles)

	years = handle.years

	reputation = handle.reputation(val_get)
	# print(reputation)

	dy = pd.DataFrame(reputation, columns=["PID", "#Cited"])
	dx = pd.DataFrame(zip(pub_id, titles, years), columns=["PID", "Title", "Year"])

	df = pd.merge(dx, dy, how="outer", on="PID")


	df["Score"] = df.apply(lambda x: CountScore(pd.to_numeric(x["#Cited"]), pd.to_numeric(x["Year"])), axis=1)
	# print(df)
	# df = df.drop(columns=["#Cited", "Year"], axis=1)


	df = df.sort_values(by='Score', ascending=False)
	df = df.set_index('PID')
	return df, counts
# query = "(microorganism[Title/Abstract]) AND (Genetic Engineering[Title/Abstract])"

# query = '(((3.2.1.23[EC/RN Number]) AND (telomerase))) AND (DNA[Title/Abstract])'
# print(f"QUERY: {query}")
# val_get = 50

# df=load_data(query)
# df.to_csv('df.csv', index=False)

# st.dataframe(df)

