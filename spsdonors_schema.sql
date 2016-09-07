drop table if exists spsdonors;
create table spsdonors (
  id integer primary key autoincrement,
  donorname text not null,
  donorclassification text not null,
  solicitorname text not null,
  solicitoremail text not null,
  solicitorphone text not null
);

