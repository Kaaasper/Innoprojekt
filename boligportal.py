import requests, json

def search(search):
	result = None

	with requests.get("https://www.boligportal.dk/RAP/places?q={}".format(quote(search))) as r:
		data = json.loads(r.text)

		if (len(data["data"]["places"]) <= 0):
			return None

		result = data["data"]["places"][0]

	with requests.get("https://www.boligportal.dk/RAP/ads?placeIds[]={}".format(result["id"])) as r:
		data = json.loads(r.text)
		return data["data"]

def scanner():
	i = 0
	max = 1

	entries = []

	while (max > i):
		#max 200 records
		with requests.get("https://www.boligportal.dk/RAP/ads?startRecord={}&listViewResults=true&limitRecords=200&sort=paid".format(i)) as r:
			data = json.loads(r.text)
			max = data["data"]["properties"]["count"]
			print(i,max)

			for j in data["data"]["properties"]["collection"]:
				entries.append(j)

			i = i + len(data["data"]["properties"]["collection"])

	return entries

if __name__ == "__main__":
	with open("boligportal.json", "w") as f:
		json.dump(scanner(), f)
	#print(json.dumps(scanner(),indent="\t"))