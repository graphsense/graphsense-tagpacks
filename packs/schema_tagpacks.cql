DROP KEYSPACE IF EXISTS tagpacks;

CREATE KEYSPACE tagpacks WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1 };

USE tagpacks;


CREATE TABLE tagpack_by_uri (
    uri				text PRIMARY KEY,
    title  			text,
    creator			text
);


CREATE TABLE tag_by_label (
	label_prefix	text,
	label 			text,
	address			text,
	source			text,
	tagpack_uri		text,
	currency		text,
	lastmod			int,
	PRIMARY KEY (label_prefix, label, address, source, tagpack_uri)
);