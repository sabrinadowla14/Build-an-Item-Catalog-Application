<h1>Project: Build an Item Catalog Application</h1>
**Note**: Contents are taken from *websites*, *GitHub* and *Instructors Notes*.

Developed an application that provides a list of items within a variety of categories (*Shops*) as
well as provides a user registration and authentication system. Registered users will have the
ability to post, edit and delete their own items. I have learned how to develop a RESTful web application
using the Python framework Flask along with implementing third-party OAuth authentication. 
Also learned when to properly use the various HTTP methods available to me and how these methods relate 
to CRUD (create, read, update and delete) operations.

<h2>Required Libraries and dependencies</h2>
A web framework Flask version - 0.9
Python version - 2.7.13
I have used SQLAlchemy - The Database Toolkit for Python

Project Contents ( * .py, static, template folder)
catalog folder:
 * project.py,
 * client_secret_value.json, 
 * fb_client_secrets.json,
 * database_setup.py and,
 * itemsinfo.py.
static folder:
 * styles.css
 * images
Templates folder:
 * HTML files.

>You need to login first in order to delete, edit or add an item. http://localhost:5010/login -- You 
>have the option to choose either Google sign in or Facebook to sign in. After signing, it will redirect 
>you to the homepage. Homepage (http://localhost:5010/ or http://localhost:5010/shop/) displays all 
>current categories (Shops) along with the latest added items.

There is a link called Shops which will take you to the home page. Selecting a specific category (Shop) 
shows all the items available for that category (Shop). Path: http://localhost:5010/shop/1/items/. 
Selecting a specific item shows you the name of a particular item.
If you click the button for the description of that item, it will show description in
the modal dialog box. Path: http://localhost:5010/shop/1/items/1.
If you want to edit or delete, without login in it will tell you to log in first.

If you want to add a new item, click on Add Item button, it will let you add the item. 
http://localhost:5010/shop/items/new/  You need to choose all the option, otherwise,
it will give you an error. 
If you click on edit button it will take you to this path: http://localhost:5010/shop/1/items/1/edit.
After editing the item it will render womenitems.html which will show the name of the edited item,
if you click on the description it will show you edited items.
If you click on delete it will take you to http://localhost:5010/shop/3/items/31/delete.
It will ask you if you really want to delete the item. After deleting the item it will render the shop.html 
file and show you a total number of items in that particular shop.

Google and/or Facebook OAuth service setup:
* Created Client ID & Secret
In the Google APIs Console — https://console.developers.google.com/apis
Chosen Credentials from the menu on the left.
Created an OAuth Client ID.
From the list of application types, chosen Web application.
Then set the authorized JavaScript origins.
Thus got the client ID and client secret.

* Created Anti Forgery State Token
* Created Login Page
* Made A Callback Method
* Created GConnect to connect with Google.
* Created Disconnect to disconnect from the Google.
* Wrote a code to protect the pages.

Run the code:
Go to the working directory where the vagrant file is located.
In the terminal type:
vagrant up
vagrant ssh
cd to vagrant
cd to catalog
In the terminal: 
* type python database_setup.py which will create database - itemsdatabase.db
* type python itemsinfo.py to populate the database.
* type: python project.py to run the application.
