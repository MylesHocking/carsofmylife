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

