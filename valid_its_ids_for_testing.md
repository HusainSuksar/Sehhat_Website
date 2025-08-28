# Valid ITS IDs for Testing

The system now uses **database-driven ITS validation**. Only ITS IDs that exist in the database (generated via `generate_mock_data_enhanced.py`) are valid.

## How to Get Valid ITS IDs:

### 1. **Check Database for Existing Users**
```python
# Run this in Django shell to see available ITS IDs
python manage.py shell
>>> from accounts.models import User
>>> users = User.objects.all().values_list('its_id', 'role', 'first_name', 'last_name')
>>> for its_id, role, first, last in users:
...     print(f"{its_id} - {role} - {first} {last}")
```

### 2. **Expected ITS ID Ranges** (from enhanced mock data generator):
- **Admin**: `10000001` and up
- **Aamil**: `10000002` and up  
- **Moze Coordinators**: `10000102` and up
- **Doctors**: `10000202` and up
- **Students**: `10000252` and up
- **Patients**: `10000452` and up

### 3. **Generate More Mock Data**
```bash
# Run the enhanced mock data generator to create more users
python generate_mock_data_enhanced.py
```

## How the validation works:
1. **Must be exactly 8 digits**
2. **Must be in range 10000000-99999999**
3. **Must exist in the User table** - No arbitrary ITS IDs are accepted
4. **Database lookup** - The system fetches user data directly from the database

## Benefits:
- ✅ **Realistic testing** - Only actual users can login
- ✅ **No random ITS IDs** - Prevents fake data
- ✅ **Consistent data** - User data comes from your generated mock data
- ✅ **Role-based testing** - Each ITS ID has a specific role (admin, doctor, patient, etc.)

## Quick Test ITS IDs:
If you've run the enhanced mock data generator, try these likely ITS IDs:
- `10000001` (Admin)
- `10000002` (Aamil) 
- `10000102` (Moze Coordinator)
- `10000202` (Doctor)
- `10000252` (Student)
- `10000452` (Patient)