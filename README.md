# fastapi-testing

FastAPI Testing

## Examples of use

* Create item
    ```shell
    curl -X POST -H "Content-Type: application/json" \
    -d '{"name": "Coffee Beans", "description": "Great Columbian Coffee Beans!!!"}' \
    http://0.0.0.0:8000/items
    ```
* Read items
    ```shell
    curl -X GET -H "Content-Type: application/json" \
    http://0.0.0.0:8000/items
    ```
* Read item detail
    ```shell
    curl -X GET -H "Content-Type: application/json" \
    http://0.0.0.0:8000/items/1
    ```
* Update item
    ```shell
    curl -X PUT -H "Content-Type: application/json" \
    -d '{"name": "Coffee Beans Updated", "description": "Great Columbian Coffee Beans!!!"}' \
    http://0.0.0.0:8000/items/1
    ```
* Delete item
    ```shell
    curl -X DELETE -H "Content-Type: application/json" \
    http://0.0.0.0:8000/items/1
    ```
