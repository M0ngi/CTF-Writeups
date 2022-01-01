import hlextend

with open('outputPayloads', 'wb') as f:
    for i in xrange(1,50):
        sha = hlextend.new('sha256')
        x = sha.extend(":guinjutsu.php", "read.php", i, '184b5d255817fc0afe9316e67c8f386506a3b28b470c94f47583b76c7c0ec1e5')
        f.write(sha.hexdigest() + '|' + x.replace('\\x', '%')+'\n') # For url encoding

