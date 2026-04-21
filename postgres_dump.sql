--
-- PostgreSQL database dump
--

\restrict mJORogBFJXHALsTQQBUlfxEj0sWJrUpHe1FHcgCeZbgX2FEKLxYcPEjzpcGYDwf

-- Dumped from database version 15.14
-- Dumped by pg_dump version 15.14

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
-- Name: channels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.channels (
    id bigint NOT NULL,
    channel_id bigint NOT NULL,
    title character varying NOT NULL,
    invite_link character varying NOT NULL
);


ALTER TABLE public.channels OWNER TO postgres;

--
-- Name: channels_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.channels_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.channels_id_seq OWNER TO postgres;

--
-- Name: channels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.channels_id_seq OWNED BY public.channels.id;


--
-- Name: promo_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.promo_codes (
    id bigint NOT NULL,
    code character varying NOT NULL,
    bonus_days integer NOT NULL,
    discount_percent integer NOT NULL,
    expire_date timestamp without time zone,
    max_uses integer NOT NULL,
    uses_left integer NOT NULL
);


ALTER TABLE public.promo_codes OWNER TO postgres;

--
-- Name: promo_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.promo_codes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.promo_codes_id_seq OWNER TO postgres;

--
-- Name: promo_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.promo_codes_id_seq OWNED BY public.promo_codes.id;


--
-- Name: tariffs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tariffs (
    id bigint NOT NULL,
    name character varying NOT NULL,
    price double precision NOT NULL,
    duration_days integer NOT NULL,
    is_active boolean NOT NULL
);


ALTER TABLE public.tariffs OWNER TO postgres;

--
-- Name: tariffs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tariffs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tariffs_id_seq OWNER TO postgres;

--
-- Name: tariffs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tariffs_id_seq OWNED BY public.tariffs.id;


--
-- Name: used_promo_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.used_promo_codes (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    promo_code_id bigint NOT NULL,
    used_date timestamp without time zone NOT NULL
);


ALTER TABLE public.used_promo_codes OWNER TO postgres;

--
-- Name: used_promo_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.used_promo_codes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.used_promo_codes_id_seq OWNER TO postgres;

--
-- Name: used_promo_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.used_promo_codes_id_seq OWNED BY public.used_promo_codes.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id bigint NOT NULL,
    username character varying,
    full_name character varying NOT NULL,
    reg_date timestamp without time zone NOT NULL,
    subscription_end_date timestamp without time zone,
    marzban_username character varying,
    has_received_trial boolean NOT NULL,
    referrer_id bigint,
    referral_bonus_days integer NOT NULL,
    is_first_payment_made boolean NOT NULL,
    support_topic_id integer
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: channels id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.channels ALTER COLUMN id SET DEFAULT nextval('public.channels_id_seq'::regclass);


--
-- Name: promo_codes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.promo_codes ALTER COLUMN id SET DEFAULT nextval('public.promo_codes_id_seq'::regclass);


--
-- Name: tariffs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tariffs ALTER COLUMN id SET DEFAULT nextval('public.tariffs_id_seq'::regclass);


