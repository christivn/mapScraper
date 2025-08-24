from requests_html import HTMLSession
from urllib.parse import unquote
import json
import csv
from tqdm import tqdm
import time

def search(query, lang, country, limit):
    result = []
    pagination = 0
    page_count = 0
    
    # Crear barra de progreso para esta query específica
    pbar = tqdm(desc=f"Scraping", unit="results", leave=False)
    
    while True:
        try:
            session = HTMLSession()
            url = f'https://www.google.com/localservices/prolist?hl={lang}&gl={country}&ssta=1&q={query}&oq={query}&src=2&lci={pagination}'
            r = session.get(url)
            r.html.render(timeout=10)

            data_script = r.html.find('#yDmH0d > script:nth-child(12)')[0].text.replace("AF_initDataCallback(", "").replace("'", "").replace("\n", "")[:-2]
            data_script = data_script.replace("{key:", "{\"key\":").replace(", hash:", ", \"hash\":").replace(", data:", ", \"data\":").replace(", sideChannel:", ", \"sideChannel\":")
            data_script = data_script.replace("\"key\": ds:", "\"key\": \"ds: ").replace(", \"hash\":", "\",\"hash\":")
            data_script = json.loads(data_script)

            places_data = data_script["data"][1][0]
            page_count += 1
            
            pbar.set_description(f"Página {page_count}")

            try:
                for i in range(len(places_data)):
                    place_id = places_data[i][21][0][1][4]
                    
                    obj = {
                        "id": place_id,
                        "url_place": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                        "title": places_data[i][10][5][1],
                        "category": places_data[i][21][9],
                        "address": "",
                        "phoneNumber": "",
                        "completePhoneNumber": "",
                        "domain": "",
                        "url": "",
                        "coor": "",
                        "stars": "",
                        "reviews": "",
                        "source_query": ""  # Nuevo campo para identificar la query original
                    }

                    try:
                        obj["phoneNumber"] = places_data[i][10][0][0][1][0][0]
                        obj["completePhoneNumber"] = places_data[i][10][0][0][1][1][0]
                    except TypeError:
                        pass

                    try:
                        obj["domain"] = places_data[i][10][1][1]
                        obj["url"] = places_data[i][10][1][0]
                    except TypeError:
                        pass

                    try:
                        obj["address"] = unquote(places_data[i][10][8][0][2]).split("&daddr=")[1].replace("+", " ")
                    except:
                        pass

                    try:
                        obj["coor"] = f'{places_data[i][19][0]},{places_data[i][19][1]}'
                    except:
                        pass

                    try:
                        obj["stars"] = places_data[i][21][3][0]
                        obj["reviews"] = places_data[i][21][3][2]
                    except:
                        pass
                    
                    result.append(obj)
                    pbar.update(1)
                    pbar.set_postfix({'Total': len(result)})
                    
                    if limit and len(result) >= limit:
                        session.close()
                        pbar.close()
                        return result
                        
            except TypeError:
                session.close()
                break

            if len(places_data) < 20:
                session.close()
                break
            else:
                pagination += len(places_data)
                # Pequeña pausa entre páginas
                time.sleep(0.3)
                
            session.close()
            
        except Exception as e:
            pbar.set_postfix({'Error': str(e)[:20]})
            if 'session' in locals():
                session.close()
            time.sleep(1)
            break

    pbar.close()
    return result

def save_to_csv(data, filename="data/output.csv"):
    """Guarda los datos en un archivo CSV."""
    if not data:
        print("No data to save.")
        return

    # Definir el orden de las columnas
    column_order = [
        "id", "url_place", "title", "category", "address", 
        "phoneNumber", "completePhoneNumber", "domain", "url", 
        "coor", "stars", "reviews", "source_query"
    ]
    
    # Asegurar que todas las columnas existan en todos los registros
    for record in data:
        for col in column_order:
            if col not in record:
                record[col] = ""
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=column_order)
            writer.writeheader()
            writer.writerows(data)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving data to {filename}: {e}")