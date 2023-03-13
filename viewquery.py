import requests
import re
import concurrent.futures as futures
import pandas as pd
import webbrowser
import argparse


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
	page = requests.get(payload, timeout=10)
	html_doc = page.text
	total = re.findall(r"<span class=\"value\">(\d+)</span>", html_doc)
	if len(total) > 0:
		# print(pub_id, total[0])
		return int(total[0])
	else:
		return 0
# print(RepuScore_html("17459724"))

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
				handle = requests.get(esum_url,params=payload, timeout=20)
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

		future_list = []
		with futures.ThreadPoolExecutor() as executor:
			for ids in self.pub_ids:
				future_list.append(executor.submit(RepuScore_html, ids))
		
		repu = []
		for future in future_list:
			while True:
				try:
					rs = future.result()
					# print(rs)
					repu.append(rs)
				except:
					continue
				break

		return repu 

# query = "(microorganism[Title/Abstract]) AND (Genetic Engineering[Title/Abstract])"
query = args.query

handle = pub_search(query)

counts = handle.counts
pub_id = handle.pub_ids
# print(pub_id)

titles = handle.title
# print(titles)

reputation = handle.reputation()
# print(reputation)

df = pd.DataFrame(zip(pub_id, titles, reputation), columns=["ID Pubmed", "Title", "#Cited"])
df = df.sort_values(by='#Cited', ascending=False)
df = df.set_index('ID Pubmed')
# df["Title"] = df["Title"].apply(lambda x: Breakline(x, 70))
print(df)

# with open('data.txt', 'w', encoding="utf-8") as writer:
# 	writer.write(f"QUERY: {query}\n")
# 	writer.write(f'Mount of papers: {counts}\n')
# 	writer.writelines(df.to_string())


if __name__ == "__main__":
    html = generate_html(df)
    # write the HTML content to an HTML file
    open("data.html", "w", encoding="utf-8").write(html)
    # open the new HTML file with the default browser
    webbrowser.open("data.html")
