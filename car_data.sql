--
-- PostgreSQL database dump
--

-- Dumped from database version 16.0
-- Dumped by pg_dump version 16.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: car_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.car_data (
    model_id bigint,
    model_make_id text,
    model_name text,
    model_trim text,
    model_year bigint,
    model_body text,
    model_engine_position text,
    model_engine_cc bigint,
    model_engine_cyl double precision,
    model_engine_type text,
    model_engine_valves_per_cyl double precision,
    model_engine_power_ps double precision,
    model_engine_power_rpm double precision,
    model_engine_torque_nm double precision,
    model_engine_torque_rpm double precision,
    model_engine_bore_mm double precision,
    model_engine_stroke_mm double precision,
    model_engine_compression text,
    model_engine_fuel text,
    model_top_speed_kph double precision,
    model_0_to_100_kph double precision,
    model_drive text,
    model_transmission_type text,
    model_seats double precision,
    model_doors double precision,
    model_weight_kg double precision,
    model_length_mm double precision,
    model_width_mm double precision,
    model_height_mm double precision,
    model_wheelbase_mm double precision,
    model_lkm_hwy double precision,
    model_lkm_mixed double precision,
    model_lkm_city double precision,
    model_fuel_cap_l double precision,
    model_sold_in_us bigint,
    model_co2 double precision,
    model_make_display text
);


ALTER TABLE public.car_data OWNER TO postgres;

--
-- PostgreSQL database dump complete
--

ALTER TABLE car_images ADD COLUMN web_image_url TEXT;
ALTER TABLE car_images ADD COLUMN attribution_text TEXT;

select model_id, model_make_id,   model_name ,      model_trim      , model_year , model_body  , model_engine_cc  from car_data LIMIT 20; 


SELECT model_id, model_make_id, model_name, model_trim, model_year, model_body, model_engine_cc, COUNT(*)
FROM car_data
GROUP BY model_id, model_make_id, model_name, model_trim, model_year, model_body, model_engine_cc
HAVING COUNT(*) > 1;



https://www.google.co.uk/search?q=ford+fiesta+xr2&sca_esv=568754602&hl=en&authuser=0&tbm=isch&source=hp&biw=1904&bih=986&sclient=img
https://www.google.co.uk/search?q=9966+ford+fiesta+xr2&sca_esv=568754602&hl=en&authuser=0&tbm=isch&source=hp&biw=1904&bih=986&sclient=img


policies, filters (public demo too)
new environment for static assets



[0928/194336.089:INFO:CONSOLE(420)] "%c%s font-size: 18px; Using this console may allow attackers to impersonate you and steal your information using an attack called Self-XSS.



Host
ec2-52-215-68-14.eu-west-1.compute.amazonaws.com
Database
d5mqaipp88lvin
User
fazzudrhahcbsa
Port
5432
Password
RedactedPassword
URI
postgres://fazzudrhahcbsa:503e449ccdc062a8a50b6346ae553191cb50cff68fcbb8e89b49c4b844d04b34@ec2-52-215-68-14.eu-west-1.compute.amazonaws.com:5432/d5mqaipp88lvin
Heroku CLI
heroku pg:psql postgresql-graceful-10646 --app carsofmylife

heroku config:set DATABASE_URL=postgres://fazzudrhahcbsa:password@host:port/database


git remote set-url origin git@github.com:MylesHocking/carsofmylifescraper1.git
git remote set-url origin https://github.com/MylesHocking/carsofmylifescraper1.git

cars-of-my-life-images

C:\Users\myles\OneDrive\Documents\GitHub\Google-Image-Scraper\photos

gsutil -m cp -r C:\Users\myles\OneDrive\Documents\GitHub\Google-Image-Scraper\photos gs://cars-of-my-life-images/photos

great, seemed to work, forgot what I'm doing though!,  oh yeah adding a car... the main landing page should have a link to add a car (either your first or an additional one)


UPDATE car_data SET model_make_id = INITCAP(model_make_id);

UPDATE car_data SET model_make_id = REPLACE(model_make_id, '-', ' ');

C:\Credentials\dynamic-chiller-392810-e4dc5daacec3.json