--
-- Name: used_promo_codes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.used_promo_codes ALTER COLUMN id SET DEFAULT nextval('public.used_promo_codes_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: channels; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.channels (id, channel_id, title, invite_link) FROM stdin;
\.


--
-- Data for Name: promo_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.promo_codes (id, code, bonus_days, discount_percent, expire_date, max_uses, uses_left) FROM stdin;
\.


--
-- Data for Name: tariffs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tariffs (id, name, price, duration_days, is_active) FROM stdin;
2	Тариф неделя	50	7	t
4	Тариф 3 месяца	349	90	t
5	Тариф 6 месяцев	649	180	t
6	Тариф год	949	365	t
3	Тариф месяц	99	30	t
\.


--
-- Data for Name: used_promo_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.used_promo_codes (id, user_id, promo_code_id, used_date) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (user_id, username, full_name, reg_date, subscription_end_date, marzban_username, has_received_trial, referrer_id, referral_bonus_days, is_first_payment_made, support_topic_id) FROM stdin;
7725907943	\N	Sami Ullah	2025-10-13 06:18:39.004715	\N	\N	f	\N	0	f	\N
5414851134	aleksrams	Алексей Шилов	2025-10-13 06:27:40.350423	\N	\N	f	\N	0	f	\N
6312863686	sohailasghar232	Muhammad Sohail Asghar	2025-10-13 06:31:22.386529	\N	\N	f	\N	0	f	\N
6846125309	Alexej02	Alex Kiselev	2025-10-13 11:42:55.819079	\N	\N	f	\N	0	f	\N
738672059	\N	Аня	2025-10-13 06:56:00.184615	2026-10-23 06:57:05.763527	user_738672059	f	\N	0	t	\N
7282188118	Ssisyv	ЕГОР	2025-10-04 11:07:33.108465	\N	\N	f	\N	0	f	\N
1146900703	Lairon2005	That’s that me espresso	2025-09-13 13:24:28.945095	2031-04-23 06:09:01.677875	user_1146900703	t	\N	21	t	22
2109374034	Tia_Hatake	Тия Хатаке	2025-10-15 08:22:05.464733	2025-10-22 08:22:23.721545	user_2109374034	t	\N	0	f	\N
449696999	volandemort27	qqqqqqqqq	2025-09-13 15:36:26.435365	2025-12-01 13:28:58.839432	user_449696999	f	1146900703	0	t	\N
8086324646	silatenii	broomer	2025-10-09 06:36:27.218902	2025-11-15 06:36:49.82432	user_8086324646	t	\N	0	t	\N
7108317408	aaandrey23	Андрей	2025-10-10 14:59:23.395827	\N	\N	f	\N	0	f	\N
328214246	\N	Софья Боброва	2025-09-13 15:53:17.248862	2025-09-16 15:53:17.279664	user_328214246	f	1146900703	0	f	\N
5552137646	Muhammed97x	⚡Ⓜ️uhammed ⚡	2025-10-13 13:39:10.243989	2025-10-20 13:39:13.446772	user_5552137646	t	\N	0	f	\N
866315154	THUGGER_NGG59	THUGGER	2025-10-22 07:01:50.414094	2025-10-29 07:02:02.144453	user_866315154	t	\N	0	f	\N
439855137	Iria_Work	Илья🚀 Бакай	2025-10-13 05:22:48.823136	\N	\N	f	\N	0	f	\N
6056136474	Anayashykh	Anayashykh	2025-10-13 05:22:56.704705	2025-10-20 05:23:15.361121	user_6056136474	t	\N	0	f	\N
7756722862	semenpikstman	Семён Пикстман	2025-10-13 05:23:26.873253	\N	\N	f	\N	0	f	\N
8490096155	Tabu2884	Tabu Miya	2025-10-13 05:23:47.070581	\N	\N	f	\N	0	f	\N
7929254810	IgnatStarlinkov	Игнат Старлинков	2025-10-13 05:24:20.73763	\N	\N	f	\N	0	f	\N
8243931457	Antone888	Anton Evdokimov	2025-10-13 05:24:08.346198	2025-10-20 05:24:28.672178	user_8243931457	t	\N	0	f	\N
5299577492	Cherepok89	Bogdan cvuch	2025-10-13 05:25:31.456034	\N	\N	f	\N	0	f	\N
6094942381	Vladislav90123	Влад	2025-10-13 05:30:48.572746	\N	\N	f	\N	0	f	\N
6106965356	shurik_999	shurik_999	2025-10-13 05:33:31.414174	\N	\N	f	\N	0	f	\N
8135148390	symbat110422	Сымбат	2025-10-13 05:40:30.918473	\N	\N	f	\N	0	f	\N
7317691505	AyanM996	Ayan .	2025-10-13 05:39:10.779603	2025-10-20 05:40:43.203478	user_7317691505	t	\N	0	f	\N
6964506558	Uzairkhan312	Uzair Khan	2025-10-13 07:07:09.539939	\N	\N	f	\N	0	f	\N
5652034797	SAFIQ7894	ATIK BHAI	2025-10-13 05:43:00.352732	2025-10-20 05:43:52.731096	user_5652034797	t	\N	0	f	\N
470035429	Svekrukha	Maksim@bountyhash	2025-10-13 05:47:13.189166	\N	\N	f	\N	0	f	\N
6262448324	Gravitator2000	Снежана Суворова	2025-10-13 05:47:57.312784	\N	\N	f	\N	0	f	\N
6393928835	Nyusha325	Татьянa	2025-10-13 05:48:16.69954	\N	\N	f	\N	0	f	\N
7991253461	vadim4195	Vadims	2025-10-13 05:57:09.393949	\N	\N	f	\N	0	f	\N
6151086473	zvzvzv222	Азимут	2025-10-13 05:57:57.688333	\N	\N	f	\N	0	f	\N
8007881171	\N	Rabia Saleem	2025-10-13 05:59:28.053228	\N	\N	f	\N	0	f	\N
6626231703	tamim1805	Tamim	2025-10-13 06:03:33.70223	\N	\N	f	\N	0	f	\N
7500884153	SanpenMan	Александр	2025-10-13 07:25:57.127816	\N	\N	f	\N	0	f	\N
6824965696	useless006	𝐓𝐨𝐧𝐲 𝐒𝐭𝐚𝐫𝐤👑🦒	2025-10-13 06:04:09.550946	2025-10-20 06:05:17.83914	user_6824965696	t	\N	0	f	\N
8490206286	hinakhan3713	Hina Khan	2025-10-13 06:07:35.74669	\N	\N	f	\N	0	f	\N
8309695773	adnandani34	Ch Adnan	2025-10-13 06:09:23.248353	\N	\N	f	\N	0	f	\N
7846885350	OlgaOlgina8312	Ольга	2025-10-13 06:15:03.088089	\N	\N	f	\N	0	f	\N
5521593202	Conik41	Leon	2025-10-13 07:52:35.428542	\N	\N	f	\N	0	f	\N
6433440899	\N	Трезвый	2025-10-13 08:31:14.309587	2025-10-20 08:31:24.894276	user_6433440899	t	\N	0	f	\N
8446820870	Yayaspi	Spiderman	2025-10-13 08:35:47.96732	\N	\N	f	\N	0	f	\N
6441652499	aleksguide77	Алексей	2025-10-13 08:38:39.375443	\N	\N	f	\N	0	f	\N
1214446972	Aki_Vik	Akivika	2025-10-13 08:39:07.207756	\N	\N	f	\N	0	f	\N
8273497561	\N	ᅠ	2025-10-14 11:23:22.78297	2025-10-21 11:23:35.998074	user_8273497561	t	\N	0	f	\N
6209555080	aamirshaikh6105	Aamir	2025-10-13 08:52:00.368254	2025-10-20 08:53:43.824095	user_6209555080	t	\N	0	f	\N
374466050	grey_gandalf	Tania Grey	2025-10-13 08:58:42.391829	\N	\N	f	\N	0	f	\N
338327921	keyrnza	Евгения	2025-10-13 09:36:39.741339	\N	\N	f	\N	0	f	\N
8127389075	Babafareed184	Baba Fareed	2025-10-13 09:51:56.808552	\N	\N	f	\N	0	f	\N
5558988322	black_ladi_ligh	Крис Станиславовна Крюкова	2025-10-13 09:56:32.523255	\N	\N	f	\N	0	f	\N
5163698414	Mixa866	михаил	2025-10-13 10:07:20.130244	\N	\N	f	\N	0	f	\N
7890253333	Winnergms9	Winner GMS	2025-10-13 10:28:35.458454	\N	\N	f	\N	0	f	\N
665234140	mridul016	Mridul	2025-10-13 10:41:26.476156	\N	\N	f	\N	0	f	\N
871233313	AlexGriner	Good	2025-10-13 10:48:05.797955	\N	\N	f	\N	0	f	\N
6813636167	Catoo1245	haram maki	2025-10-13 11:40:27.909011	\N	\N	f	\N	0	f	\N
5938123338	AlirezaMirzaei_2005	Alireza	2025-10-14 15:01:36.036681	\N	\N	f	\N	0	f	\N
7244488526	Chika2303	Chika	2025-10-14 17:11:05.641436	\N	\N	f	\N	0	f	\N
5277694166	\N	Кирилл Подвинцев	2025-09-13 14:00:20.60964	2025-11-21 09:52:16.959246	user_5277694166	f	1146900703	0	t	\N
694242528	frocjok	zzzzz	2025-10-18 19:35:17.379875	\N	\N	f	\N	0	f	\N
5696383036	Borispetrovich54	Борис	2025-09-14 09:28:40.321937	2025-11-18 09:53:54.877737	user_5696383036	f	1146900703	0	t	\N
7639033854	yhpvff	Зачем	2025-10-02 06:55:57.537961	2025-11-21 09:38:02.639422	user_7639033854	t	\N	0	f	\N
5800950494	\N	Oleg Olega	2025-10-20 06:29:00.798353	2025-10-27 06:37:48.59612	user_5800950494	t	\N	0	f	\N
797948287	onerake	Саша	2025-09-19 13:42:06.040316	2025-11-18 19:14:03.581276	user_797948287	f	\N	0	t	\N
6043979307	popova_kira	Kira	2025-09-13 15:25:56.215306	2025-11-15 13:40:37.060867	user_6043979307	f	1146900703	0	f	\N
7346056280	Kardinal1210	Kara2000	2025-11-06 07:07:54.890449	\N	\N	f	\N	0	f	\N
1084773416	jenya2hh	jenya2h	2025-09-13 13:37:23.829533	2026-10-14 04:07:29.615082	user_1084773416	f	1146900703	0	f	\N
1980750141	Alexmen100889	Алексей	2025-10-31 10:26:55.086652	2025-12-01 10:38:16.119759	user_1980750141	f	\N	0	t	\N
1134604042	\N	Ярослав	2025-10-27 06:28:07.678759	2025-12-03 08:24:13.406916	user_1134604042	f	\N	0	t	48
\.


--
-- Name: channels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.channels_id_seq', 1, false);


--
-- Name: promo_codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.promo_codes_id_seq', 1, false);


--
-- Name: tariffs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tariffs_id_seq', 6, true);


--
-- Name: used_promo_codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.used_promo_codes_id_seq', 1, false);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_user_id_seq', 1, false);


