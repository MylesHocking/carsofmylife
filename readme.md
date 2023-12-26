
#GOOGLE
gsutil -m mv gs://cars-of-my-life-images/thumbs2/thumbs2/** gs://cars-of-my-life-images/thumbs/

gsutil -m cp -r C:\Users\myles\OneDrive\Documents\GitHub\Google-Image-Scraper\thumbs2\* gs://cars-of-my-life-images/thumbs/


gsutil -m cp -n -r C:\Users\myles\OneDrive\Documents\GitHub\Google-Image-Scraper\photos gs://cars-of-my-life-images/photos

POSTGRES SQL
psql -h localhost -p 5432 -U postgres -d carsofmylife
heroku pg:psql -a carsofmylife

ALTER TABLE users ADD COLUMN google_id VARCHAR(50) UNIQUE;
ALTER TABLE users ADD COLUMN is_google_account BOOLEAN DEFAULT FALSE;


carsofmylife=# select model_seats from car_data LIMIT 60;
DBMODEL:
flask db migrate -m "Add custom car make model variant"

INSERT INTO car_data (model_id, model_make_id, model_name) VALUES (1, 'Custom', 'Custom');

heroku run flask db upgrade --app carsofmylife

CYPRESS TESTS
C:\Users\myles\OneDrive\Documents\GitHub\COML-react> npx cypress run