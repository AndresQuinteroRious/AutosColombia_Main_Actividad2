--
-- PostgreSQL database dump
--

\restrict imxfsh2rzGqHZnvS37nCQ7efzigdl7H0ZwctriyGDdoT7Gnt90HYoa0m8bnC6Ld

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

-- Started on 2026-11-08 19:16:35

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- TOC entry 219 (class 1259 OID 24646)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 24650)
-- Name: ausencias; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ausencias (
    id bigint NOT NULL,
    turno_id bigint NOT NULL,
    motivo text NOT NULL,
    reemplazo_id bigint,
    observacion text,
    registrado_en timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.ausencias OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 24660)
-- Name: ausencias_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.ausencias ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.ausencias_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 222 (class 1259 OID 24661)
-- Name: celda; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.celda (
    id bigint NOT NULL,
    codigo text NOT NULL,
    tipo text NOT NULL,
    CONSTRAINT ck_celda_codigo_no_vacio CHECK ((codigo ~ '[^[:space:]]'::text)),
    CONSTRAINT ck_celda_codigo_normalizado CHECK ((codigo = upper(regexp_replace(codigo, '^[[:space:]]+|[[:space:]]+$'::text, ''::text, 'g'::text)))),
    CONSTRAINT ck_celda_tipo_no_vacio CHECK ((tipo ~ '[^[:space:]]'::text))
);


ALTER TABLE public.celda OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 24672)
-- Name: celda_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.celda ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.celda_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 224 (class 1259 OID 24673)
-- Name: cuenta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cuenta (
    id bigint NOT NULL,
    usuario text NOT NULL,
    password_hash text NOT NULL,
    rol text NOT NULL,
    operador_id bigint
);


ALTER TABLE public.cuenta OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 24682)
-- Name: cuenta_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cuenta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cuenta_id_seq OWNER TO postgres;

--
-- TOC entry 5183 (class 0 OID 0)
-- Dependencies: 225
-- Name: cuenta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cuenta_id_seq OWNED BY public.cuenta.id;


--
-- TOC entry 226 (class 1259 OID 24683)
-- Name: estancia; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estancia (
    id bigint NOT NULL,
    vehiculo_id bigint NOT NULL,
    celda_id bigint NOT NULL,
    entrada timestamp with time zone DEFAULT now() NOT NULL,
    salida timestamp with time zone,
    operador_entrada_id bigint NOT NULL,
    operador_salida_id bigint,
    CONSTRAINT ck_estancia_cierre_completo CHECK (((salida IS NULL) = (operador_salida_id IS NULL))),
    CONSTRAINT ck_estancia_orden_fechas CHECK ((salida >= entrada))
);


ALTER TABLE public.estancia OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 24694)
-- Name: estancia_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.estancia ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.estancia_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 228 (class 1259 OID 24695)
-- Name: horarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.horarios (
    id bigint NOT NULL,
    nombre text NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL,
    CONSTRAINT chk_8_horas CHECK ((((hora_fin - hora_inicio) = '08:00:00'::interval) OR ((hora_fin - hora_inicio) = '-16:00:00'::interval)))
);


ALTER TABLE public.horarios OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 24705)
-- Name: horarios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.horarios ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.horarios_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 241 (class 1259 OID 32982)
-- Name: mensualidad; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mensualidad (
    id_mensualidad integer NOT NULL,
    estado character varying(15) NOT NULL,
    id_vehiculo integer NOT NULL,
    CONSTRAINT mensualidad_estado_check CHECK (((estado)::text = ANY ((ARRAY['activo'::character varying, 'desactivado'::character varying])::text[])))
);


ALTER TABLE public.mensualidad OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 24706)
-- Name: novedad; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.novedad (
    descripcion text NOT NULL,
    fecha timestamp with time zone DEFAULT now() NOT NULL,
    vehiculo_id bigint,
    id bigint NOT NULL,
    CONSTRAINT ck_novedad_descripcion_no_vacio CHECK ((descripcion ~ '[^[:space:]]'::text))
);


ALTER TABLE public.novedad OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 33033)
-- Name: novedad_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.novedad ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.novedad_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 231 (class 1259 OID 24717)
-- Name: operador; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.operador (
    id bigint NOT NULL,
    nombre text NOT NULL,
    telefono text NOT NULL,
    direccion text,
    documento text,
    CONSTRAINT ck_operador_nombre_no_vacio CHECK ((nombre ~ '[^[:space:]]'::text)),
    CONSTRAINT ck_operador_telefono_no_vacio CHECK ((telefono ~ '[^[:space:]]'::text))
);