--
-- Name: channels channels_channel_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.channels
    ADD CONSTRAINT channels_channel_id_key UNIQUE (channel_id);


--
-- Name: channels channels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.channels
    ADD CONSTRAINT channels_pkey PRIMARY KEY (id);


--
-- Name: promo_codes promo_codes_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.promo_codes
    ADD CONSTRAINT promo_codes_code_key UNIQUE (code);


--
-- Name: promo_codes promo_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.promo_codes
    ADD CONSTRAINT promo_codes_pkey PRIMARY KEY (id);


--
-- Name: tariffs tariffs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tariffs
    ADD CONSTRAINT tariffs_pkey PRIMARY KEY (id);


--
-- Name: used_promo_codes used_promo_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.used_promo_codes
    ADD CONSTRAINT used_promo_codes_pkey PRIMARY KEY (id);


--
-- Name: users users_marzban_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_marzban_username_key UNIQUE (marzban_username);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: used_promo_codes used_promo_codes_promo_code_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.used_promo_codes
    ADD CONSTRAINT used_promo_codes_promo_code_id_fkey FOREIGN KEY (promo_code_id) REFERENCES public.promo_codes(id);


--
-- Name: used_promo_codes used_promo_codes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.used_promo_codes
    ADD CONSTRAINT used_promo_codes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: users users_referrer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_referrer_id_fkey FOREIGN KEY (referrer_id) REFERENCES public.users(user_id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict mJORogBFJXHALsTQQBUlfxEj0sWJrUpHe1FHcgCeZbgX2FEKLxYcPEjzpcGYDwf

