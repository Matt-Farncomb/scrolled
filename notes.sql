CREATE TABLE flights (
	id SERIAL PRIMARY KEY,
	origin VARCHAR NOT NULL,
	destination VARCHAR NOT NULL,
	duration INTEGER NOT NULL
);

INSERT INTO flights 
	(origin, destination, duration)
	VALUES ('New York', 'London', 415)

#Select everything from the flights table
SELECT * FROM flights;
SELECT origin, destination FROM flights;
#Select everything from flighta where the id == 3
SELECT * FROM flights WHERE id = 3;

SELECT * FROM flights WHERE destination = 'Paris' AND duration > 500;

SELECT AVG(duration) FROM flights;

SELECT COUNT(*) FROM flights;

SELECT MIN(duration) FROM flights;

SELECT * FROM flights WHERE origin IN ('New York', 'Lima');

#All things where the origin has an 'a' in it.
SELECT * FROM flights WHERE  origin like '%a%';

SELECT * FROM flights Limit 2;

SELECT * FROM flights ORDER by duration ASC;

#This will group flights by their  origin and show
# how  many flights come from each destination group
SELECT origin, COUNT(*) FROM flights GROUP BY origin;
#Same as above but it will list only groups that have
#a count > 1.

SELECT origin, COUNT(*) FROM flights GROUP BY origin
	HAVING COUNT(*) > 1

SELECT origin, destination, name 
	FROM flights JOIN passengers
	ON passengers.flight_id = flights.id
	WHERE name = 'Alice'

#This will do the top row query in the result of the query in the  brackets
SELECT * FROM flights WHERE id IN
	(SELECT FLIGHT_ID from passengers
		GROUP by flight_id HAVING COUNT(*) > 1);

UPDATE flights
	SET duration = 430
	WHERE origin = 'New York'
	AND destination = 'London'

DELETE FROM flights
	WHERE destination = 'Tokyo'

#SQL Transactions
BEGIN;
COMMIT;
#NOTE: references is a keyowrd to use to stop deleting stuff from tables
	#Left joins will get all the rows from the left query even if they don't match up

	#Rememerb indexes? Kind of like a ready made query that can make looking up regualr seacrehs quicker
CREATE table passengers (
	id SERIAL PRIMARY key,
	name VARCHAR NOT NULL,
	flight_id INTEGER REFERENCES flights)
