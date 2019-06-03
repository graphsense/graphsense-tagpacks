DROP KEYSPACE IF EXISTS tagpacks;

CREATE KEYSPACE tagpacks WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3 };

USE tagpacks;


CREATE TABLE tagpack_by_uri (
    uri             text PRIMARY KEY,
    title           text,
    description     text,
    creator         text
);


CREATE TABLE tag_by_address (
    address         text,
    label           text,
    source          text,
    tagpack_uri     text,
    currency        text,
    lastmod         text,
    category        text,
    PRIMARY KEY (address, label, source, tagpack_uri)
);