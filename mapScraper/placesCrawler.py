from requests_html import HTMLSession
from urllib.parse import unquote

def search(query):
    result = []
    PAGINATION = 0

    while True:
        session = HTMLSession()
        url = 'https://www.google.com/localservices/prolist?hl=en&ssta=1&q='+query+'&oq=gimnasios%20utrera%20espa%C3%B1a&src=2&lci='+str(PAGINATION)
        r = session.get(url)

        r.html.render(timeout=20)

        title = r.html.find('.xYjf2e')
        details = r.html.find('.I9iumb:nth-child(2)')
        rating = r.html.find('.Ty81De')
        ratingCount = r.html.find('.Ty81De')

        buttons = r.html.find('.fQqZ2e')

        for i in range(len(title)):
            obj = {
                "title": title[i].text
            }

            try:
                obj["category"] = details[i].find('.hGz87c:nth-child(2)')[0].text
            except:
                obj["category"] = details[i].find('.hGz87c:nth-child(1)')[0].text

            try:
                addressurl = unquote(buttons[i].find("a[aria-label='Directions']")[0].attrs['href'])
                addressurl = addressurl.split("&daddr=")
                addressurl = addressurl[1].split("&ved=")
                addressurl = addressurl[0].replace("+"," ")
                obj["address"] = addressurl
            except:
                obj["address"] = ""

            try:
                obj["website"] = buttons[i].find("a[aria-label='Website']")[0].attrs['href']
            except:
                None

            try:
                phonebutton = buttons[i].find("a[aria-label='Call']")[0].attrs['data-phone-number']
                obj["phoneNumber"] = phonebutton
            except:
                None

            try:
                ratingdata = ratingCount[i].text.replace("\n","--")
                if "(" in ratingdata:
                    obj["rating"] = float(ratingdata.split("--")[0].replace(",","."))
                else:
                    obj["rating"] = 0
                if "(" in ratingdata:
                    obj["ratingCount"] = int(float(ratingdata.split("--")[1].replace("(","").replace(")","")))
                else:
                    obj["ratingCount"] = 0
            except:
                obj["ratingCount"] = 0


            if(len(obj["address"])>1):
                result.append(str(obj))
        session.close()

        if(len(title) < 20):
            PAGINATION = 0
            break
        else:
            PAGINATION += len(title)

    return(result)