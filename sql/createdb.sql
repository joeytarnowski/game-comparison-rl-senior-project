use GameRL;

create table Game(
	id int unsigned auto_increment,
	gametype_id int unsigned not null,
    player_token varchar(40) not null,
    game_datetime datetime,
    primary key(id),
    foreign key(gametype_id) references GameType(id)
);

create table GameMove(
	id int unsigned auto_increment,
	game_id int unsigned not null,
    boardstate varchar(42) not null,
    movecount int unsigned not null,
    move_datetime datetime,
    primary key(id),
    foreign key(game_id) references Game(id)
);

create table GameType(
	id int unsigned auto_increment,
    name varchar(20) not null,
    primary key(id)
);
    
create table Agent(
	id int unsigned auto_increment,
    name varchar(20) not null,
    gametype_id int unsigned not null,
    primary key(id),
    foreign key(gametype_id) references GameType(id)
);

create table QValue(
	id int unsigned auto_increment,
    agent_id int unsigned not null,
    boardstate varchar(42) not null,
    action varchar(20) not null,
    value float default 0.0,
    primary key(id),
    foreign key(agent_id) references Agent(id)
);
    