ALTER TABLE public.operador OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 24727)
-- Name: operador_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.operador ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.operador_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 233 (class 1259 OID 24728)
-- Name: pago; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pago (
    id bigint NOT NULL,
    valor numeric(10,2) NOT NULL,
    fecha timestamp with time zone DEFAULT now() NOT NULL,
    periodo text NOT NULL,
    CONSTRAINT ck_pago_periodo_no_vacio CHECK ((periodo ~ '[^[:space:]]'::text)),
    CONSTRAINT ck_pago_valor_positivo CHECK ((valor > (0)::numeric))
);


ALTER TABLE public.pago OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 24740)
-- Name: pago_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.pago ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.pago_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 235 (class 1259 OID 24741)
-- Name: turnos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.turnos (
    id bigint NOT NULL,
    operador_id bigint CONSTRAINT turnos_empleado_id_not_null NOT NULL,
    horario_id bigint NOT NULL,
    fecha date NOT NULL
);


ALTER TABLE public.turnos OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 24748)
-- Name: turnos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.turnos ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.turnos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 237 (class 1259 OID 24749)
-- Name: usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario (
    id bigint NOT NULL,
    nombre text NOT NULL,
    documento text NOT NULL,
    telefono text NOT NULL,
    fecha_vencimiento date NOT NULL,
    rol text DEFAULT 'EMPLEADO'::text NOT NULL,
    turno text DEFAULT 'MAÑANA'::text NOT NULL,
    horas_semana integer DEFAULT 42 NOT NULL,
    ausentismo_horas integer DEFAULT 0 NOT NULL,
    CONSTRAINT ck_usuario_ausentismo_horas_valida CHECK (((ausentismo_horas >= 0) AND (ausentismo_horas <= 84))),
    CONSTRAINT ck_usuario_documento_no_vacio CHECK ((documento ~ '[^[:space:]]'::text)),
    CONSTRAINT ck_usuario_horas_semana_valida CHECK (((horas_semana >= 1) AND (horas_semana <= 84))),
    CONSTRAINT ck_usuario_nombre_no_vacio CHECK ((nombre ~ '[^[:space:]]'::text)),
    CONSTRAINT ck_usuario_rol_valido CHECK ((rol = ANY (ARRAY['ADMINISTRADOR'::text, 'EMPLEADO'::text]))),
    CONSTRAINT ck_usuario_telefono_no_vacio CHECK ((telefono ~ '[^[:space:]]'::text)),
    CONSTRAINT ck_usuario_turno_valido CHECK ((turno = ANY (ARRAY['MAÑANA'::text, 'TARDE'::text, 'NOCHE'::text, 'RESPALDO'::text])))
);


ALTER TABLE public.usuario OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 24770)
-- Name: usuario_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.usuario ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.usuario_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 239 (class 1259 OID 24771)
-- Name: vehiculo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vehiculo (
    id bigint NOT NULL,
    placa text NOT NULL,
    color text NOT NULL,
    modelo integer NOT NULL,
    marca text NOT NULL,
    tipo text NOT NULL,
    celda_id bigint,
    CONSTRAINT ck_vehiculo_color_no_vacio CHECK ((color ~ '[^[:space:]]'::text)),
    CONSTRAINT ck_vehiculo_marca_no_vacia CHECK ((marca ~ '[^[:space:]]'::text)),
    CONSTRAINT ck_vehiculo_modelo_anio CHECK (((modelo >= 1) AND (modelo <= 9999))),
    CONSTRAINT ck_vehiculo_placa_no_vacia CHECK ((placa ~ '[^[:space:]]'::text)),
    CONSTRAINT ck_vehiculo_placa_normalizada CHECK ((placa = upper(regexp_replace(placa, '^[[:space:]]+|[[:space:]]+$'::text, ''::text, 'g'::text)))),
    CONSTRAINT ck_vehiculo_tipo CHECK ((tipo = ANY (ARRAY['MOTO'::text, 'AUTOMOVIL'::text, 'CAMIONETA'::text, 'FURGON'::text, 'CAMION'::text, 'OTROS'::text])))
);


ALTER TABLE public.vehiculo OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 24788)
-- Name: vehiculo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.vehiculo ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.vehiculo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 4916 (class 2604 OID 24789)
-- Name: cuenta id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cuenta ALTER COLUMN id SET DEFAULT nextval('public.cuenta_id_seq'::regclass);


