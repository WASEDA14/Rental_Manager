
CREATE TABLE IF NOT EXISTS room (
    room_no             TEXT NOT NULL PRIMARY KEY,
    area_m2             INTEGER,
    floor               INTEGER,
    base_rent INTEGER,
    electric_unit_price INTEGER ,
    water_unit_price    INTEGER ,
    status              TEXT NOT NULL DEFAULT 0
             CHECK (status  IN (0, 1)),
    note                TEXT,
    is_deleted          INTEGER NOT NULL DEFAULT 0
        CHECK (is_deleted IN (0, 1))
);


CREATE TABLE IF NOT EXISTS tenant (
    tenant_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name   TEXT    NOT NULL,
   sex         INTEGER
        CHECK (sex IN (0, 1, 2)),
    phone       TEXT,
    id_number   INTEGER NOT NULL,
    address     TEXT,
    birth       TEXT,
    email       TEXT,
    room_no     TEXT,
    move_in     TEXT,
    move_out    TEXT,
    note        TEXT,
    is_deleted      INTEGER NOT NULL DEFAULT 1
        CHECK (is_deleted IN (0, 1)),
    FOREIGN KEY (room_no) REFERENCES room(room_no)
);

CREATE TABLE IF NOT EXISTS contract (
    contract_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    room_no            TEXT    NOT NULL,
    tenant_id          INTEGER NOT NULL,
    start_ymd          TEXT    NOT NULL,
    end_ymd            TEXT,
    rent_amount        INTEGER NOT NULL,
    deposit_amount     INTEGER,
    electric_meter_start INTEGER,
    water_meter_start  INTEGER,
    contract_status    INTEGER NOT NULL DEFAULT 0
        CHECK (contract_status IN (0, 1, 2)),
    deposit_ymd        TEXT,
    note               TEXT,
    contract_name      TEXT,
    is_deleted         INTEGER NOT NULL DEFAULT 0
        CHECK (is_deleted IN (0, 1)),
    FOREIGN KEY (room_no)   REFERENCES room(room_no),
    FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id)
);


CREATE TABLE IF NOT EXISTS bill (
    bill_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id        INTEGER NOT NULL,
    tenant_name TEXT NOT NULL,
    room_no           TEXT NOT NULL,
    bill_month         TEXT    NOT NULL,
    elec_prev          INTEGER,
    elec_current       INTEGER,
    water_prev         INTEGER,
    water_current      INTEGER,
    water_unit_price   INTEGER,
    electric_unit_price INTEGER,
    room_rent_amount   INTEGER,
    other_fee          INTEGER,
    total_amount       INTEGER,
    paid_amount        INTEGER,
    paid_status        INTEGER NOT NULL DEFAULT 0
        CHECK (paid_status IN (0, 1, 2)),
        --  0=Chưa trả, 1=Trả một phần, 2=Đã trả đủ
    paid_ymd           TEXT,
    pdf_path           TEXT,
    note               TEXT,
    invoice_name       TEXT,
    is_deleted         INTEGER NOT NULL DEFAULT 0
        CHECK (is_deleted IN (0, 1)),
    FOREIGN KEY (contract_id) REFERENCES contract(contract_id),
    FOREIGN KEY (room_no) REFERENCES room(room_no)
);

CREATE TABLE IF NOT EXISTS user (
    login_id       TEXT PRIMARY KEY,
    login_password TEXT NOT NULL,
    user_name      TEXT NOT NULL,
    email          TEXT
);

