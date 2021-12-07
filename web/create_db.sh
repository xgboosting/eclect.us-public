
read -p "Are you sure? I'm about to drop the existing database. Type Y or y: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    psql -Upostgres -c "DROP DATABASE eclectus"
    psql -Upostgres -c "CREATE DATABASE eclectus"
    psql -Upostgres -c "CREATE USER eclectus WITH PASSWORD 'eclectus'"
    psql -Upostgres -c "GRANT ALL PRIVILEGES ON DATABASE eclectus to eclectus"
fi