--
-- TOC entry 5150 (class 0 OID 24646)
-- Dependencies: 219
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
novedad_id_identity
\.


--
-- TOC entry 5151 (class 0 OID 24650)
-- Dependencies: 220
-- Data for Name: ausencias; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ausencias (id, turno_id, motivo, reemplazo_id, observacion, registrado_en) FROM stdin;
\.


--
-- TOC entry 5153 (class 0 OID 24661)
-- Dependencies: 222
-- Data for Name: celda; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.celda (id, codigo, tipo) FROM stdin;
143	63	MOTO
18	01	CAMION
19	02	CAMION
20	03	CAMION
21	05	CAMION
22	04	CAMION
24	06	CAMION
27	07	CAMION
28	09	FURGON
29	08	FURGON
31	11	FURGON
33	12	FURGON
34	13	FURGON
35	14	FURGON
36	15	FURGON
37	16	CAMIONETA
38	17	CAMIONETA
39	18	CAMIONETA
40	19	CAMIONETA
41	20	CAMIONETA
30	10	FURGON
42	22	CAMIONETA
43	21	CAMIONETA
44	25	CAMIONETA
45	26	CAMIONETA
46	24	CAMIONETA
47	28	CAMIONETA
48	23	CAMIONETA
49	27	CAMIONETA
50	29	CAMIONETA
51	31	AUTOMOVIL
52	33	AUTOMOVIL
53	32	AUTOMOVIL
54	34	AUTOMOVIL
55	30	CAMIONETA
56	38	AUTOMOVIL
57	39	AUTOMOVIL
58	40	AUTOMOVIL
59	36	AUTOMOVIL
60	37	AUTOMOVIL
61	35	AUTOMOVIL
62	42	AUTOMOVIL
64	45	AUTOMOVIL
63	41	AUTOMOVIL
65	44	AUTOMOVIL
66	43	AUTOMOVIL
67	46	AUTOMOVIL
68	49	AUTOMOVIL
69	47	AUTOMOVIL
70	48	AUTOMOVIL
71	50	AUTOMOVIL
132	51	AUTOMOVIL
133	53	AUTOMOVIL
134	52	AUTOMOVIL
135	54	AUTOMOVIL
136	55	AUTOMOVIL
137	56	AUTOMOVIL
138	58	AUTOMOVIL
139	57	AUTOMOVIL
141	60	AUTOMOVIL
140	59	AUTOMOVIL
142	61	MOTO
144	64	MOTO
145	65	MOTO
146	66	MOTO
147	67	MOTO
148	62	MOTO
149	69	MOTO
150	68	MOTO
151	70	MOTO
152	72	MOTO
154	74	MOTO
155	75	MOTO
156	77	MOTO
157	76	MOTO
158	78	MOTO
159	73	MOTO
160	79	MOTO
161	80	MOTO
162	81	CARRO
\.


--
-- TOC entry 5155 (class 0 OID 24673)
-- Dependencies: 224
-- Data for Name: cuenta; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cuenta (id, usuario, password_hash, rol, operador_id) FROM stdin;
\.


--
-- TOC entry 5157 (class 0 OID 24683)
-- Dependencies: 226
-- Data for Name: estancia; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.estancia (id, vehiculo_id, celda_id, entrada, salida, operador_entrada_id, operador_salida_id) FROM stdin;
8	16	30	2026-10-31 20:34:41.823479-05	2026-10-31 20:35:22.215363-05	12	13
9	16	18	2026-11-01 18:43:14.881214-05	2026-11-01 18:43:43.279354-05	11	11
10	16	20	2026-11-01 19:13:36.261406-05	2026-11-01 19:21:12.969839-05	11	12
11	35	35	2026-11-03 23:45:04.711653-05	\N	11	\N
12	15	41	2026-11-04 00:06:51.117176-05	\N	12	\N
13	91	40	2026-11-04 10:34:26.392464-05	\N	11	\N
14	30	42	2026-11-08 16:01:37.877358-05	\N	13	\N
15	21	34	2026-11-08 16:01:55.583-05	\N	13	\N
16	19	22	2026-11-08 16:04:18.963031-05	\N	13	\N
17	23	45	2026-11-08 16:10:15.857634-05	\N	13	\N
18	52	18	2026-11-08 16:22:20.954805-05	\N	14	\N
19	18	44	2026-11-08 18:19:38.866988-05	\N	12	\N
\.


--
-- TOC entry 5159 (class 0 OID 24695)
-- Dependencies: 228
-- Data for Name: horarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.horarios (id, nombre, hora_inicio, hora_fin) FROM stdin;
1	Mañana	06:00:00	14:00:00
2	Tarde	14:00:00	22:00:00
3	Noche	22:00:00	06:00:00
\.


