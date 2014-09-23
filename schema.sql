drop table if exists games;
create table games (
  id integer primary key autoincrement,
  author varchar(50) not null, 
  source varchar(200) not null, 
  'year' integer null, 
  pdn text not null
);

drop table if exists distances;
create table distances (
  id integer primary key autoincrement,
  game1pdn text not null,
  game2pdn text not null,
  distance integer not null
);