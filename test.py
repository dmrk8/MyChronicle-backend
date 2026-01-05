TypeID = 3
filterID = 13166
tagNumber = TypeID << 28
tagNumber |= filterID

print(f"tagNumber: {tagNumber}")

tagNumber = 536909952

# Reverse the process: Extract TypeID and filterID from tagNumber
extracted_filterID = tagNumber & ((1 << 28) - 1)  # Mask to get lower 28 bits
extracted_TypeID = tagNumber >> 28  # Shift right by 28 to get higher bits

print(f"Extracted TypeID: {extracted_TypeID}")
print(f"Extracted filterID: {extracted_filterID}")


from datetime import datetime

# Convert Unix timestamp to readable UTC time
timestamp = 1765165739
readable_time = datetime.utcfromtimestamp(timestamp)
print(readable_time)  # Output: 2025-11-07 02:45:12


class A:
    pass


a = A()
b = A()
list = [a, b]

print(len(list))