--
-- TOC entry 5172 (class 0 OID 32982)
-- Dependencies: 241
-- Data for Name: mensualidad; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mensualidad (id_mensualidad, estado, id_vehiculo) FROM stdin;
1	activo	15
3	activo	16
2	activo	17
4	activo	18
5	activo	19
6	activo	20
7	activo	21
8	activo	22
9	activo	23
10	activo	24
\.


--
-- TOC entry 5161 (class 0 OID 24706)
-- Dependencies: 230
-- Data for Name: novedad; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.novedad (descripcion, fecha, vehiculo_id, id) FROM stdin;
puerta golpeada	2026-11-08 00:00:00-05	16	1
golpe en el stop	2026-11-08 18:25:53.532-05	32	2
\.


--
-- TOC entry 5162 (class 0 OID 24717)
-- Dependencies: 231
-- Data for Name: operador; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.operador (id, nombre, telefono, direccion, documento) FROM stdin;
11	Andres Mauricio Quintero Rios	3046509495	san nicolas	1040034902
12	Liliana Yaneth Carmona Montoya	3124755568	vereda fatima	1040038823
13	Thiago Alejandro Rios Lopes	3046508886	san calletano	1040052403
14	Jesús Antonio Arcila Rios	3124758641	la maria	1040034454
\.


--
-- TOC entry 5164 (class 0 OID 24728)
-- Dependencies: 233
-- Data for Name: pago; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pago (id, valor, fecha, periodo) FROM stdin;
\.


--
-- TOC entry 5166 (class 0 OID 24741)
-- Dependencies: 235
-- Data for Name: turnos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.turnos (id, operador_id, horario_id, fecha) FROM stdin;
5	12	1	2026-10-29
6	11	1	2026-10-29
8	13	2	2026-10-29
7	14	3	2026-10-29
\.


--
-- TOC entry 5168 (class 0 OID 24749)
-- Dependencies: 237
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuario (id, nombre, documento, telefono, fecha_vencimiento, rol, turno, horas_semana, ausentismo_horas) FROM stdin;
2	Administrador Principal	ADMIN-001	3001112222	2035-12-31	ADMINISTRADOR	RESPALDO	42	0
3	Andres Mauricio Quintero Rios	1040034902	3046509495	2026-11-01	ADMINISTRADOR	MAÑANA	42	0
4	Liliana Yaneth Carmona Montoya	1040038823	3124755500	2026-12-31	EMPLEADO	MAÑANA	42	0
5	Thiago Alejandro Rios Lopes	1040052403	3046508800	2026-12-31	EMPLEADO	MAÑANA	42	0
6	Jesús Antonio Arcila Rios	1040034454	3124758600	2026-12-31	EMPLEADO	MAÑANA	42	0
7	oscar rene Operario	1111111	310	2026-12-29	EMPLEADO	MAÑANA	42	0
\.


