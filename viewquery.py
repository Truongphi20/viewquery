import requests
import re
import concurrent.futures as futures
import pandas as pd
import webbrowser
import argparse
import numpy as np
from lxml import etree
from tqdm import tqdm

# Initialize parser
parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-q", "--query", help = 'query for Pubmed search')
parser.add_argument("-v",'--version', action='version', version='%(prog)s 1.0',help = 'show version')
parser.add_argument("-g", "--get",default = '100', help = 'Number of newest papers get.')


# Read arguments from command line
args = parser.parse_args()


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

def generate_html(dataframe: pd.DataFrame):
    # get the table HTML from the dataframe
    table_html = dataframe.to_html(table_id="table")
    # construct the complete HTML with jQuery Data tables
    # You can disable paging or enable y scrolling on lines 20 and 21 respectively
    html = f"""
    <html>
    <header>
        <link href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.min.css" rel="stylesheet">
    </header>
    <body>
    {table_html}
    <script src="https://code.jquery.com/jquery-3.6.0.slim.min.js" integrity="sha256-u7e5khyithlIdTpu22PHhENmPcRdFiHRjhAuHcs05RI=" crossorigin="anonymous"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready( function () {{
            $('#table').DataTable({{
                // paging: false,    
                // scrollY: 400,
            }});
        }});
    </script>
    </body>
    </html>
    """
    # return the html
    return html

class pub_search():
	def __init__(self, query):
		self.query = query

		esum_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
		payload = {"db":"pubmed", "term":query,
								'retmax':args.get, 'sort':"pub_date", 'usehistory':"y"}
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
		payload = {'db':'pubmed', 'query_key':f'{self.query_key}', 'WebEnv':f'{self.wed_env}'}
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

	# Summa("1.1.1.6")

	def reputation(self):

		bucket = self.pub_ids.copy()
		# print(bucket)
		reputation = []
		pbar = tqdm(total = min([int(args.get), int(self.counts)]))

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

# query = "(microorganism[Title/Abstract]) AND (Genetic Engineering[Title/Abstract])"
query = args.query
print(f"QUERY: {query}")

handle = pub_search(query)

counts = handle.counts
print(f'Total of papers: {counts}\n')

pub_id = handle.pub_ids
# print(pub_id)

titles = handle.title
# print(titles)

reputation = handle.reputation()
# print(reputation)

dy = pd.DataFrame(reputation, columns=["ID Pubmed", "#Cited"])
dx = pd.DataFrame(zip(pub_id, titles), columns=["ID Pubmed", "Title"])

df = pd.merge(dx, dy, how="outer", on="ID Pubmed")

df = df.sort_values(by='#Cited', ascending=False)
df = df.set_index('ID Pubmed')
# df["Title"] = df["Title"].apply(lambda x: Breakline(x, 70))
# print(df)

# with open('data.txt', 'w', encoding="utf-8") as writer:
# 	writer.write(f"QUERY: {query}\n")
# 	writer.write(f'Mount of papers: {counts}\n')
# 	writer.writelines(df.to_string())


if __name__ == "__main__":
    html = generate_html(df)
    # write the HTML content to an HTML file
    open("table.html", "w", encoding="utf-8").write(html)
    # open the new HTML file with the default browser
    webbrowser.open("data.html")
