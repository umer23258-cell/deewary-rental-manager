DROP TABLE IF EXISTS house_inventory, client_leads, visit_logs;

CREATE TABLE house_inventory (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    owner_name TEXT,
    contact TEXT,
    location TEXT,
    rent NUMERIC DEFAULT 0,
    marla TEXT,
    floor TEXT,
    beds INTEGER DEFAULT 1,
    water TEXT,       
    gas TEXT,         
    electricity TEXT, 
    status TEXT DEFAULT 'Available',
    added_by TEXT
);

CREATE TABLE client_leads (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    name TEXT,
    contact TEXT,
    budget NUMERIC DEFAULT 0,
    marla TEXT,
    beds INTEGER DEFAULT 1,
    area TEXT,
    portion TEXT,
    added_by TEXT
);

CREATE TABLE visit_logs (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date DATE DEFAULT CURRENT_DATE,
    client TEXT,
    house TEXT,
    staff TEXT,
    feedback TEXT
);

ALTER TABLE house_inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE client_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE visit_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all" ON house_inventory FOR ALL USING (true);
CREATE POLICY "Allow all" ON client_leads FOR ALL USING (true);
CREATE POLICY "Allow all" ON visit_logs FOR ALL USING (true);
