import json

with open("./data/musinsa_product_detail_상의_셔츠-블라우스.json" , "r" , encoding="utf-8") as f:
    data = json.load(f)

print(len(data) , "개")




