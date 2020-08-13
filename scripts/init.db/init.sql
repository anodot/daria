-- todo source types are enum

CREATE TABLE sources (
    id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    type VARCHAR(20) NOT NULL,
    config JSON NOT NULL
);

CREATE TABLE pipelines (
    id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    source_id INT NOT NULL,
    config JSON NOT NULL,
    CONSTRAINT fk_source
      FOREIGN KEY(source_id)
	  REFERENCES sources(id)
);
