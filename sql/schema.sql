CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255),
    headline TEXT,
    company VARCHAR(255),
    school VARCHAR(255),
    mutual_group VARCHAR(255),
    profile_url VARCHAR(255) UNIQUE,
    email VARCHAR(255),
    last_contact TIMESTAMP,
    status VARCHAR(50)
);