from scipy import stats
from search import flytningsdata
import json, requests

def kvadratmeterpris(postnummer):
	return 1

with open("boligportal.json") as f:
	boligportal = json.load(f)

def gennemsnitsleje(postnummer):
	x = []
	y = []

	for i in boligportal:
		if int(i["zipcode"]) == postnummer:
			x.append(i["sizeM2"])
			y.append(i["monthlyPrice"])

	if len(x) <= 0 or len(y) <= 0:
		return lambda x: x*-1

	slope, intercept, r, p, std_err = stats.linregress(x, y)

	#print(postnummer)

	def myfunc(x):
		return slope * x + intercept
	
	return myfunc

kommune = {}

#En float som 1.01 efter om der er et positivt antal tilflyttende i kommunen eller ej.
def flytningssats(postnummer):
	postnummer = str(postnummer)

	if not postnummer in kommune:
		with requests.get("https://dawa.aws.dk/postnumre/{}".format(postnummer)) as r:
			data = json.loads(r.text)
			kommune[postnummer] = data["kommuner"][0]["navn"]

	with open("regioner.json", encoding="utf8") as f:
		data = json.load(f)
		data = {v: k for k, v in data.items()}
		#print(data)
		#print(postnummer,kommune[postnummer])
		#print(flytningsdata(kommune[postnummer]))
		try:
			result = flytningsdata(kommune[postnummer])*10
			#print(kommune[postnummer],result)
			return result
		except:
			print("Failed for",postnummer,kommune[postnummer])
			return -1

def overskud(entry):
	pris = int(entry["pris"])
	udbetaling = int(entry["udbetaling"])
	ejerudgift = int(entry["ejerudgift"])
	brutto = float(entry["brutto"])
	kvpris = pris/int(entry["grundstørrelse"])
	postnummer = int(entry["postnummer"])
	gennemsnit_kvpris = kvadratmeterpris(postnummer)

	indtægt = gennemsnitsleje(postnummer)(int(entry["grundstørrelse"]))
	udgifter = ejerudgift+brutto

	overskud = indtægt - udgifter

	timetoreturn = ((pris - udbetaling)*1.01)/overskud

	return (timetoreturn * kvpris/gennemsnit_kvpris)*flytningssats(postnummer)

def judge(max):
	data = None

	with open("boliga_new.json", encoding="utf8") as f:
		data = json.load(f)
		for i in data:
			if not "værelser" in i or int(i["værelser"]) <= 0:
				continue
			if int(i["pris"]) > max:
				continue
			if i["grundstørrelse"] == "0":
				continue

			i["vurdering"] = overskud(i)
	
	data.sort(key=lambda x: x["vurdering"] if "vurdering" in x else -9999999999)

	return json.dumps(data[-5:], indent="\t")

if __name__ == "__main__":
	print(judge(4000000))