--
-- TOC entry 5170 (class 0 OID 24771)
-- Dependencies: 239
-- Data for Name: vehiculo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vehiculo (id, placa, color, modelo, marca, tipo, celda_id) FROM stdin;
85	RUI57N	rojo	2023	Hero	MOTO	\N
15	GBE137	amarillo	2012	Hino	CAMION	18
16	LUS174	amarillo	2016	Isuzu	CAMION	19
17	UPC211	plateado	2021	Foton	CAMION	20
18	TYQ248	amarillo	2013	International	CAMION	22
19	CDV285	rojo	2010	JAC	CAMION	21
20	NZG322	gris	2017	International	CAMION	24
21	SXG359	plateado	2025	Chevrolet	CAMION	27
22	UYP396	plateado	2023	Chevrolet	FURGON	29
23	FAO433	amarillo	2011	Foton	FURGON	28
24	VQH470	gris	2015	Chevrolet	FURGON	30
25	DKY507	rojo	2018	Chevrolet	FURGON	31
26	IDX544	blanco	2019	Foton	FURGON	33
27	LYF581	plateado	2020	Fiat	FURGON	34
28	CHE618	azul	2024	Fiat	FURGON	35
29	OOC655	azul	2019	Chevrolet	FURGON	36
30	DPV692	verde	2019	Nissan	CAMIONETA	37
31	GHP729	rojo	2011	Ford	CAMIONETA	38
32	YMZ766	azul	2014	Ford	CAMIONETA	39
33	ITJ803	verde	2019	Nissan	CAMIONETA	40
34	LHI840	verde	2022	Renault	CAMIONETA	41
35	NVD877	negro	2023	Mitsubishi	CAMIONETA	43
36	JIJ914	azul	2010	Toyota	CAMIONETA	42
37	VGN951	plateado	2019	Toyota	CAMIONETA	48
38	UYO988	amarillo	2011	Mitsubishi	CAMIONETA	46
39	KHM125	gris	2011	Chevrolet	CAMIONETA	44
40	XBX162	rojo	2020	Mitsubishi	CAMIONETA	45
41	RYK199	plateado	2010	Chevrolet	CAMIONETA	49
42	CWZ236	gris	2019	Chevrolet	CAMIONETA	47
43	EXP273	amarillo	2024	Nissan	CAMIONETA	50
44	POS310	gris	2021	Nissan	CAMIONETA	55
45	WGU347	verde	2020	Renault	AUTOMOVIL	51
46	ONX384	amarillo	2015	Kia	AUTOMOVIL	53
47	EDZ421	rojo	2014	Toyota	AUTOMOVIL	52
48	FVJ458	verde	2018	Chevrolet	AUTOMOVIL	54
49	HMQ495	gris	2010	Toyota	AUTOMOVIL	61
50	MXG532	verde	2025	Volkswagen	AUTOMOVIL	59
51	JFD569	blanco	2015	Volkswagen	AUTOMOVIL	60
52	CMY606	gris	2018	Mazda	AUTOMOVIL	56
53	DKU643	gris	2012	Volkswagen	AUTOMOVIL	57
54	RRD680	rojo	2020	Mazda	AUTOMOVIL	58
55	WNZ717	azul	2020	Mazda	AUTOMOVIL	63
56	FRT754	blanco	2010	Hyundai	AUTOMOVIL	62
57	JHX791	rojo	2025	Toyota	AUTOMOVIL	66
58	YZX828	blanco	2025	Volkswagen	AUTOMOVIL	65
59	QGS865	azul	2023	Chevrolet	AUTOMOVIL	64
60	ORZ902	negro	2016	Volkswagen	AUTOMOVIL	67
61	DRC939	azul	2024	Volkswagen	AUTOMOVIL	69
62	CFE976	plateado	2023	Renault	AUTOMOVIL	70
63	EJQ113	plateado	2022	Volkswagen	AUTOMOVIL	68
64	JGA150	amarillo	2023	Nissan	AUTOMOVIL	71
65	BHZ187	azul	2022	Renault	AUTOMOVIL	132
66	DKC224	verde	2024	Renault	AUTOMOVIL	134
67	ZRV261	gris	2020	Volkswagen	AUTOMOVIL	133
68	OOC298	blanco	2011	Volkswagen	AUTOMOVIL	135
69	XAS335	plateado	2024	Chevrolet	AUTOMOVIL	136
70	AOP372	plateado	2012	Chevrolet	AUTOMOVIL	137
71	DYW409	blanco	2013	Mazda	AUTOMOVIL	139
72	FWZ446	blanco	2021	Kia	AUTOMOVIL	138
73	BER483	azul	2018	Volkswagen	AUTOMOVIL	140
74	VBG520	negro	2014	Mazda	AUTOMOVIL	141
75	HCM77S	blanco	2012	Honda	MOTO	142
76	VLP84X	verde	2022	AKT	MOTO	148
77	DIN91C	azul	2021	KTM	MOTO	143
78	ZQB98I	gris	2024	Hero	MOTO	144
79	DKF15U	gris	2011	Suzuki	MOTO	145
80	WNX22O	blanco	2021	TVS	MOTO	146
81	SPT29I	azul	2013	Yamaha	MOTO	147
82	AFF36A	gris	2013	Suzuki	MOTO	150
83	ZAF43Y	amarillo	2024	TVS	MOTO	149
84	LVP50T	negro	2010	Yamaha	MOTO	151
86	OFL64U	blanco	2023	Bajaj	MOTO	152
87	JAZ71X	rojo	2022	KTM	MOTO	159
88	AJO78A	verde	2021	Honda	MOTO	154
89	FZJ85I	azul	2015	TVS	MOTO	155
90	HBD92A	amarillo	2017	Suzuki	MOTO	157
91	ANM99P	verde	2022	Yamaha	MOTO	156
92	QRI16C	amarillo	2013	Suzuki	MOTO	158
93	ILI23X	plateado	2019	Yamaha	MOTO	160
94	JWU30G	azul	2025	Honda	MOTO	161
\.


