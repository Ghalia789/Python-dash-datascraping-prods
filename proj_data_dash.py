import requests
import csv
from bs4 import BeautifulSoup
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])

urls = ["https://www.jumia.com.tn/smartphones/",
        "https://www.jumia.com.tn/smartphones/?page=2#catalog-listing",
        "https://www.jumia.com.tn/smartphones/?page=3#catalog-listing",
        "https://www.jumia.com.tn/smartphones/?page=4#catalog-listing",
        "https://www.jumia.com.tn/smartphones/?page=5#catalog-listing",
        "https://www.jumia.com.tn/smartphones/?page=6#catalog-listing",
        "https://www.jumia.com.tn/smartphones/?page=7#catalog-listing",
        "https://www.jumia.com.tn/smartphones/?page=8#catalog-listing", 
        "https://www.jumia.com.tn/smartphones/?page=9#catalog-listing",
        "https://www.jumia.com.tn/smartphones/?page=10#catalog-listing",
        "https://www.jumia.com.tn/smartphones/?page=11#catalog-listing"]

# Extract the brand, name, price, image, and link of each product and save to CSV file
with open("products.csv", encoding="utf-8", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Brand", "Name", "Price", "Image", "Link"])
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        products = soup.find_all("article", class_="prd _fb col c-prd")
        for product in products:
            name = product.find("h3", class_="name").text
            brand = product.find("a", class_="core")["data-brand"]
            price = product.find("div", class_="prc").text
            price = float(price.replace(",", "").rstrip(" TND"))
            image = product.find("img", class_="img")["data-src"]
            link = product.find("a", class_="core")["href"]
            link = "https://www.jumia.com.tn/smartphones" + link
            writer.writerow([brand, name, price, image, link])

# Get the list of unique brands from the CSV file
brands = []
with open("products.csv", mode="r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row["Brand"] not in brands:
            brands.append(row["Brand"])

# Create the Dash layout with input fields for brand and maximum price
app.layout = dbc.Container(
    [
        html.H1("Smartphone Search", className="card mb-4 mt-4"),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Brand"),
                dcc.Dropdown(
                    id="brand-dropdown",
                    options=[{"label": brand, "value": brand} for brand in brands],
                    style={"padding": "1.5rem 2.5rem", "font-size": "1.2rem"},
                ),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Maximum Price"),
                dcc.Input(id="price-input", type="number"),
            ]
        ),
        dbc.Button("Search", id="search-button", color="primary", className="mt-3"),
        html.Hr(),
        dbc.CardGroup(id="search-results"),
    ]
)


# Define the Dash callback to handle the search button click event
@app.callback(
    dash.dependencies.Output("search-results", "children"),
    [dash.dependencies.Input("search-button", "n_clicks")],
    [dash.dependencies.State("brand-dropdown", "value")],
    [dash.dependencies.State("price-input", "value")],
)
def search_products(n_clicks, brand, max_price):
    if not n_clicks:
        return
    # Filter the products based on the user's preferences
    search_results = []
    with open("products.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if (not brand or brand.lower() in row["Brand"].lower()) and \
                    (not max_price or float(row["Price"]) <= max_price):
                    search_results.append(row)
                
    # Create a list of product cards for the search results
    product_cards = [
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardImg(src=row["Image"], top=True),
                    dbc.CardBody(
                        [
                            html.H5(row["Name"], className="card-title"),
                            html.P(row["Brand"], className="card-text"),
                            html.P(str(row["Price"]) + " TND", className="card-text"),
                            dbc.Button(
                                "View", color="primary", href=row["Link"], target="_blank"
                            ),
                        ]
                    ),
                ],
                className="mb-3",
            ),
            width=4,
        )
        for row in search_results
    ]

    cards_row = dbc.Row(product_cards, className="mb-4 justify-content-center")
    container = html.Div(cards_row, className="container")
    return container



if __name__ == "__main__":
    app.run_server(debug=True)
