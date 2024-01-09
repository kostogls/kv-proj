# Execution instructions

### What you'll need installed in your system:

1. Docker
2. Docker-compose
3. Pgadmin (optional)


### Initial steps:

1. Clone the repository

2. Regarding the .env file: Despite that common practice has it in .gitignore, I uploaded it, for convinience in running the code directly. If you wish to change the values of the variables in the .env, you can edit it accordingly. In the next steps, I mention where the values of the .env variables must be used.  


### Connect to the db (Option 1: using pgadmin tool - windows or linux)

Steps: 
    
1. Open a terminal

2. cd to the directory of the project where docker-compose is (.\kv-proj directory) and start the db container (without sudo if you're using windows):

    ```
    sudo docker compose up db
    ```
   The database is also created when the container starts.
    
4. If you have pgadmin tool, open it and register a new server. A dialogue box opens. There, in 'General' section: give the server the name you gave to the POSTGRES_DB .env variable.

   ![Register server general settings](./readme_img/reg_server_name.png?raw=true)

5. In 'Connection' section: Use 'localhost' as Host name/address, your port, username and password from PORT, USER, PASSWORD variables in .env file respectively.

   ![Register server connection settings](./readme_img/reg_server_conn.png?raw=true)

6. Choose the kivos-db database inside the server (it's the name defined in DATABASE and POSTGRES_DB variable in .env).

7. Right click on the database and open the Query tool. Then, in the editor that opens, open the ./sql_material/official_kivosdb_creation.sql script and run all the queries inside together. After that, the tables have been created. 

### Connect to the db (Option 2: using the terminal - linux only) 

Steps:

1. Open a terminal

2. cd to the directory of the project where docker-compose is and start the db container:
    
    ```
    sudo docker compose up db
    ```
    
6. First copy the ./sql_material/official_kivosdb_creation.sql script inside the docker container. kv-proj-db-1 is the container name:

    ```
    sudo docker cp ./sql_material/official_kivosdb_creation.sql kv-proj-db-1:/official_kivosdb_creation.sql
    ```
    
7. Connect to postgres inside the started docker container. If you have not made changes in the .env file or in docker-compose, you can run it as it is. kv-proj-db-1 is the 
   container name, postgres the db username and kivos-db the database name.
    
    ```
    sudo docker exec -it kv-proj-db-1 psql -U postgres -d kivos-db 
    ```
    
8. Run the sql script to create tables and relations
    
    ```
    \i official_kivosdb_creation.sql
    ```
    

### Run the app
Steps:

1. Open a new terminal, in the directory where docker-compose is, and start the app container:
    
    ```
    sudo docker compose up app
    ```
    
2. Open http://0.0.0.0:8501 or localhost:8501 to see the dashboard

     
### Note
Inside the ./sql_material directory, except the SQL script for creating the db, there is an SQL script containing all the queries, with extensive comments.
One could use this script to check the output tables on the database, in detail, using a tool like pgadmin.
    
