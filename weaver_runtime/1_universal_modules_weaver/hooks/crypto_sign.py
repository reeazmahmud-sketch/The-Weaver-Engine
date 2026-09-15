import sys
import json
import hashlib
if __name__ == '__main__':
    input_data = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    raw_string = input_data.get('data', '')
    hashed = hashlib.md5(raw_string.encode()).hexdigest()
    print(json.dumps({'verification_hash': hashed}))
