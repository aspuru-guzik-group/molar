--
-- PostgreSQL database dump
--

-- Dumped from database version 11.2 (Debian 11.2-1.pgdg90+1)
-- Dumped by pg_dump version 11.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE ONLY public.calculation DROP CONSTRAINT lnk_user_calculation;
ALTER TABLE ONLY public.calculation DROP CONSTRAINT lnk_software_calculation;
ALTER TABLE ONLY public.molecule_fragment DROP CONSTRAINT lnk_molecule_fragment;
ALTER TABLE ONLY public.conformation DROP CONSTRAINT lnk_molecule_conformation;
ALTER TABLE ONLY public.molecule_fragment DROP CONSTRAINT lnk_fragment_molecule;
ALTER TABLE ONLY public.calculation DROP CONSTRAINT lnk_conformation_calculation;
DROP INDEX public.unique_name_version;
DROP INDEX public.index_uuid_user;
DROP INDEX public.index_uuid_calculation;
DROP INDEX public.index_uuid_software;
DROP INDEX public.index_uuid_conformation;
DROP INDEX public.index_uuid_fragment;
DROP INDEX public.index_uuid_molecule;
DROP INDEX public.index_user_id;
DROP INDEX public.index_conformation_id;
ALTER TABLE ONLY public."user" DROP CONSTRAINT user_pkey;
ALTER TABLE ONLY public."user" DROP CONSTRAINT unique_user_name;
ALTER TABLE ONLY public.software DROP CONSTRAINT unique_software_version;
ALTER TABLE ONLY public.molecule DROP CONSTRAINT unique_molecule_smiles;
ALTER TABLE ONLY public.fragment DROP CONSTRAINT uniqu_fragment_smiles;
ALTER TABLE ONLY public.software DROP CONSTRAINT software_pkey;
ALTER TABLE ONLY public.molecule DROP CONSTRAINT molecule_pkey;
ALTER TABLE ONLY public.molecule_fragment DROP CONSTRAINT molecule_fragment_pkey;
ALTER TABLE ONLY public.fragment DROP CONSTRAINT fragment_pkey;
ALTER TABLE ONLY public.conformation DROP CONSTRAINT conformation_pkey;
ALTER TABLE public."user" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.software ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.molecule_fragment ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.molecule_fragment ALTER COLUMN fragment_id DROP DEFAULT;
ALTER TABLE public.molecule_fragment ALTER COLUMN molecule_id DROP DEFAULT;
ALTER TABLE public.molecule ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.fragment ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.conformation ALTER COLUMN molecule_id DROP DEFAULT;
ALTER TABLE public.conformation ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.calculation ALTER COLUMN conformation_id DROP DEFAULT;
ALTER TABLE public.calculation ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.user_id_seq;
DROP TABLE public."user";
DROP SEQUENCE public."tbl_molecule_MM_fragment_molecule_id_seq";
DROP SEQUENCE public."tbl_molecule_MM_fragment_fragment_id_seq";
DROP SEQUENCE public.software_id_seq;
DROP TABLE public.software;
DROP SEQUENCE public.molecule_id_seq;
DROP SEQUENCE public.molecule_fragment_id_seq;
DROP TABLE public.molecule_fragment;
DROP TABLE public.molecule;
DROP SEQUENCE public.fragment_id_seq;
DROP TABLE public.fragment;
DROP SEQUENCE public.conformation_id_seq;
DROP TABLE public.conformation;
DROP TABLE public.calculation;
DROP TYPE public.user_role;
DROP TYPE public.calculation_type;
DROP TYPE public.calculation_status;
DROP SCHEMA public;
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: calculation_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.calculation_status AS ENUM (
    'PENDING',
    'FAILED',
    'SUCCESS'
);


ALTER TYPE public.calculation_status OWNER TO postgres;

--
-- Name: calculation_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.calculation_type AS ENUM (
    'STRUCT_OPT',
    'FREQUENCY',
    'ENERGY'
);


ALTER TYPE public.calculation_type OWNER TO postgres;

--
-- Name: user_role; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.user_role AS ENUM (
    'ADMIN',
    'EDITOR',
    'READER'
);


ALTER TYPE public.user_role OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: calculation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.calculation (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    updated_on timestamp without time zone NOT NULL,
    created_on timestamp without time zone NOT NULL,
    status public.calculation_status NOT NULL,
    output text,
    properties jsonb DEFAULT '{}'::jsonb,
    coordinates jsonb NOT NULL,
    conformation_id uuid NOT NULL,
    software_id uuid NOT NULL,
    user_id integer NOT NULL,
    calculation_type public.calculation_type NOT NULL,
    output_conformation uuid
);


