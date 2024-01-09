CREATE TABLE Calendar (
    date DATE PRIMARY KEY,
    year INT,
    quarter INT,
    quarterID TEXT,
    month_number INT,
    monthID TEXT,
    month_name TEXT,
    month_day INT,
    week_day INT,
    day_name TEXT,
    year_week INT,
    weekID TEXT
);

INSERT INTO Calendar (date, year, quarter, quarterID, month_number, monthID, month_name, month_day, week_day, day_name, year_week, weekID)
WITH RECURSIVE DateSeries AS (
    SELECT DATE '2022-01-01' AS date
    UNION ALL
    SELECT date + 1
    FROM DateSeries
    WHERE date < '2025-01-01'
)
SELECT
    date,
    EXTRACT(YEAR FROM date) AS year,
    EXTRACT(QUARTER FROM date) AS quarter,
    CONCAT(EXTRACT(YEAR FROM date), EXTRACT(QUARTER FROM date)) AS quarterID,
    EXTRACT(MONTH FROM date) AS month_number,
    TO_CHAR(date, 'YYYYMM') AS monthID,
    TO_CHAR(date, 'Month') AS month_name,
    EXTRACT(DAY FROM date) AS month_day,
    EXTRACT(ISODOW FROM date) AS week_day,
    TO_CHAR(date, 'Day') AS day_name,
    EXTRACT(WEEK FROM date) AS year_week,
    TO_CHAR(date, 'IYYYIW') AS weekID
FROM DateSeries;


-- Create PlanDigest table
CREATE TABLE PlanDigest (
    pid VARCHAR(255) PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    plan_descr VARCHAR(255)
);

-- Create PlanDate table
CREATE TABLE PlanDate (
    id SERIAL PRIMARY KEY,
    pid VARCHAR(255) REFERENCES PlanDigest(pid),
    date DATE NOT NULL,
    FOREIGN KEY (date) REFERENCES Calendar(date)
);

-- Create PlanCluster table
CREATE TABLE PlanCluster (
    pid VARCHAR(255),
    store_id INT,
    cluster_id INT,
    cluster_descr VARCHAR(255),
    PRIMARY KEY (pid, store_id),
    FOREIGN KEY (pid) REFERENCES PlanDigest(pid)
);

-- Create PlanSales table
CREATE TABLE PlanSales (
    date DATE,
    item_id INT,
    store_id INT,
    pid VARCHAR(255),
    planned_sales NUMERIC,
    PRIMARY KEY (date, item_id, store_id),
    FOREIGN KEY (store_id, pid) REFERENCES PlanCluster(store_id, pid),
    FOREIGN KEY (date) REFERENCES Calendar(date)
);

-- Create Forecast table with only date as a foreign key
CREATE TABLE Forecast (
    date DATE,
    item_id INT,
    store_id INT,
    forecast INT,
    PRIMARY KEY (date, item_id, store_id),
    FOREIGN KEY (date) REFERENCES Calendar(date)
);

-- Create Sales table with only date as a foreign key
CREATE TABLE Sales (
    date DATE,
    item_id INT,
    store_id INT,
    sales INT,
    PRIMARY KEY (date, item_id, store_id),
    FOREIGN KEY (date) REFERENCES Calendar(date)
);

