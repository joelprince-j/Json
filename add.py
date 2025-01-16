import json

with open("ex5.json", "r") as file:
    ex5 = json.load(file)

for donut in ex5:
    if donut["name"] == "Old Fashioned":
        donut["batters"]["batter"].append({"id": "1005", "type": "Tea"})
        break

with open("ex5_updated.json", "w") as file:
    json.dump(ex5, file, indent=4)

print("Done")