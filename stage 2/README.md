This is my Stage 2 file. i have used file systems to build this app. 
# overview of filesystem used in this project.
i have files such as -

users.txt - this file has python dictionary which contains username as key and base64 encoded string as value which is the password(we were provided with base64 strings for password so we did'nt encode it at back end .
but you can encode this in front end using javascript and send it to the backend.

category.txt - this file is a python dictionary with key and category name and value is an integer which represents the number of acts this particular category has.

acts.txt - this file is a python dictionary with key as actID and value as to which category it belongs to.

and we have categories folder in which we create a folder for each category and place all the acts for that category in its folder.
example we have categories abc and efg and act(1) belongs to abc similarly act(2) belongs to efg. then categories folder looks like 
categories/abc/1 and categories/efg2