ALTER TABLE public.calculation OWNER TO postgres;

CREATE TABLE public.conformation (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    properties jsonb DEFAULT '{}'::jsonb,
    updated_on timestamp without time zone NOT NULL,
    created_on timestamp without time zone NOT NULL,
    molecule_id uuid NOT NULL
);


ALTER TABLE public.conformation OWNER TO postgres;

--
-- Name: conformation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.conformation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.conformation_id_seq OWNER TO postgres;

--
-- Name: conformation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.conformation_id_seq OWNED BY public.conformation.id;

--
-- Name: fragment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fragment (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    properties jsonb DEFAULT '{}'::jsonb,
    updated_on timestamp without time zone NOT NULL,
    created_on timestamp without time zone NOT NULL,
    smiles text NOT NULL
);


ALTER TABLE public.fragment OWNER TO postgres;

--
-- Name: fragment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fragment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fragment_id_seq OWNER TO postgres;

--
-- Name: fragment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fragment_id_seq OWNED BY public.fragment.id;


--
-- Name: molecule; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.molecule (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    properties jsonb DEFAULT '{}'::jsonb,
    updated_on timestamp without time zone NOT NULL,
    created_on timestamp without time zone NOT NULL,
    smiles text NOT NULL
);


ALTER TABLE public.molecule OWNER TO postgres;

