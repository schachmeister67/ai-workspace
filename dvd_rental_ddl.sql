-- DVD Rental Database DDL
-- Generated from PostgreSQL database
-- Date: 2025-07-19 16:53:33.827372

-- Table: actor
CREATE TABLE actor (
    actor_id INTEGER NOT NULL SERIAL,
    first_name VARCHAR(45) NOT NULL,
    last_name VARCHAR(45) NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

-- Table: address
CREATE TABLE address (
    address_id INTEGER NOT NULL SERIAL,
    address VARCHAR(50) NOT NULL,
    address2 VARCHAR(50),
    district VARCHAR(20) NOT NULL,
    city_id SMALLINT NOT NULL,
    postal_code VARCHAR(10),
    phone VARCHAR(20) NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

-- Table: category
CREATE TABLE category (
    category_id INTEGER NOT NULL SERIAL,
    name VARCHAR(25) NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

-- Table: city
CREATE TABLE city (
    city_id INTEGER NOT NULL SERIAL,
    city VARCHAR(50) NOT NULL,
    country_id SMALLINT NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

-- Table: country
CREATE TABLE country (
    country_id INTEGER NOT NULL SERIAL,
    country VARCHAR(50) NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

-- Table: customer
CREATE TABLE customer (
    customer_id INTEGER NOT NULL SERIAL,
    store_id SMALLINT NOT NULL,
    first_name VARCHAR(45) NOT NULL,
    last_name VARCHAR(45) NOT NULL,
    email VARCHAR(50),
    address_id SMALLINT NOT NULL,
    activebool BOOLEAN NOT NULL DEFAULT true,
    create_date DATE NOT NULL DEFAULT ('now'::text)::date,
    last_update TIMESTAMP DEFAULT now(),
    active INTEGER
);

-- Table: film
CREATE TABLE film (
    film_id INTEGER NOT NULL SERIAL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    release_year INTEGER,
    language_id SMALLINT NOT NULL,
    rental_duration SMALLINT NOT NULL DEFAULT 3,
    rental_rate NUMERIC NOT NULL DEFAULT 4.99,
    length SMALLINT,
    replacement_cost NUMERIC NOT NULL DEFAULT 19.99,
    rating MPAA_RATING DEFAULT 'G'::mpaa_rating,
    last_update TIMESTAMP NOT NULL DEFAULT now(),
    special_features ARRAY,
    fulltext TSVECTOR NOT NULL
);

-- Table: film_actor
CREATE TABLE film_actor (
    actor_id SMALLINT NOT NULL,
    film_id SMALLINT NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

-- Table: film_category
CREATE TABLE film_category (
    film_id SMALLINT NOT NULL,
    category_id SMALLINT NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

-- Table: inventory
CREATE TABLE inventory (
    inventory_id INTEGER NOT NULL SERIAL,
    film_id SMALLINT NOT NULL,
    store_id SMALLINT NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

-- Table: language
CREATE TABLE language (
    language_id INTEGER NOT NULL SERIAL,
    name CHAR(20) NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

-- Table: payment
CREATE TABLE payment (
    payment_id INTEGER NOT NULL SERIAL,
    customer_id SMALLINT NOT NULL,
    staff_id SMALLINT NOT NULL,
    rental_id INTEGER NOT NULL,
    amount NUMERIC NOT NULL,
    payment_date TIMESTAMP NOT NULL
);

-- Table: rental
CREATE TABLE rental (
    rental_id INTEGER NOT NULL SERIAL,
    rental_date TIMESTAMP NOT NULL,
    inventory_id INTEGER NOT NULL,
    customer_id SMALLINT NOT NULL,
    return_date TIMESTAMP,
    staff_id SMALLINT NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

-- Table: staff
CREATE TABLE staff (
    staff_id INTEGER NOT NULL SERIAL,
    first_name VARCHAR(45) NOT NULL,
    last_name VARCHAR(45) NOT NULL,
    address_id SMALLINT NOT NULL,
    email VARCHAR(50),
    store_id SMALLINT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT true,
    username VARCHAR(16) NOT NULL,
    password VARCHAR(40),
    last_update TIMESTAMP NOT NULL DEFAULT now(),
    picture BYTEA
);

-- Table: store
CREATE TABLE store (
    store_id INTEGER NOT NULL SERIAL,
    manager_staff_id SMALLINT NOT NULL,
    address_id SMALLINT NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

-- Primary Keys
ALTER TABLE actor ADD PRIMARY KEY (actor_id);
ALTER TABLE address ADD PRIMARY KEY (address_id);
ALTER TABLE category ADD PRIMARY KEY (category_id);
ALTER TABLE city ADD PRIMARY KEY (city_id);
ALTER TABLE country ADD PRIMARY KEY (country_id);
ALTER TABLE customer ADD PRIMARY KEY (customer_id);
ALTER TABLE film ADD PRIMARY KEY (film_id);
ALTER TABLE film_actor ADD PRIMARY KEY (actor_id, film_id);
ALTER TABLE film_category ADD PRIMARY KEY (film_id, category_id);
ALTER TABLE inventory ADD PRIMARY KEY (inventory_id);
ALTER TABLE language ADD PRIMARY KEY (language_id);
ALTER TABLE payment ADD PRIMARY KEY (payment_id);
ALTER TABLE rental ADD PRIMARY KEY (rental_id);
ALTER TABLE staff ADD PRIMARY KEY (staff_id);
ALTER TABLE store ADD PRIMARY KEY (store_id);

-- Foreign Keys
ALTER TABLE address ADD CONSTRAINT fk_address_city FOREIGN KEY (city_id) REFERENCES city(city_id);
ALTER TABLE city ADD CONSTRAINT fk_city FOREIGN KEY (country_id) REFERENCES country(country_id);
ALTER TABLE customer ADD CONSTRAINT customer_address_id_fkey FOREIGN KEY (address_id) REFERENCES address(address_id);
ALTER TABLE film ADD CONSTRAINT film_language_id_fkey FOREIGN KEY (language_id) REFERENCES language(language_id);
ALTER TABLE film_actor ADD CONSTRAINT film_actor_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES actor(actor_id);
ALTER TABLE film_actor ADD CONSTRAINT film_actor_film_id_fkey FOREIGN KEY (film_id) REFERENCES film(film_id);
ALTER TABLE film_category ADD CONSTRAINT film_category_category_id_fkey FOREIGN KEY (category_id) REFERENCES category(category_id);
ALTER TABLE film_category ADD CONSTRAINT film_category_film_id_fkey FOREIGN KEY (film_id) REFERENCES film(film_id);
ALTER TABLE inventory ADD CONSTRAINT inventory_film_id_fkey FOREIGN KEY (film_id) REFERENCES film(film_id);
ALTER TABLE payment ADD CONSTRAINT payment_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES customer(customer_id);
ALTER TABLE payment ADD CONSTRAINT payment_rental_id_fkey FOREIGN KEY (rental_id) REFERENCES rental(rental_id);
ALTER TABLE payment ADD CONSTRAINT payment_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES staff(staff_id);
ALTER TABLE rental ADD CONSTRAINT rental_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES customer(customer_id);
ALTER TABLE rental ADD CONSTRAINT rental_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id);
ALTER TABLE rental ADD CONSTRAINT rental_staff_id_key FOREIGN KEY (staff_id) REFERENCES staff(staff_id);
ALTER TABLE staff ADD CONSTRAINT staff_address_id_fkey FOREIGN KEY (address_id) REFERENCES address(address_id);
ALTER TABLE store ADD CONSTRAINT store_address_id_fkey FOREIGN KEY (address_id) REFERENCES address(address_id);
ALTER TABLE store ADD CONSTRAINT store_manager_staff_id_fkey FOREIGN KEY (manager_staff_id) REFERENCES staff(staff_id);

-- Indexes
CREATE INDEX idx_actor_last_name ON public.actor USING btree (last_name);
CREATE INDEX idx_fk_city_id ON public.address USING btree (city_id);
CREATE INDEX idx_fk_country_id ON public.city USING btree (country_id);
CREATE INDEX idx_fk_address_id ON public.customer USING btree (address_id);
CREATE INDEX idx_fk_store_id ON public.customer USING btree (store_id);
CREATE INDEX idx_last_name ON public.customer USING btree (last_name);
CREATE INDEX film_fulltext_idx ON public.film USING gist (fulltext);
CREATE INDEX idx_fk_language_id ON public.film USING btree (language_id);
CREATE INDEX idx_title ON public.film USING btree (title);
CREATE INDEX idx_fk_film_id ON public.film_actor USING btree (film_id);
CREATE INDEX idx_store_id_film_id ON public.inventory USING btree (store_id, film_id);
CREATE INDEX idx_fk_customer_id ON public.payment USING btree (customer_id);
CREATE INDEX idx_fk_rental_id ON public.payment USING btree (rental_id);
CREATE INDEX idx_fk_staff_id ON public.payment USING btree (staff_id);
CREATE INDEX idx_fk_inventory_id ON public.rental USING btree (inventory_id);
CREATE UNIQUE INDEX idx_unq_rental_rental_date_inventory_id_customer_id ON public.rental USING btree (rental_date, inventory_id, customer_id);
CREATE UNIQUE INDEX idx_unq_manager_staff_id ON public.store USING btree (manager_staff_id);