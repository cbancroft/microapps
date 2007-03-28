alter table document add column vectors tsvector;
create index body_index on document using gist(vectors);
update document set vectors = to_tsvector(body);
