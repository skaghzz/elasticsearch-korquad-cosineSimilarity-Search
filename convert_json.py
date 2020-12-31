# -*- coding: utf-8 -*-
import json

'''
after
{"paragraph" : "~~~"}
{"paragraph" : "~~~"}
{"paragraph" : "~~~"}
'''

SOURCE_FILE = './KorQuAD_v1.0_train.json'
DEST_FILE = './KorQuAD_v1.0_train_convert.json'

with open(SOURCE_FILE) as json_file:
    korquad_json_data = json.load(json_file)
    data = korquad_json_data["data"]
    paragraphs_data = {}
    i = 0
    for d in data:
        title = d["title"]
        complete_paragraph = ""
        for p in d["paragraphs"]:
            complete_paragraph += p["context"]
            complete_paragraph += "\n"
        paragraphs_data.append({"title": title, "paragraph": complete_paragraph})


        i += 1
        if (i % 1000) == 0:
            print("processing ", i)
    print("total : ", i)
    with open(DEST_FILE, "w") as out:
        out.write(json.dumps(paragraphs_data))
        out.write("\n")
