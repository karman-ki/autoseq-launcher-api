CREATE USER referral_writer WITH ENCRYPTED PASSWORD 'ProbioWriter';
CREATE DATABASE autoseq_launcher;
GRANT ALL PRIVILEGES ON DATABASE autoseq_launcher TO referral_writer;

CREATE TYPE project_status AS ENUM ('0','1', '2', '-1');
CREATE TYPE job_status AS ENUM ('0','1', '2', '-1');
CREATE TYPE barcode_status AS ENUM ('0','1');

CREATE TABLE barcodes_t
  (
     b_id          SERIAL PRIMARY KEY,
     project_name  VARCHAR(100),
     search_pattern   VARCHAR(100),
     barcode_path    TEXT,
     config_path    TEXT,
     bar_status  barcode_status,
     create_time TIMESTAMP,
     update_time TIMESTAMP
  ); 

CREATE TABLE projects_t
  (
     p_id          SERIAL PRIMARY KEY,
     barcode_id  SERIAL REFERENCES barcodes_t (b_id),
     sample_id   VARCHAR(100),
     cfdna   TEXT,
     normal   TEXT,
     tumor   TEXT,
     config_path TEXT,
     pro_status         project_status,
     cores   VARCHAR(100),
     machine_type   VARCHAR(100),
     create_time TIMESTAMP,
     update_time TIMESTAMP
  ); 


  CREATE TABLE jobs_t
  (
     job_id          SERIAL PRIMARY KEY,
     project_id  SERIAL REFERENCES projects_t (p_id),
     cores   VARCHAR(100),
     machine_type   VARCHAR(100),
     pipeline_cmd TEXT,
     log_path TEXT,
     json_path TEXT,
     job_status         job_status,
     create_time TIMESTAMP,
     update_time TIMESTAMP
  ); 