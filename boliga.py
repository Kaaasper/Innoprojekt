import requests, re, json, os
from bs4 import BeautifulSoup

def scan(url):
	with requests.get(url) as r:
		soup = BeautifulSoup(r.text, "html.parser")
		with open("fuck.html","w") as f:
			f.write(r.text)

		data = {}

		data["type"] = soup.find("span", {"class": "d-none d-sm-inline-block"}).getText().strip()

		address = soup.find("span", {"class": "h-md-4 h5 text-muted"}).getText().strip()

		split = address.rfind(", ")
		data["address"] = address[:split]
		post_code = address[split+2:]
		data["postnummer"] = post_code[:post_code.find(" ")]
		#data["img_url"] = soup.find("img", {"class": "rounded shadow"})["src"]
		data["img_url"] = soup.find("meta", {"property": "og:image"})["content"]

		data["pris"] = soup.find("span", {"class": "h-md-2 h4 font-weight-bold m-0 text-nowrap"}).getText().strip().replace("\xa0kr.", "").replace(".", "")
		data["udbetaling"] = soup.find("span", {"class": "d-block text-right h-md-4 h5 text-muted"}).getText().replace("Udbetaling ", "").replace("\xa0kr.", "").replace(".","")
		#I kr.

		for i in soup.find("div", {"class": "row p-0 m-0 no-gutters mb-3"}):
			text = None
			try:
				text = i.getText()
			except AttributeError:
				continue

			m = re.search("Boligstørrelse  (\d+) m", text)
			if (m):
				data["boligstørrelse"] = m.group(1)
				#I m^2

			m = re.search("Grundstørrelse  (\d+)", text)
			if (m):
				data["grundstørrelse"] = m.group(1)
				#I m^2

			m = re.search("Værelser  (\d+)", text)
			if (m):
				data["værelser"] = m.group(1)

			m = re.search("Byggeår  (\d+)", text)
			if (m):
				data["byggeår"] = m.group(1)

			m = re.search("Energimærke  (\w+)", text)
			if (m):
				data["energimærke"] = m.group(1)

			m = re.search("Ejerudgift  (\d+) kr. / md.", text)
			if (m):
				data["ejerudgift"] = m.group(1)
				#I m^2

			m = re.search("Kælderstørrelse  (\d+)", text)
			if (m):
				data["kælderstørrelse"] = m.group(1)
				#I m^2

		data["salg"] = []
		for i in soup.find("div", {"class": "col-lg-8 app-print-full-width d-print-block ng-star-inserted"}).find("div").find("div").find("app-real-estate-property-info-history").find("div",{"class":"card-body p-0"}).find("table").find_all("tbody"):
			for j in i.find_all("tr"):
				if ("Tidslinje" in str(j)):
					continue

				date = j.find("span",{"class": "timeline"}).getText().strip()
				status = j.find("div",{"class": "mr-0 mr-sm-2"}).getText().strip()
				price = j.find("td",{"class": "text-right price-col"}).getText().replace("\u00a0kr. ", "").replace(".","")

				"""
				Known statuses:
				Boligen blev sat til salg
				Boligen blev taget af markedet
				Solgt, alm. frit salg
				Solgt, auktion
				"""

				data["salg"].append({
					"date": date,
					"status": status, #TODO: What types of events are there?
					"pris": price
				})

		data["salg"].reverse()

		return data

def scanner(solgte=False):

	#TODO: Executor
	with open("boliga_{}.json".format(solgte), "w") as f:
		f.write("[\n")

		page = 1
		pages = 2 #Arbitrary number
		while (page < pages):
			with requests.get("https://www.boliga.dk/resultat?searchTab=0&area=7&page={}&searchArchive={}&sort=daysForSale-a".format(page, "true" if solgte else "false")) as r:
				print(page)

				soup = BeautifulSoup(r.text, "html.parser")
				if (page == 1):
					pages = int(soup.find("div", {"class": "jump-to-page"}).find("a").getText())

				for a in soup.find_all('a', href=True):
					url = a["href"]
					if (url.startswith("/bolig/")):
						print(url)
						try:
							#Allows us to dump to ram directly
							#TODO: Encapsulate this solution instead
							f.write(json.dumps(scan("https://www.boliga.dk" + url)) + ",\n")
						except Exception as e:
							print(e)

			page = page + 1
			#Dump ram to file
			f.flush()

		f.write("{}\n") #HOTFIX
		f.write("]")

if __name__ == "__main__":
	#result = scan("https://www.boliga.dk/bolig/1728694/limfjordsgade_5_7790_thyholm")
	#result = scan("https://www.boliga.dk/bolig/1726498/bygaden_5_3660_stenloese")
	#print(json.dumps(result, indent="\t"))

	scanner()
	#scanner(solgte=True)

#Cirka 1m pr side
#913m = 15+ timer

"""
Ejendoms data
	Addresse, pris, energimærke, (bolig/grund)størrelse, byggeår, type
	Prisudvikling på denne type bolig
Ejendoms historik
	Prisudvikling
	Stand
Nabolags/vej data
	Prisudvikling
	Vej data
	Lokal område
Kommune data
	Prisudvikling
Kort over markedsværdi i områder
Markets udvikling vs ejendoms værdi
"""