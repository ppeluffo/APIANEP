-- Table: public.datos

-- DROP TABLE IF EXISTS public.control_acceso;

CREATE TABLE IF NOT EXISTS public.control_acceso
(
    id bigint NOT NULL GENERATED BY DEFAULT AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    access_token character varying(50) COLLATE pg_catalog."default" NOT NULL,
    last_row bigint NOT NULL,
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.control_acceso
    OWNER to admin;
-- Index: control_acceso_idx

