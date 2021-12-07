#!/bin/bash

read -p "Are you sure? I'm about to drop the existing database. Type Y or y: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    psql -Ueclectus -c "drop schema public cascade;"
    psql -Ueclectus -c "create schema public;"
    psql -Ueclectus -c "CREATE SCHEMA public AUTHORIZATION eclectus;"
    psql -Ueclectus -c "GRANT ALL ON SCHEMA public TO eclectus;"
    psql -Ueclectus -c "GRANT ALL ON SCHEMA public TO public;"
    psql -Ueclectus -c "COMMENT ON SCHEMA public IS 'standard public schema';"
fi

