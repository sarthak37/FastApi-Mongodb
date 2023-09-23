
Deployed-Link(Swagger UI) - https://fastapi-mongodb-p9f8.onrender.com/docs

(may take upto 1 minute to load as it is free hosting)


*How to run locally-

1)Clone the Repository:

2)Create a Virtual Environment: python -m venv venv

3)Activate the Virtual Environment: venv\Scripts\activate

4)Install Dependencies: pip install -r requirements.txt

5)Run the FastAPI Application:: uvicorn main:app --host 0.0.0.0 --port 8000 --reload


*Product Endpoints:

1)POST /product/: Creates a new product in the database. Checks if a product with the same name already exists.

2)GET /product/: Retrieves a list of all products from the database.

3)GET /product/{product_id}: Retrieves details of a specific product by its ID.

4)PUT /product/{product_id}: Updates the details of a specific product.

5)DELETE /product/{product_id}: Deletes a product by its ID.


*Order Endpoints:

1)POST /order/: Creates a new order in the database. Checks product availability and updates product quantities.

2)PUT /order/{order_id}: Updates an existing order. Checks product availability and updates product quantities.

3)DELETE /order/{order_id}: Deletes an order by its ID.

4)GET /order/: Retrieves a list of all orders from the database.

5)GET /order/{order_id}: Retrieves details of a specific order by its ID.


*Functionality:


The code handles various scenarios such as checking if products exist, if there's enough quantity of products for an order, updating product quantities, and calculating the total cost of orders.




