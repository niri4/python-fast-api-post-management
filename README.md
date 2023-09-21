# FastAPI App for Post managment

# Readme
This is a Python fast-api application that allows for the creation, and deletition of post via authenticate user

# Prerequisite
- mysql running on port: 3306
- Redis 

## Want to use this project?

1. Fork/Clone

2. Create .env file and set data mention in .sample.env file:

3. Create and activate a virtual environment:

    ```sh
    $ python3 -m venv venv && source venv/bin/activate
    ```

4. Install the requirements:

    ```sh
    (venv)$ pip install -r requirements.txt
    ```

5. Run the app:

    ```sh
    (venv)$ uvicorn main:app --host 0.0.0.0 --port 8081
    ```

6. Test at [http://localhost:8081/docs](http://localhost:8081/docs)