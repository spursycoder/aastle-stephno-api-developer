# importing mongo clients
import pymongo
from pymongo import MongoClient
# importing datetime for date formatting
import datetime as dt
# imports for pydantic as provided by the company
from typing import Optional
from pydantic import BaseModel, Field
# imports for FastAPI
from fastapi import FastAPI, Query
import uvicorn
# misc
import os
import json


# Initialize FastAPI
app = FastAPI()
# MongoURI needed to connect to the database
uri = os.environ['MONGO_URI']
# Initialize PyMongo client
client = MongoClient(uri)
db = client.test

#Pydantic model as given by Steeleye for the TradeDetails field that will be inside Trade model  
class TradeDetails(BaseModel):
    buySellIndicator: str = Field(
        description="A value of BUY for buys, SELL for sells.")

    price: float = Field(description="The price of the Trade.")

    quantity: int = Field(description="The amount of units traded.")

#Pydantic model "Trade" which is to represent every single trade transaction
class Trade(BaseModel):
    asset_class: Optional[str] = Field(alias="assetClass", default=None, description="The asset class of the instrument traded. E.g. Bond, Equity, FX...etc")

    counterparty: Optional[str] = Field(default=None, description="The counterparty the trade was executed with. May not always be available")

    instrument_id: str = Field(alias="instrumentId", description="The ISIN/ID of the instrument traded. E.g. TSLA, AAPL, AMZN...etc")

    instrument_name: str = Field(alias="instrumentName", description="The name of the instrument traded.")

    trade_date_time: dt.datetime = Field(alias="tradeDateTime", description="The date-time the Trade was executed")

    trade_details: TradeDetails = Field(alias="tradeDetails", description="The details of the trade, i.e. price, quantity")

    trade_id: str = Field(alias="tradeId", default=None, description="The unique ID of the trade")

    trader: str = Field(description="The name of the Trader")

    
    class Config:
        #this configuration has been added to the model to do validation based on field names and not aliases as the data is stored in the database with the field names 
        allow_population_by_field_name = True

#home endpoint that redirects to docs page for testing
@app.get("/")
def home():
    return "Hello welcome to API assesment submission of Aastle Stephno, go to /docs to test the api"


#Endpoint of POST method used to add data to the MongoDB cluster
@app.post("/trades/")
def create_trade(trade: Trade):
    trade_dict = trade.dict()
    try:
        # validate the data using the Pydantic model
        Trade(**trade_dict)

        # Store the trade in MongoDB
        db.tradedata.insert_one(trade_dict)

        return {"message": "Trade created successfully", "tradeId": trade.trade_id}

    except:
        return "Pydantic data validation failed, check your request body again"



#Endpoint of GET method used to fetch all the trade data, with pagination and sorting compatability
@app.get("/trades/list")
def list_all_trades(skip: int = 0, limit: int = 10, sort: Optional[str] = Query(None, enum=["asset_class", "counterparty", "instrument_id", "instrument_name","trade_date_time","trade_details.buySellIndicator","trade_details.price","trade_details.quantity","trade_id","trader"]), order: Optional[str]=Query("Des",enum=["Des","Asc"])):
    print("getting all trades")
    # skip and limit are used to implement pagination, sort must be a proper parameter in accordance with the pydantic model
    # define the sort order based on the sort parameter

    if sort:
        if order=="Des":
            sort="-"+sort
        if sort.startswith("-"):
            # the "-" sign is to be given along with the parameter to sort the data in descending order
            sort_order = [(sort[1:], pymongo.DESCENDING)]
        else:
            sort_order = [(sort, pymongo.ASCENDING)]

        # query the MongoDB with skip, limit, and sort parameters
        trades = db.tradedata.find().skip(skip).limit(limit).sort(sort_order)
    else:
        trades = db.tradedata.find().skip(skip).limit(limit)

    # convert the trades to a list of dictionaries
    trades_list = [Trade(**trade_dict) for trade_dict in trades]

    return trades_list


#Endpoint of GET method used to search trade data according to search query
@app.get("/trades/")
def search_trades(search: str = None):
    print("searching for relevant trades....")
    print(search)

    #ensure indexes are created with text format before calling the text search on searchQuery in MongoDB

    trades = db.tradedata.find({
        "$text": {"$search": search},
        "$or": [
            {"counterparty": {"$exists": True}},
            {"instrument_id": {"$exists": True}},
            {"instrument_name": {"$exists": True}},
            {"trader": {"$exists": True}}
        ]

    })

    # convert the trades to a list of dictionaries
    trades_list = [Trade(**trade_dict) for trade_dict in trades]

    return trades_list


#Endpoint of GET method used to filter trade data according to applied filters
@app.get("/trades/filter")
def filter_trades(assetClass: Optional[str] =  Query(None, enum=["Bond", "FX", "Equity", "Crypto"]),
                  end: Optional[dt.datetime] = Query(None,description="Kindly give the date in proper format. For example, 2022-06-08T00:00:00"),
                  maxPrice: Optional[float] = None,
                  minPrice: Optional[float] = None,
                  start: Optional[dt.datetime] =  Query(None,description="Kindly give the date in proper format. For example, 2022-06-08T00:00:00"),
                  tradeType: Optional[str] =Query(None, enum=["BUY", "SELL"])):

    print("filtering trades")

    # create an empty filter dictionary
    filter_dict = {}

    # add all the necessary filters to the dictionary
    if assetClass:
        filter_dict["asset_class"] = assetClass

    if maxPrice:
        filter_dict["trade_details.price"] = {
            "$lte": maxPrice
        }

    if minPrice and maxPrice:
        filter_dict["trade_details.price"] = {
            "$gte": minPrice,
            "$lte": maxPrice
        }

    if minPrice and not maxPrice:
        filter_dict["trade_details.price"] = {
            "$gte": minPrice
        }

    if end:
        filter_dict["trade_date_time"] = {
            "$lte": end
        }

    if start and end:
        filter_dict["trade_date_time"] = {
            "$gte": start,
            "$lte": end
        }

    if start and not end:
        filter_dict["trade_date_time"] = {
            "$gte": start
        }

    if tradeType:
        filter_dict["trade_details.buySellIndicator"] = tradeType

    print(filter_dict)

    # query the trades collection with the filter dictionary
    trades = list(db.tradedata.find(filter_dict))

    # convert the resultant trades to a list of dictionaries
    trades_list = [Trade(**trade_dict) for trade_dict in trades]

    return trades_list


#Endpoint of GET method used to fetch trade data based on its id
@app.get("/trades/id/{tID}")
def get_single_trade_by_id(tID: str):
    print("getting a single trade")
    print(tID)
    # to get a single trade from the MongoDB instance use find_one() method on the collection
    trade = db.tradedata.find_one({"trade_id": tID})
    if trade:
        trade=Trade(**trade)
        return trade
    else:
        return "Trade with id {} does not exist".format(tID)


#Endpoint used during development for testing purposes
# @app.get("/testing")
# def test():
  # pass