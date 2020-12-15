import requests, json
from urllib.parse import quote
from boliga import scan as boliga_scan
from boligportal import search as boligportal_search

def boligejer(search):
	result = None

	with requests.get("https://dawa.aws.dk/adgangsadresser/autocomplete?q={}".format(quote(search.replace(" ", "+")))) as r:
		data = json.loads(r.text) #The curse of javascript's ghost lives on
		#print(json.dumps(data,indent="\t"))
		
		if (len(data) <= 0):
			return None

		result = data[0]

	with requests.get(result["adgangsadresse"]["href"]) as r:
		data = json.loads(r.text)
		return data

def tinglysning(search):
	result = None

	print(quote(search))

	print(requests.get("https://www.tinglysning.dk/rest/soeg/save/new_phone_who_dis").text)
	with requests.get("https://www.tinglysning.dk/rest/soeg/{}?token=new_phone_who_dis".format(quote(search))) as r:
		print(r.text)
		data = json.loads(r.text)
		if data["items"] == None:
			return None
		result = data

	with requests.get("https://www.tinglysning.dk/m/ejendom/{}/new_phone_who_dis".format(result)) as r:
		data = json.loads(r.text)
		return data

def flytningsdata(kommune, years=5):
	gain = 0
	loss = 0
	print(kommune)

	with open("fyn_flytningsdata.csv") as f:
		for line in f.readlines():
			data = line.strip().replace("\"","").split(";")
			if (data[0] == "Køn"):
				continue

			if (data[2] == kommune):
				for i in range(len(data)-1, len(data)-1-years, -1):
					amount = int(data[i].strip())
					if (data[1] == "Tilflyttede"):
						gain += amount
					else:
						loss += amount

	return (gain/loss)-1

def gennemsnitsalder(kommune):
	with open("fyn_gennemsnitsalder.csv") as f:
		for line in f.readlines():
			data = line.strip().replace("\"","").split(";")
			if (data[0] != "I alt"):
				continue
			if (data[1] != kommune):
				continue

			return data[-1]

def gennemsnitskvadratmeterpris(kommune):
	pass
def gennemsnitsudlegningspris(kommune):
	pass

def arbejdssteder():
	pass #ERHV2_all.csv

def boliga(search):
	with requests.get("https://api.boliga.dk/api/v2/location/suggestions?q={}&queryType=0&areaLimit=10&addressLimit=10".format(quote(search))) as r:
		data = json.loads(r.text)
		if (len(data["boligSuggestions"]) <= 0):
			return None
		return boliga_scan("https://www.boliga.dk/bolig/{}".format(data["boligSuggestions"][0]["id"]))

def search(search):
	data = {}
	data["boligejer"] = boligejer(search)
	#data["boligportal"] = boligportal(search)
	data["boliga"] = boliga(search)
	print(data)
	kommune = data["boligejer"]["postnummer"]["navn"]
	#kommune = "Assens"
	data["kommune_data"] = {
		"tilflytning": flytningsdata(kommune),
		"gennemsnitsalder": gennemsnitsalder(kommune)
	}

	#print(json.dumps(data,indent="\t"))
	return data
	
if __name__ == "__main__":
	search("Ny Adelgade 1, 5610 Assens")