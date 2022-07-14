### imports 
from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
import pyodbc
import sqlite3
from datetime import date

### initializations
app = Flask(__name__)
api = Api(app)
global conn
conn = sqlite3.connect("project_database.db", check_same_thread=False)
global cursor
cursor = conn.cursor()

### creating tables
cursor.execute("""CREATE TABLE inventoryList (
	itemName text NOT NULL , 
    itemCategory text NULL,
	quantity integer NULL,
    entryDate Date NULL,
    expiryDate Date NOT NULL,
    PRIMARY KEY (itemName, expiryDate)
    )"""
)

cursor.execute("""CREATE TABLE shoppingList(
	itemName text PRIMARY KEY,
	quantity integer NULL,
	purchased integer NULL
   )"""
)


### classes
class InventoryList(Resource):
    def get(self):
        query = "SELECT * FROM inventoryList"
        data = pd.read_sql(query,conn)                  
        data = data.to_dict()                           
        return {'data': data}, 200                      

    def post(self):
        parser = reqparse.RequestParser()  
        parser.add_argument('itemName', required=True)  
        parser.add_argument('quantity', required=True)
        entryDate = str(date.today())
        parser.add_argument('expiryDate', required=True)
        parser.add_argument('itemCategory', required=True)    
        args = parser.parse_args()  

        # read data
        query = "SELECT * FROM inventoryList"
        data = pd.read_sql(query,conn) 
        
        if args['itemName'] in list(data['itemName']):
            return {
                'message': f"'{args['itemName']}' already exists."
            }, 409
        else:
            # create new dataframe containing new values
            new_data = pd.DataFrame({
                'itemName': [args['itemName']],
                'quantity': [args['quantity']]
            })
            
            # add the newly provided values
            
            cursor.execute("INSERT INTO inventoryList VALUES (:itemName, :quantity, :entryDate, :expiryDate, :itemCategory) ",  
                            {'itemName':args['itemName'], 'quantity':args['quantity'], 'entryDate':entryDate, 'expiryDate':args['expiryDate'], 'itemCategory':args['itemCategory']} )
            conn.commit()
            return {'data': new_data.to_dict()}, 200  # return data with 200 OK

    def patch(self):
        parser = reqparse.RequestParser()  
        parser.add_argument('itemName', required=True)  
        parser.add_argument('quantity', required=True)
        parser.add_argument('newExpiryDate', required=True)
        parser.add_argument('oldExpiryDate', required=True)
        args = parser.parse_args()  

        # read data
        query = "SELECT * FROM inventoryList"
        data = pd.read_sql(query,conn) 
        
        if args['itemName'] in list(data['itemName']):
            cursor.execute("UPDATE inventoryList SET quantity = :quantity, expiryDate = :newExpiryDate WHERE itemName = :itemName and expiryDate = :oldExpiryDate", 
                                            {'itemName':args['itemName'], 'quantity':args['quantity'], 'newExpiryDate':args['newExpiryDate'], 'oldExpiryDate':args['oldExpiryDate']})
            conn.commit()
              
            # create new dataframe containing new values
            new_data = pd.DataFrame({
                'itemName': [args['itemName']],
                'quantity': [args['quantity']]
            })
            return {'data': new_data.to_dict()}, 200

        else:
            # otherwise the itemName does not exist
            return {
                'message': f"'{args['itemName']}' item not found."
            }, 404

    def delete(self):
        parser = reqparse.RequestParser()  
        parser.add_argument('itemName', required=True)  
        parser.add_argument('expiryDate', required=True)  
        args = parser.parse_args()  

        # read data
        query = "SELECT * FROM inventoryList"
        data = pd.read_sql(query,conn) 
                
        if args['itemName'] in list(data['itemName']):
            # remove data entry matching given itemName
            cursor.execute("DELETE FROM inventoryList WHERE itemName = :itemName and expiryDate = :expiryDate", {'itemName':args['itemName'], 'expiryDate':args['expiryDate']})
            conn.commit()

            # return data and 200 OK
            new_data = pd.DataFrame({
                'itemName': [args['itemName']]
            })
            return {'data': new_data.to_dict()}, 200

        else:
            # otherwise we return 404 because itemId does not exist
            return {
                'message': f"'{args['itemName']}' item not found."
            }, 404


class ShoppingList(Resource):
    def get(self):
        query = "SELECT * FROM shoppingList"
        data = pd.read_sql(query,conn)                  
        data = data.to_dict()                           
        return {'data': data}, 200                      

    def post(self):
        parser = reqparse.RequestParser()  
        parser.add_argument('itemName', required=True)  
        parser.add_argument('quantity', store_missing=False)
        args = parser.parse_args()  

        # read data
        query = "SELECT * FROM shoppingList"
        data = pd.read_sql(query,conn) 
        
        if args['itemName'] in list(data['itemName']):
            return {
                'message': f"'{args['itemName']}' already exists."
            }, 409
        else:
            # add the newly provided values
            if 'quantity' in args:
                cursor.execute("INSERT INTO shoppingList VALUES (:itemName, :quantity, :purchased) ",  
                                {'itemName':args['itemName'], 'quantity':args['quantity'], 'purchased': 0})
            else:
                cursor.execute("INSERT INTO shoppingList (itemName) VALUES (:itemName)", 
                                {'itemName':args['itemName'], 'quantity':0, 'purchased': 0} )
            conn.commit()

            # return data with 200 OK
            new_data = pd.DataFrame({
                'itemName': [args['itemName']]
            })
            return {'data': new_data.to_dict()}, 200  

    def patch(self):
        parser = reqparse.RequestParser()  
        parser.add_argument('itemName', required=True)  
        parser.add_argument('quantity', store_missing=False)
        parser.add_argument('purchased', store_missing=False)
        args = parser.parse_args()  

        # read data
        query = "SELECT * FROM shoppingList"
        data = pd.read_sql(query,conn) 
        
        if args['itemName'] in list(data['itemName']):
            if 'quantity' in args:
                cursor.execute("UPDATE shoppingList SET quantity = :quantity WHERE itemName = :itemName ",
                                {'itemName':args['itemName'], 'quantity':args['quantity']})
            if 'puchased' in args:
                cursor.execute("UPDATE shoppingList SET purchased = :purchased WHERE itemName = :itemName ", 
                                {'itemName':args['itemName'], 'purchased':args['purchased']})
            conn.commit()

            # return data with 200 OK
            new_data = pd.DataFrame({
                'itemName': [args['itemName']]
            })
            return {'data': new_data.to_dict()}, 200

        else:
            # otherwise the itemName does not exist
            return {
                'message': f"'{args['itemName']}' item not found."
            }, 404

    def delete(self):
        parser = reqparse.RequestParser()  
        parser.add_argument('itemName', required=True)  
        args = parser.parse_args()  

        # read data
        query = "SELECT * FROM shoppingList"
        data = pd.read_sql(query,conn) 
                
        if args['itemName'] in list(data['itemName']):
            # remove data entry matching given itemName
            cursor.execute("DELETE FROM shoppingList WHERE itemName = (:itemName)", {'itemName':args['itemName']})
            conn.commit()
            
            # return data and 200 OK
            new_data = pd.DataFrame({
                'itemName': [args['itemName']]
            })
            return {'data': new_data.to_dict()}, 200

        else:
            # otherwise we return 404 because itemId does not exist
            return {
                'message': f"'{args['itemName']}' item not found."
            }, 404


# add endpoints
api.add_resource(InventoryList, '/inventorylist')  
api.add_resource(ShoppingList, '/shoppinglist')

# run our Flask app
if __name__ == '__main__':
    app.run()  
