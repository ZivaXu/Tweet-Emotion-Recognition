import requests, json
api_key = "e1pNeA7xCEAKhZoFF7w7RvArWVq0EOVvMxAJgA88UVc"
text = "{}".format(['1', 'slkjklsd',"sdsd","sdsfs","sdsf"])
output = requests.post("https://apis.paralleldots.com/v5/emotion_batch",
                       data={"api_key": api_key, "text": text}).json()
print(output)