--
-- TOC entry 5193 (class 0 OID 0)
-- Dependencies: 221
-- Name: ausencias_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ausencias_id_seq', 2, true);


--
-- TOC entry 5194 (class 0 OID 0)
-- Dependencies: 223
-- Name: celda_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.celda_id_seq', 162, true);


--
-- TOC entry 5195 (class 0 OID 0)
-- Dependencies: 225
-- Name: cuenta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cuenta_id_seq', 1, false);


--
-- TOC entry 5196 (class 0 OID 0)
-- Dependencies: 227
-- Name: estancia_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.estancia_id_seq', 19, true);


--
-- TOC entry 5197 (class 0 OID 0)
-- Dependencies: 229
-- Name: horarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.horarios_id_seq', 3, true);


--
-- TOC entry 5198 (class 0 OID 0)
-- Dependencies: 242
-- Name: novedad_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.novedad_id_seq', 2, true);


--
-- TOC entry 5199 (class 0 OID 0)
-- Dependencies: 232
-- Name: operador_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.operador_id_seq', 14, true);


--
-- TOC entry 5200 (class 0 OID 0)
-- Dependencies: 234
-- Name: pago_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pago_id_seq', 1, true);


--
-- TOC entry 5201 (class 0 OID 0)
-- Dependencies: 236
-- Name: turnos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.turnos_id_seq', 8, true);


--
-- TOC entry 5202 (class 0 OID 0)
-- Dependencies: 238
-- Name: usuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuario_id_seq', 7, true);


--
-- TOC entry 5203 (class 0 OID 0)
-- Dependencies: 240
-- Name: vehiculo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vehiculo_id_seq', 94, true);


--
-- TOC entry 4950 (class 2606 OID 24791)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 4952 (class 2606 OID 24793)
-- Name: ausencias ausencias_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ausencias
    ADD CONSTRAINT ausencias_pkey PRIMARY KEY (id);


--
-- TOC entry 4954 (class 2606 OID 24795)
-- Name: ausencias ausencias_turno_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ausencias
    ADD CONSTRAINT ausencias_turno_id_key UNIQUE (turno_id);


--
-- TOC entry 4956 (class 2606 OID 24797)
-- Name: celda celda_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.celda
    ADD CONSTRAINT celda_pkey PRIMARY KEY (id);


--
-- TOC entry 4960 (class 2606 OID 24799)
-- Name: cuenta cuenta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cuenta
    ADD CONSTRAINT cuenta_pkey PRIMARY KEY (id);


--
-- TOC entry 4962 (class 2606 OID 24801)
-- Name: cuenta cuenta_usuario_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cuenta
    ADD CONSTRAINT cuenta_usuario_key UNIQUE (usuario);


--
-- TOC entry 4964 (class 2606 OID 24803)
-- Name: estancia estancia_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estancia
    ADD CONSTRAINT estancia_pkey PRIMARY KEY (id);


--
-- TOC entry 4969 (class 2606 OID 24805)
-- Name: horarios horarios_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.horarios
    ADD CONSTRAINT horarios_nombre_key UNIQUE (nombre);


--
-- TOC entry 4971 (class 2606 OID 24807)
-- Name: horarios horarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.horarios
    ADD CONSTRAINT horarios_pkey PRIMARY KEY (id);


--
-- TOC entry 4989 (class 2606 OID 32990)
-- Name: mensualidad mensualidad_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mensualidad
    ADD CONSTRAINT mensualidad_pkey PRIMARY KEY (id_mensualidad);


--
-- TOC entry 4973 (class 2606 OID 24811)
-- Name: operador operador_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.operador
    ADD CONSTRAINT operador_pkey PRIMARY KEY (id);


--
-- TOC entry 4975 (class 2606 OID 24813)
-- Name: pago pago_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pago
    ADD CONSTRAINT pago_pkey PRIMARY KEY (id);


--
-- TOC entry 4977 (class 2606 OID 24815)
-- Name: turnos turnos_empleado_id_fecha_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.turnos
    ADD CONSTRAINT turnos_empleado_id_fecha_key UNIQUE (operador_id, fecha);


--
-- TOC entry 4979 (class 2606 OID 24817)
-- Name: turnos turnos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.turnos
    ADD CONSTRAINT turnos_pkey PRIMARY KEY (id);


--
-- TOC entry 4958 (class 2606 OID 24819)
-- Name: celda uq_celda_codigo; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.celda
    ADD CONSTRAINT uq_celda_codigo UNIQUE (codigo);


