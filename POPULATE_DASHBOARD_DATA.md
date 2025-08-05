# 📊 **FIX DASHBOARD STATISTICS ON PYTHONANYWHERE**

## 🚨 **PROBLEM:**
Dashboard shows `"--"` instead of numbers because the PythonAnywhere MySQL database doesn't have sample data.

## ✅ **SOLUTION:**

### **Step 1: Setup Environment (First Time Only)**
```bash
cd ~/umoor_sehhat
cp .env.pythonanywhere.example .env
nano .env  # Update with your MySQL password and username
```

### **Step 2: Quick Fix (Recommended)**
Run this single command in your PythonAnywhere Bash console:

```bash
cd ~/umoor_sehhat
python3.10 check_and_populate_data.py
```

This will:
- ✅ Check your current database status
- ✅ Create minimal sample data if missing
- ✅ Show before/after statistics

### **Step 3: Full Sample Data (Optional)**
If you want comprehensive test data instead of minimal:

```bash
cd ~/umoor_sehhat
python3.10 create_sample_data.py
```

## 🎯 **EXPECTED RESULT:**

After running either script, your dashboard will show:

- **✅ Total Users**: 13 (your test users)
- **✅ Students**: 3 (instead of --)
- **✅ Doctors**: 2 (instead of --)
- **✅ Hospitals**: 2-3 (instead of --)
- **✅ Moze Centers**: 2-3 (instead of --)
- **✅ Surveys**: 3 (instead of --)
- **✅ Petitions**: 5 (instead of --)
- **✅ Photo Albums**: 4 (instead of --)

## 🔍 **VERIFICATION:**

1. **Run the population script**
2. **Refresh your PythonAnywhere web app**
3. **Login as any user** (admin_user1, aamil_001, etc.)
4. **Check the dashboard** - numbers should appear instead of "--"

## ⚡ **TROUBLESHOOTING:**

If you get errors:

1. **Check you're in the right directory:**
   ```bash
   cd ~/umoor_sehhat
   pwd  # Should show /home/yourusername/umoor_sehhat
   ```

2. **Check Python version:**
   ```bash
   python3.10 --version  # Should be Python 3.10.x
   ```

3. **Check database connection:**
   ```bash
   python3.10 manage.py check --settings=umoor_sehhat.settings_pythonanywhere
   ```

## 🎉 **SUCCESS CRITERIA:**

✅ Dashboard shows actual numbers instead of "--"
✅ All test users can login and see populated statistics
✅ Ready for stakeholder demonstration

---

**🚀 This will fix your dashboard statistics immediately!**