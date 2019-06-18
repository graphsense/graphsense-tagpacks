DROP KEYSPACE IF EXISTS crawler_tags;
CREATE KEYSPACE crawler_tags WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1 };

// USE graphsense_raw;
USE crawler_tags;

CREATE TABLE tag (
    address text,
    tag text,
    tag_uri text,
    description text,
    actor_category text,
    source text,
    source_uri text,
    timestamp int,
    PRIMARY KEY (address, tag, source)
);
