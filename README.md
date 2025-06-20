# Instructions to exploit the weaknesses 
#
# Vulnerablities SQL Injection:
#
# Username:  ' OR '1'='1
# Password:  ' OR '1'='1
# 
# For the rest, use the following credentials:
# 
# Username: admin
# Password: adminpass
#
# Go to the Bug Report Tab and enter in the following: <script>alert("XSS success!")</script>
# Click Submit
# You should see the alert box pop up - the Java Script code is executed
# 
# You can also open this link to see everyone who has logged in: http://localhost:5000/api/users
# 
# Go again to the Bug Report Tab and enter in the following: <b>Nice bold bug</b>
# Click Submit
# You should see the bold text in the bug feed
# 