--
-- TOC entry 4981 (class 2606 OID 24821)
-- Name: usuario uq_usuario_documento; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT uq_usuario_documento UNIQUE (documento);


--
-- TOC entry 4985 (class 2606 OID 24823)
-- Name: vehiculo uq_vehiculo_placa; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT uq_vehiculo_placa UNIQUE (placa);


--
-- TOC entry 4983 (class 2606 OID 24825)
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id);


--
-- TOC entry 4987 (class 2606 OID 24827)
-- Name: vehiculo vehiculo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_pkey PRIMARY KEY (id);


--
-- TOC entry 4965 (class 1259 OID 24828)
-- Name: ix_estancia_vehiculo_entrada; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_estancia_vehiculo_entrada ON public.estancia USING btree (vehiculo_id, entrada);


--
-- TOC entry 4966 (class 1259 OID 24829)
-- Name: uq_estancia_celda_abierta; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_estancia_celda_abierta ON public.estancia USING btree (celda_id) WHERE (salida IS NULL);


--
-- TOC entry 4967 (class 1259 OID 24830)
-- Name: uq_estancia_vehiculo_abierta; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_estancia_vehiculo_abierta ON public.estancia USING btree (vehiculo_id) WHERE (salida IS NULL);


--
-- TOC entry 4990 (class 2606 OID 24831)
-- Name: ausencias ausencias_reemplazo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ausencias
    ADD CONSTRAINT ausencias_reemplazo_id_fkey FOREIGN KEY (reemplazo_id) REFERENCES public.operador(id);


--
-- TOC entry 4991 (class 2606 OID 24836)
-- Name: ausencias ausencias_turno_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ausencias
    ADD CONSTRAINT ausencias_turno_id_fkey FOREIGN KEY (turno_id) REFERENCES public.turnos(id);


--
-- TOC entry 4992 (class 2606 OID 24841)
-- Name: cuenta cuenta_operador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cuenta
    ADD CONSTRAINT cuenta_operador_id_fkey FOREIGN KEY (operador_id) REFERENCES public.operador(id) ON DELETE CASCADE;


--
-- TOC entry 4993 (class 2606 OID 24846)
-- Name: estancia fk_estancia_celda; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estancia
    ADD CONSTRAINT fk_estancia_celda FOREIGN KEY (celda_id) REFERENCES public.celda(id) ON DELETE RESTRICT;


--
-- TOC entry 4994 (class 2606 OID 24851)
-- Name: estancia fk_estancia_operador_entrada; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estancia
    ADD CONSTRAINT fk_estancia_operador_entrada FOREIGN KEY (operador_entrada_id) REFERENCES public.operador(id) ON DELETE RESTRICT;


--
-- TOC entry 4995 (class 2606 OID 24856)
-- Name: estancia fk_estancia_operador_salida; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estancia
    ADD CONSTRAINT fk_estancia_operador_salida FOREIGN KEY (operador_salida_id) REFERENCES public.operador(id) ON DELETE RESTRICT;


--
-- TOC entry 4996 (class 2606 OID 24861)
-- Name: estancia fk_estancia_vehiculo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estancia
    ADD CONSTRAINT fk_estancia_vehiculo FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculo(id) ON DELETE RESTRICT;


--
-- TOC entry 5001 (class 2606 OID 32997)
-- Name: mensualidad fk_id_vehiculo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mensualidad
    ADD CONSTRAINT fk_id_vehiculo FOREIGN KEY (id_vehiculo) REFERENCES public.vehiculo(id);


--
-- TOC entry 4997 (class 2606 OID 33028)
-- Name: novedad fk_novedad_vehiculo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.novedad
    ADD CONSTRAINT fk_novedad_vehiculo FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculo(id) ON DELETE SET NULL;


--
-- TOC entry 5000 (class 2606 OID 24866)
-- Name: vehiculo fk_vehiculo_celda; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT fk_vehiculo_celda FOREIGN KEY (celda_id) REFERENCES public.celda(id) ON DELETE SET NULL;


--
-- TOC entry 5002 (class 2606 OID 32991)
-- Name: mensualidad mensualidad_id_vehiculo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mensualidad
    ADD CONSTRAINT mensualidad_id_vehiculo_fkey FOREIGN KEY (id_vehiculo) REFERENCES public.vehiculo(id);


--
-- TOC entry 4998 (class 2606 OID 24871)
-- Name: turnos turnos_horario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.turnos
    ADD CONSTRAINT turnos_horario_id_fkey FOREIGN KEY (horario_id) REFERENCES public.horarios(id);


