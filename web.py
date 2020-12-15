from flask import Flask, request, render_template, abort, send_from_directory, send_file
from search import search, flytningsdata
import re, json

app = Flask(__name__)

@app.route("/static/<path:path>")
def resources(path):
	return send_from_directory("static", path)

with open("regioner.json") as f:
	regions = json.load(f)

def kommunekvadratmeterpris(num):
	#num = regions[kommune]

	years = {}

	with open("boliga_True.json", encoding='utf8') as f:
		data = json.load(f)
		for i in data:
			if not "grundstørrelse" in i:
				continue
			grund = int(i["grundstørrelse"])
			if (grund <= 0):
				continue
			if (i["postnummer"] == num):
				item = i["salg"][-1]
				year = item["date"]
				year = year[year.find(" ")+1:]
				if not year in years:
					years[year] = []
					
				years[year].append(int(item["pris"])/grund)

	for i in years.keys():
		years[i] = sum(years[i])/len(years[i])

	output = {
		"date": [],
		"prkv": []
	}

	for i in sorted([int(i) for i in list(years.keys())]):
		output["date"].append(str(i))
		output["prkv"].append(int(years[str(i)]))

	return output

def kommunelejepris(num):
	items = []
	with open("boligportal.json") as f:
		data = json.load(f)
		for i in data:
			if i["zipcode"] == num:
				items.append(i["monthlyPrice"])

	return sum(items)/len(items)

def flytningswow(kommune, years=10):
	saved = []

	output = {
		"date": [],
		"num": [0 for i in range(0,years)]
	}

	with open("fyn_flytningsdata.csv", encoding='utf8') as f:
		for line in f.readlines():
			data = line.strip().replace("\"","").split(";")

			if (data[0] == "Køn"):
				saved = data
				#print(saved)
				continue

			if (data[2] == kommune):
				for i in range(len(data)-1, len(data)-1-years, -1):
					amount = int(data[i].strip())
					year = saved[i]

					if (not year in output["date"]):
						output["date"].append(year)

					index = output["date"].index(year)
					#print(index, year, saved)

					#print(year,output["num"][index],amount)
					if (data[1] == "Tilflyttede"):
						output["num"][index] += amount
					else:
						output["num"][index] -= amount

	output["date"].reverse()
	output["num"].reverse()

	return output

@app.route("/bolig/<string:navn>")
def specific(navn):
	bolig = search(navn)

	oprettelsesdato = ""
	prisudvikling = 0

	solgt = {}

	for i in bolig["boliga"]["salg"]:
		if i["status"] == "Boligen blev sat til salg":
			oprettelsesdato = i["date"]

		result = re.search("(-?\d+)%", i["status"])
		if (result):
			prisudvikling = result.group(1)
		if i["status"].startswith("Solgt"):
			solgt["dato"] = i["date"]
			solgt["pris"] = i["pris"]

	return render_template("data.html",
		data={
			"name": navn,
			"udbudspris": bolig["boliga"]["pris"],
			"udbetaling": bolig["boliga"]["udbetaling"],
			"oprettelsesdato": oprettelsesdato,
			"boligareal": bolig["boliga"]["boligstørrelse"],
			"værelser": bolig["boliga"]["værelser"],
			"grundareal": bolig["boliga"]["grundstørrelse"],
			"kvadratmeterpris": "%.2f" % (int(bolig["boliga"]["pris"])/int(bolig["boliga"]["grundstørrelse"])),
			"byggeår": bolig["boliga"]["byggeår"],
			"energimærke": bolig["boliga"]["energimærke"],
			#"lejeudvikling": 0,
			"prisudvikling": prisudvikling,
			"befolkningstilvækst": "%.2f" % flytningsdata(bolig["boligejer"]["postnummer"]["navn"]),
			"img": bolig["boliga"]["img_url"],
			"raw": bolig,
			"solgt": solgt,
			"salgs_historik": {
				"date": json.dumps([str(i["date"]) for i in bolig["boliga"]["salg"]]),
				"pris": json.dumps([int(i["pris"]) for i in bolig["boliga"]["salg"]]),
				"prkv": json.dumps([int(i["pris"])/int(bolig["boliga"]["grundstørrelse"]) for i in bolig["boliga"]["salg"]])
			},
			"kommunekvmpris": kommunekvadratmeterpris(bolig["boligejer"]["postnummer"]["nr"]),
			#"kommunelejepris": kommunelejepris(bolig["boligejer"]["postnummer"]["nr"]),
			"kommuneflytning": flytningswow(bolig["boligejer"]["postnummer"]["navn"])
		}
	)

@app.route("/")
def first():
	all_data = []
	for j in [
		"Louisenlund 21, 5700 Svendborg",
		"Brydegårdsvej 10, 5700 Svendborg",
		"Dyrehavevej 82, 5800 Nyborg"
	]:
		bolig = search(j)

		oprettelsesdato = ""
		prisudvikling = 0
		for i in bolig["boliga"]["salg"]:
			if i["status"] == "Boligen blev sat til salg":
				oprettelsesdato = i["date"]

			result = re.search("(-?\d+)%", i["status"])
			if (result):
				prisudvikling = result.group(1)

		print(bolig["boligejer"]["postnummer"])
		all_data.append({
			"name": j,
			"udbudspris": bolig["boliga"]["pris"],
			"udbetaling": bolig["boliga"]["udbetaling"],
			"oprettelsesdato": oprettelsesdato,
			"boligareal": bolig["boliga"]["boligstørrelse"],
			"værelser": bolig["boliga"]["værelser"],
			"grundareal": bolig["boliga"]["grundstørrelse"],
			"byggeår": bolig["boliga"]["byggeår"],
			"energimærke": bolig["boliga"]["energimærke"],
			#"lejeudvikling": 0,
			"prisudvikling": prisudvikling,
			"befolkningstilvækst": "%.2f" % flytningsdata(bolig["boligejer"]["postnummer"]["navn"]),
			"img": bolig["boliga"]["img_url"]
		})

	return render_template("example.html", 
		all_data=all_data
	)

if __name__ == "__main__":
	app.run(host="0.0.0.0", threaded=True)
	#print(kommunekvadratmeterpris("Odense C"))
