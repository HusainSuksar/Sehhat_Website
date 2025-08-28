# Valid ITS IDs for Testing

The system has reasonable ITS ID validation. Here are valid ITS IDs you can use for testing:

## Admin ITS ID:
- 50000001 (Special admin account - always valid)

## Common Valid Patterns:
**Divisible by 3:**
- 10000002, 10000005, 10000008, 12345678, 23456781

**Divisible by 5:**  
- 10000000, 10000005, 12345670, 23456780, 34567890

**Divisible by 7:**
- 10000007, 10000014, 10000021, 20000014, 30000028

**Divisible by 11:**
- 10000011, 10000022, 20000013, 30000025, 40000037

**Divisible by 13:**
- 10000013, 10000026, 20000039, 30000000, 40000013

**Ending with 00:**
- 10000000, 12345600, 23456700, 34567800, 45678900

**Ending with 01:**
- 10000001, 12345601, 23456701, 34567801, 45678901

**Ending with 11:**
- 10000011, 12345611, 23456711, 34567811, 45678911

**Ending with 21:**
- 10000021, 12345621, 23456721, 34567821, 45678921

**Ending with 31:**
- 10000031, 12345631, 23456731, 34567831, 45678931

## How the validation works:
1. Must be exactly 8 digits
2. Must be in range 10000000-99999999  
3. Must match one of these patterns:
   - Special admin account (50000001)
   - Divisible by 3, 5, 7, 11, or 13
   - Ends with 00, 01, 11, 21, or 31

This allows most reasonable ITS IDs while preventing completely random patterns.