--
-- TOC entry 4999 (class 2606 OID 24876)
-- Name: turnos turnos_operador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.turnos
    ADD CONSTRAINT turnos_operador_id_fkey FOREIGN KEY (operador_id) REFERENCES public.operador(id);


--
-- TOC entry 5179 (class 0 OID 0)
-- Dependencies: 219
-- Name: TABLE alembic_version; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE public.alembic_version FROM postgres;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE public.alembic_version TO postgres;
GRANT SELECT ON TABLE public.alembic_version TO postgres WITH GRANT OPTION;


--
-- TOC entry 5180 (class 0 OID 0)
-- Dependencies: 220
-- Name: TABLE ausencias; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE public.ausencias FROM postgres;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE public.ausencias TO postgres;
GRANT SELECT ON TABLE public.ausencias TO postgres WITH GRANT OPTION;


--
-- TOC entry 5181 (class 0 OID 0)
-- Dependencies: 222
-- Name: TABLE celda; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE public.celda FROM postgres;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE public.celda TO postgres;
GRANT SELECT ON TABLE public.celda TO postgres WITH GRANT OPTION;


--
-- TOC entry 5182 (class 0 OID 0)
-- Dependencies: 224
-- Name: TABLE cuenta; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE public.cuenta FROM postgres;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE public.cuenta TO postgres;
GRANT SELECT ON TABLE public.cuenta TO postgres WITH GRANT OPTION;


--
-- TOC entry 5184 (class 0 OID 0)
-- Dependencies: 226
-- Name: TABLE estancia; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE public.estancia FROM postgres;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE public.estancia TO postgres;
GRANT SELECT ON TABLE public.estancia TO postgres WITH GRANT OPTION;


--
-- TOC entry 5185 (class 0 OID 0)
-- Dependencies: 228
-- Name: TABLE horarios; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE public.horarios FROM postgres;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE public.horarios TO postgres;
GRANT SELECT ON TABLE public.horarios TO postgres WITH GRANT OPTION;


--
-- TOC entry 5186 (class 0 OID 0)
-- Dependencies: 241
-- Name: TABLE mensualidad; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE public.mensualidad FROM postgres;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE public.mensualidad TO postgres;
GRANT SELECT ON TABLE public.mensualidad TO postgres WITH GRANT OPTION;


--
-- TOC entry 5187 (class 0 OID 0)
-- Dependencies: 230
-- Name: TABLE novedad; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE public.novedad FROM postgres;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE public.novedad TO postgres;
GRANT SELECT ON TABLE public.novedad TO postgres WITH GRANT OPTION;


--
-- TOC entry 5188 (class 0 OID 0)
-- Dependencies: 231
-- Name: TABLE operador; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE public.operador FROM postgres;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE public.operador TO postgres;
GRANT SELECT ON TABLE public.operador TO postgres WITH GRANT OPTION;


--
-- TOC entry 5189 (class 0 OID 0)
-- Dependencies: 233
-- Name: TABLE pago; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE public.pago FROM postgres;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE public.pago TO postgres;
GRANT SELECT ON TABLE public.pago TO postgres WITH GRANT OPTION;


--
-- TOC entry 5190 (class 0 OID 0)
-- Dependencies: 235
-- Name: TABLE turnos; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE public.turnos FROM postgres;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE public.turnos TO postgres;
GRANT SELECT ON TABLE public.turnos TO postgres WITH GRANT OPTION;


--
-- TOC entry 5191 (class 0 OID 0)
-- Dependencies: 237
-- Name: TABLE usuario; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE public.usuario FROM postgres;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE public.usuario TO postgres;
GRANT SELECT ON TABLE public.usuario TO postgres WITH GRANT OPTION;


--
-- TOC entry 5192 (class 0 OID 0)
-- Dependencies: 239
-- Name: TABLE vehiculo; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE public.vehiculo FROM postgres;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE public.vehiculo TO postgres;
GRANT SELECT ON TABLE public.vehiculo TO postgres WITH GRANT OPTION;


--
-- TOC entry 2110 (class 826 OID 24881)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres REVOKE ALL ON TABLES FROM postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT SELECT ON TABLES TO postgres WITH GRANT OPTION;


-- Completed on 2026-11-08 19:16:36

--
-- PostgreSQL database dump complete
--

\unrestrict imxfsh2rzGqHZnvS37nCQ7efzigdl7H0ZwctriyGDdoT7Gnt90HYoa0m8bnC6Ld

