# Run the migration
python migration.py

# The script will:
# 1. Backup your existing data
# 2. Transform it to the new schema
# 3. Create a new table
# 4. Verify everything worked
# 5. Rollback automatically if anything fails