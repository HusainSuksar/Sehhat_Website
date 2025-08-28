# Valid ITS IDs for Testing

The system now has stricter ITS ID validation. Here are some valid ITS IDs you can use for testing:

## Sample Valid ITS IDs:
- 10000007 (divisible by 7)
- 10000011 (divisible by 11) 
- 10000013 (divisible by 13)
- 20000014 (divisible by 7)
- 30000022 (divisible by 11)
- 40000026 (divisible by 13)
- 50000035 (divisible by 7)
- 60000044 (divisible by 11)
- 70000052 (divisible by 13)
- 80000063 (divisible by 7)

## Admin ITS ID:
- 50000001 (Special admin account)

## How the validation works:
1. Must be exactly 8 digits
2. Must be in range 10000000-99999999
3. Must be divisible by 7, 11, or 13 (simulates real ITS validation patterns)

This prevents random 8-digit numbers from working while still allowing testing with predictable IDs.