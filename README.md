# 🤖🗺️ Google Maps Scraper

Este proyecto es un **web scraper basado en Python** que utiliza un navegador sin interfaz gráfica para extraer información de lugares en Google Maps.

<br>

## 🚀 Funcionalidades
Con el **Google Maps Scraper** puedes obtener datos detallados sobre negocios y lugares específicos en Google Maps, tales como:
- ID del lugar
- Nombre del lugar
- Categoría
- Dirección completa
- Número de teléfono
- Dominio y URL asociados
- Coordenadas (latitud y longitud)
- Valoración promedio en estrellas
- Número de reseñas

<br>

## 📦 Paquetes requeridos
Para ejecutar este scraper, necesitas los siguientes paquetes de Python:
- `requests_html` - para realizar solicitudes HTML y renderizar contenido dinámico
- `urllib` - para manipulación de URLs
- `json` - para manejar datos estructurados en formato JSON

<br>

## ➡️ Ejemplo de código
A continuación, un ejemplo básico de uso:

```python
from mapScraper import placesCrawlerV2

# Define tu consulta
query = "Gym in Seville Spain"
# Lanza la búsqueda
results = placesCrawlerV2.search(query)

# Muestra los resultados
print(results)
```

<br>

## 📋 Ejemplo de salida
El scraper devuelve una lista en formato JSON con la información detallada de los lugares encontrados. Aquí tienes un ejemplo de salida:

```json
[
  {
    "id": "ChIJP0UWUA9sEg0RuJoxZuLavLs",
    "title": "Sevilla",
    "category": "Gym",
    "address": "C. Amor de Dios, 35, Casco Antiguo, 41002 Sevilla",
    "phoneNumber": "681 96 61 09",
    "completePhoneNumber": "+34 681 96 61 09",
    "domain": "instagram.com",
    "url": "https://instagram.com/sevillagym_oficial?utm_medium=copy_link",
    "coor": "37.3958503,-5.994440399999999",
    "stars": 4.3,
    "reviews": 253
  },
  {
    "id": "ChIJD6RGzE9pEg0RJmWVq_nh2j0",
    "title": "Sevilla Century Fitness Gym",
    "category": "Gymnastics center",
    "address": "Av. del Alcalde Manuel del Valle, 50, Norte, 41015 Sevilla",
    "phoneNumber": "691 84 08 73",
    "completePhoneNumber": "+34 691 84 08 73",
    "domain": "www.centuryfitness.es",
    "url": "https://www.centuryfitness.es/",
    "coor": "37.4127951,-5.9724556",
    "stars": 4.8,
    "reviews": 2442
  },
  {
    "id": "ChIJNYda7WtsEg0RCC83FLkQK1Q",
    "title": "Hispanic Happiness Club",
    "category": "Athletic club",
    "address": "C. Ignacio Gómez Millán, s/n, 41010 Sevilla",
    "phoneNumber": "954 33 88 08",
    "completePhoneNumber": "+34 954 33 88 08",
    "domain": "www.galisport.com",
    "url": "http://www.galisport.com/",
    "coor": "37.3839533,-6.007852499999999",
    "stars": 3.5,
    "reviews": 172
  }
]
```

<br>

## 🛠️ Configuración y uso
1. Clona este repositorio.
2. Asegúrate de tener los paquetes necesarios instalados.
3. Modifica `query` para personalizar tu búsqueda y ejecuta el script para ver los resultados.

<br>

## ⚠️ Nota
Este proyecto es solo para fines educativos y de investigación. Respeta las políticas de uso y términos de servicio de Google. 
