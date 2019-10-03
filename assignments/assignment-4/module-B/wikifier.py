
import os, re, json, requests

def Wikify(text, KEY, threshold = 0.8):
    response = requests.get("".join(["http://www.wikifier.org/annotate-article?",
                                     "text=", text, "&lang=en", "&userKey=", KEY,
                                     "&pageRankSqThreshold=", str(threshold), 
                                     "&applyPageRankSqThreshold=", "true"]))

    return(response.json())

def get_wikification(filename, KEY):
    wikification_name = re.sub('.txt', '.json', filename)
    if os.path.exists('./data/wikifications/'+wikification_name):
        wikification = json.load(open('./data/wikifications/'+wikification_name, 'r'))
    else:
        wikification = Wikify(open("./data/texts/"+filename, "r").read(), KEY)
        with open('./data/wikifications/'+wikification_name, 'w') as f: 
            f.write(json.dumps(wikification))
    return(wikification)

def build_doc(wiki):
    if 'words' in wiki:
        doc = []
        for idx, word in enumerate(wiki['words']):
            doc.extend([wiki['spaces'][idx], word])
        else:
            doc.append(wiki['spaces'][-1])
        doc = "".join(doc)
    return(doc)

def get_links(wiki):
    links = []
    for annotation in wiki['annotations']:
        hyperlink = annotation['url']
        for support in annotation['support']:
            links.append([support["chFrom"], support["chTo"], hyperlink])
    return links

def embed_link(doc, link):
    show_text = doc[link[0]:link[1]+1]
    annotated_doc = (doc[:link[0]] + 
                     "<a href=\"" + link[2] + "\">" + show_text + "</a>" +
                     doc[link[1]+1:])
    return(annotated_doc)

def embed_links(wiki):
    ## 2
    doc = build_doc(wiki)
    ## 3
    links = get_links(wiki)
    ## 4
    links = sorted(links, key = lambda x: x[1], reverse = True)
    ## 5
    prev_from = float("Inf")
    for link in links:
        ## 6
        if link[1] < prev_from:
            doc = embed_link(doc, link)
        prev_from = link[0]
    ## 7
    return(doc)