--
-- Name: molecule_fragment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.molecule_fragment (
    molecule_id uuid NOT NULL,
    fragment_id uuid NOT NULL,
    "order" integer NOT NULL,
    created_on timestamp without time zone NOT NULL,
    updated_on timestamp without time zone NOT NULL,
    uuid uuid NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.molecule_fragment OWNER TO postgres;

--
-- Name: molecule_fragment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.molecule_fragment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.molecule_fragment_id_seq OWNER TO postgres;

--
-- Name: molecule_fragment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.molecule_fragment_id_seq OWNED BY public.molecule_fragment.id;


--
-- Name: molecule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.molecule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.molecule_id_seq OWNER TO postgres;

--
-- Name: molecule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.molecule_id_seq OWNED BY public.molecule.id;


--
-- Name: software; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.software (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    updated_on timestamp without time zone NOT NULL,
    created_on timestamp without time zone NOT NULL,
    name character varying(2044) NOT NULL,
    version character varying(2044) NOT NULL
);


ALTER TABLE public.software OWNER TO postgres;

--
-- Name: software_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.software_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.software_id_seq OWNER TO postgres;

CREATE SEQUENCE public.calculation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.calculation_id_seq OWNER TO postgres;
ALTER SEQUENCE public.calculation_id_seq OWNED BY public.calculation.id;

--
-- Name: software_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.software_id_seq OWNED BY public.software.id;

--
-- Name: tbl_molecule_MM_fragment_fragment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."tbl_molecule_MM_fragment_fragment_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."tbl_molecule_MM_fragment_fragment_id_seq" OWNER TO postgres;

--
-- Name: tbl_molecule_MM_fragment_fragment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."tbl_molecule_MM_fragment_fragment_id_seq" OWNED BY public.molecule_fragment.fragment_id;


--
-- Name: tbl_molecule_MM_fragment_molecule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."tbl_molecule_MM_fragment_molecule_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."tbl_molecule_MM_fragment_molecule_id_seq" OWNER TO postgres;

--
-- Name: tbl_molecule_MM_fragment_molecule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."tbl_molecule_MM_fragment_molecule_id_seq" OWNED BY public.molecule_fragment.molecule_id;

--
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    updated_on timestamp without time zone NOT NULL,
    created_on timestamp without time zone NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    role public.user_role DEFAULT 'READER'::public.user_role NOT NULL,
    email text NOT NULL
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_id_seq OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: conformation id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conformation ALTER COLUMN id SET DEFAULT nextval('public.conformation_id_seq'::regclass);


--
-- Name: fragment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fragment ALTER COLUMN id SET DEFAULT nextval('public.fragment_id_seq'::regclass);


--
-- Name: molecule id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.molecule ALTER COLUMN id SET DEFAULT nextval('public.molecule_id_seq'::regclass);


--
-- Name: molecule_fragment molecule_id; Type: DEFAULT; Schema: public; Owner: postgres
--


--
-- Name: molecule_fragment fragment_id; Type: DEFAULT; Schema: public; Owner: postgres
--



--
-- Name: molecule_fragment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.molecule_fragment ALTER COLUMN id SET DEFAULT nextval('public.molecule_fragment_id_seq'::regclass);


--
-- Name: software id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.software ALTER COLUMN id SET DEFAULT nextval('public.software_id_seq'::regclass);

ALTER TABLE ONLY public.calculation ALTER COLUMN id SET DEFAULT nextval('public.calculation_id_seq'::regclass);

--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
--
-- Name: conformation conformation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conformation
    ADD CONSTRAINT conformation_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.conformation
    ADD CONSTRAINT conformation_uuid_unique UNIQUE (uuid);

--
-- Name: fragment fragment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fragment
    ADD CONSTRAINT fragment_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.fragment
    ADD CONSTRAINT fragment_unique_uuid UNIQUE (uuid);

--
-- Name: molecule_fragment molecule_fragment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.molecule_fragment
    ADD CONSTRAINT molecule_fragment_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.molecule_fragment
    ADD CONSTRAINT molecule_fragment_unique_uuid UNIQUE (uuid);

--
-- Name: molecule molecule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.molecule
    ADD CONSTRAINT molecule_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.molecule
    ADD CONSTRAINT molecule_unique_uuid UNIQUE (uuid);

--
-- Name: software software_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.software
    ADD CONSTRAINT software_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.software
    ADD CONSTRAINT software_unique_uuid UNIQUE (uuid);

--
-- Name: fragment uniqu_fragment_smiles; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fragment
    ADD CONSTRAINT unique_fragment_smiles UNIQUE (smiles);

--
-- Name: molecule unique_molecule_smiles; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.molecule
    ADD CONSTRAINT unique_molecule_smiles UNIQUE (smiles);


--
-- Name: software unique_software_version; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.software
    ADD CONSTRAINT unique_software_version UNIQUE (name, version);


--
-- Name: user unique_user_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT unique_user_name UNIQUE (username);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.calculation
    ADD CONSTRAINT calculation_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.calculation
    ADD CONSTRAINT calculation_unique_uuid UNIQUE (uuid);

--
-- Name: index_conformation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_conformation_id ON public.calculation USING btree (conformation_id);


--
-- Name: index_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_user_id ON public.calculation USING btree (user_id);


--
-- Name: index_uuid111; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_uuid_molecule ON public.molecule USING btree (uuid);


--
-- Name: index_uuid1111; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_uuid_fragment ON public.fragment USING btree (uuid);


--
-- Name: index_uuid112; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_uuid_conformation ON public.conformation USING btree (uuid);


--
-- Name: index_uuid113; Type: INDEX; Schema: public; Owner: postgres
--


--
-- Name: index_uuid114; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_uuid_software ON public.software USING btree (uuid);




--
-- Name: index_uuid116111; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_uuid_calculation ON public.calculation USING btree (uuid);


--
-- Name: index_uuid117; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_uuid_user ON public."user" USING btree (uuid);


--
-- Name: unique_name_version; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX unique_name_version ON public.software USING btree (name, version);


--
-- Name: calculation lnk_conformation_calculation; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calculation
    ADD CONSTRAINT lnk_conformation_calculation FOREIGN KEY (output_conformation) REFERENCES public.conformation(uuid) MATCH FULL ON UPDATE CASCADE;


--
-- Name: calculation lnk_conformation_calculation; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calculation
    ADD CONSTRAINT lnk_conformation_calculation FOREIGN KEY (conformation_id) REFERENCES public.conformation(uuid) MATCH FULL ON UPDATE CASCADE;


--
-- Name: molecule_fragment lnk_fragment_molecule; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.molecule_fragment
    ADD CONSTRAINT lnk_fragment_molecule FOREIGN KEY (fragment_id) REFERENCES public.fragment(uuid) MATCH FULL ON UPDATE CASCADE;


--
-- Name: conformation lnk_molecule_conformation; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conformation
    ADD CONSTRAINT lnk_molecule_conformation FOREIGN KEY (molecule_id) REFERENCES public.molecule(uuid) MATCH FULL ON UPDATE CASCADE;


--
-- Name: molecule_fragment lnk_molecule_fragment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.molecule_fragment
    ADD CONSTRAINT lnk_molecule_fragment FOREIGN KEY (molecule_id) REFERENCES public.molecule(uuid) MATCH FULL ON UPDATE CASCADE;


--
-- Name: calculation lnk_software_calculation; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calculation
    ADD CONSTRAINT lnk_software_calculation FOREIGN KEY (software_id) REFERENCES public.software(uuid) MATCH FULL ON UPDATE CASCADE;


--
-- Name: calculation lnk_user_calculation; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calculation
    ADD CONSTRAINT lnk_user_calculation FOREIGN KEY (user_id) REFERENCES public."user"(id) MATCH FULL ON UPDATE CASCADE;


--
-- PostgreSQL database dump complete
--

