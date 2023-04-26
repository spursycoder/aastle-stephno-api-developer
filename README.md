# Aastle Stephno API Developer Assignment for Steeleye

Note: The API is deployed on render. Please go to https://trade-api-stephno.onrender.com/docs for testing. Initial loading time might be slow due the hosting being on free tier.

# Objectives:
This API is used to manage trade data and includes the following functionalities:

- Adding trade data to the database using a POST method.
- Listing all trade data from the database using a GET method, with pagination and sorting compatibility.
- Retrieving a trade data according to it's id using a GET method.
- Searching trade data from the database using a GET method and a search query.
- Filtering trade data from the database using a GET method and filter criteria.

# Importing Libraries:
The script imports the following libraries:

- pymongo: This is the official MongoDB driver for Python, used for interacting with MongoDB databases.
- datetime: This is a Python module used for working with dates and times.
- Pydantic: This is a library used for data validation and serialization in Python.
- FastAPI: This is a modern, fast (high-performance) web framework for building APIs with Python 3.6+ based on standard Python type hints.
- uvicorn: This is a Python ASGI web server used to run the FastAPI application.

# Using MongoDB
MongoDB Atlas instance has been used to replicate Elastisearch as it gave the flexibility to host online easily for free and its availability as a NoSQL Database

# Pydantic Models
The script defines two Pydantic models:
- TradeDetails: This model defines the details of a trade, such as the buy/sell indicator, price, and quantity. The Field class is used to define the description of each field.
- Trade: This model represents a single trade transaction and includes fields such as asset class, counterparty, instrument ID, instrument name, trade date and time, trade details, trade ID, and trader. The Field class is used to define the description, alias, default value, and other attributes of each field. The Config class is used to allow population by field name to do validation based on field names and not aliases as the data is stored in the database with the field names.

# Endpoints

## POST /trades/

### Description
This endpoint allows you to add trade data to a MongoDB cluster using a POST request.

### Request Body
trade (JSON) - Required - A JSON object containing trade data.

### Response
200 OK - The trade data was successfully added to the MongoDB cluster.
400 Bad Request - The trade data was not added to the MongoDB cluster due to a validation error.

## GET /trades/list

### Description
This endpoint allows you to fetch all the trade data stored in the MongoDB cluster using a GET request. Pagination and sorting functionality is also provided to handle large datasets.

### Query Parameters
- skip (int) - Optional - Number of records to skip. Default value is 0.
- limit (int) - Optional - Maximum number of records to return. Default value is 10.
- sort (str) - Optional - Parameter to sort the data by. Available options are asset_class, counterparty, instrument_id, instrument_name, trade_date_time, trade_details.buySellIndicator, trade_details.price, trade_details.quantity, trade_id, and trader.
- order (str) - Optional - Sort order to be used for the results. Available options are Des (Descending order) and Asc (Ascending order). Default value is Des.

### Response
200 OK - The trade data was successfully retrieved from the MongoDB cluster.

## GET /trades/

### Description
This endpoint allows you to search for trade data stored in the MongoDB cluster using a GET request. You can search for trades based on various parameters such as counterparty, instrument_id, instrument_name, and trader.

### Query Parameters
search (str) - Required - The search query to be used for the search.

### Response
200 OK - The trade data matching the search query was successfully retrieved from the MongoDB cluster.

## GET /trades/filter

### Description
This endpoint is used to filter trade data based on the applied filters. It supports the following filters:

### Query Parameters
- assetClass: An optional parameter to filter trade data based on the asset class. The allowed values for this parameter are "Bond", "FX", "Equity", and "Crypto".
- end: An optional parameter to filter trade data based on the trade date time. Trades with a trade date time less than or equal to this parameter value will be returned. The date should be provided in the format "yyyy-mm-ddTHH:MM:SS".
- maxPrice: An optional parameter to filter trade data based on the maximum trade price. Trades with a trade price less than or equal to this parameter value will be returned.
- minPrice: An optional parameter to filter trade data based on the minimum trade price. Trades with a trade price greater than or equal to this parameter value will be returned.
- start: An optional parameter to filter trade data based on the trade date time. Trades with a trade date time greater than or equal to this parameter value will be returned. The date should be provided in the format "yyyy-mm-ddTHH:MM:SS".
- tradeType: An optional parameter to filter trade data based on the trade type. The allowed values for this parameter are "BUY" and "SELL".

### Response:
The endpoint returns a list of trades that match the applied filters. Each trade is represented as a dictionary containing the trade data. If there are no trades that match the applied filters, an empty list is returned.

## GET /trades/id/{tID}

### Description
This endpoint retrieves a single trade from the MongoDB database based on its trade ID. The trade ID is passed in as a parameter in the URL.

### Path Parameters
tID: Required. A string representing the trade ID of the trade to be retrieved.

### Response
If the trade exists in the database, a JSON object representing the trade will be returned with a status code of 200.
If the trade does not exist in the database, a message "Trade with id {tID} does not exist" will be returned with a status code of 404.




