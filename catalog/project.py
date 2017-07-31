from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Shop, WomenItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from sqlalchemy.orm.exc import NoResultFound
from flask import abort

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secret_value.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Shops for Women"


# Connect to Database and create database session
engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine

# Create database session
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/v2.8/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    # strip expire tag from access token
    data = json.loads(result)
    token = 'access_token=' + data['access_token']

    url = 'https://graph.facebook.com/v2.8/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    # let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome to Udacity Item Catalog, '
    output += login_session['username']

    output += '!!!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 150px; height: 150px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Logged in as %s" % login_session['username'])
    return output


# logout from facebook.
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# gconnect is a route and a function that accepts post\
# request. confirm that the token
# client sends to the server matches the token that the server\
# sent to the client.
# This round trip verification ensure that the user is making\
# the request and not the malicious script.


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    # By using request.args.get method my code examine the\
    # state token passed in and compares
    # it with the state of the login session.\
    # If these two do not match then I create a
    # response of an invalid state token and return this message to the client.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    # collect the one time code from the server with the request.data function.
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        # I will try and use this one time use code and \
        # exchange it for credential object.
        # which will contain the access code for the server.
        # This line creates an aouth flow object and\
        # adds my clients secrets key
        # information to it.
        oauth_flow = flow_from_clientsecrets(
            'client_secret_value.json', scope='')
        # here I specify the postmessage that this is the one\
        # time code flow my server will
        # be sending off. Finally I initiate the exchange with the step
        # two exchange function.
        # Passing in my one time code as input.
        oauth_flow.redirect_uri = 'postmessage'
        # step2_exchange - function of the flow class.\
        # Exchanges as authorization
        # code for a credentials object. If all goes\
        # well then the response from the google
        # will be an object and store it in credentials.
        credentials = oauth_flow.step2_exchange(code)
    # if any error happens send the response as JSON object.
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    # store credentials.access_token in access_token variable.
    access_token = credentials.access_token
    # if I append this token with the google url - Google API server can verify
    # that this is a valid token to use.
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # In these two lines of code create a json GET request containing the URL
    # store the result of the request in the result variable.
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    # I send the 500 internal server error to my client
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    # grab the id of the token in my credential object and compared it
    # with the id returned by the Google API Server.
    gplus_id = credentials.id_token['sub']
    # if these two does not match then we do not have \
    # correct token - return an error.
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check if the user is already logged into the system. This will return
    # a 200 successful authentication. without resseting
    # all of the login session variables again.
    # assuming none of this if statements are true, and\
    # I have a valid access token.
    # user is successfully login to my server,\
    # in these user login session store their
    # credential in Google plus_ID.
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    # I will use the Google Plus API to get some more information.
    # about the user. I will send off a message to the Google API
    # Server with my access_token. Requesting the user info allowed by
    # my token_scope and stored in an object I called data.
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    # store data in my login session.
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome to Udacity Item Catalog, '
    output += login_session['username']
    output += '!!!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 150px; height: 150px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("Logged in as %s" % login_session['username'])
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

"""
DISCONNECT - Revoke a current user's token and reset their login_session
Disconnect the user from Google account.
Logging them out of our web application.
This is done by rejecting the access_token.

"""


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')

    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(json.dumps(
                   'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Shop Information
@app.route('/shop/JSON')
def showShopsJSON():
    shops = session.query(Shop).all()
    return jsonify(shops=[shop.serialize for shop in shops])


@app.route('/shop/<int:shop_id>/JSON')
@app.route('/shop/<int:shop_id>/items/JSON')
def showShopJSON(shop_id):
    items = session.query(WomenItem).filter_by(shop_id=shop_id).all()
    return jsonify(items=[item.serialize for item in items])


@app.route('/shop/<int:shop_id>/items/<int:item_id>/JSON')
def showItemJSON(shop_id, item_id):
    item = session.query(WomenItem).filter_by(id=item_id).first()
    return jsonify(item=[item.serialize])

# Show all category of shops
LATEST_ITEMS = 8


@app.route('/')
@app.route('/shop/')
def showShops():
    # Get all categories of shops
    shops = session.query(Shop).all()
    # Latest category items added
    items = session.query(WomenItem).all()
    latest_items = session.query(WomenItem).order_by(WomenItem.id.desc()) \
        .limit(LATEST_ITEMS).all()

    if 'username' not in login_session:
        return render_template(
            'publicshops.html',
            shops=shops,
            items=latest_items)
    else:
        return render_template(
            'shops.html',
            shops=shops,
            items=latest_items)


# show the selected category of shop.
@app.route('/shop/<int:shop_id>/')
@app.route('/shop/<int:shop_id>/items/')
def showShop(shop_id):
    # Get all shops
    shops = session.query(Shop).all()
    # Get one shop
    shop = session.query(Shop).filter_by(id=shop_id).first()
    # Get the creator of the shop.
    creator = getUserInfo(shop.user_id)
    # Get the specific shop's(Categoty) name
    shopName = shop.name
    # Get all items of a specific shop
    items = session.query(WomenItem).filter_by(
        shop_id=shop_id).all()
    latest_item = session.query(WomenItem) \
        .order_by(WomenItem.shop_id.desc()).first()
    # count of items in a shop
    womenItemsCount = session.query(WomenItem) \
        .filter_by(shop_id=shop_id).count()
    print womenItemsCount
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template(
            'publicshop.html',
            items=items,
            shop=shop,
            shops=shops,
            creator=creator,
            shopName=shopName,
            womenItemsCount=womenItemsCount,
            latest_item=latest_item)
    else:
        return render_template(
            'shop.html',
            items=items,
            shop=shop,
            shops=shops,
            creator=creator,
            shopName=shopName,
            womenItemsCount=womenItemsCount,
            latest_item=latest_item)


""" Show one chosen item """


@app.route('/shop/<int:shop_id>/items/<int:item_id>')
def showItem(shop_id, item_id):
    # Get category item
    try:
        item = session.query(WomenItem).filter_by(id=item_id).one()
    except NoResultFound:
        abort(404)
    try:
        shop = session.query(Shop).filter_by(id=shop_id).one()
    except NoResultFound:
        abort(404)
    # Get creator of item
    creator = getUserInfo(shop.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicwomenitems.html',
                               item=item, shop=shop,
                               creator=creator)
    else:
        return render_template('womenitems.html',
                               item=item, shop=shop,
                               creator=creator)


# Add a new women item
@app.route('/shop/items/new/', methods=['GET', 'POST'])
def newWomenItem():
    if 'username' not in login_session:
        flash('Please login first, to add new item!')
        return redirect('/login')
    if request.method == 'POST':
        if not request.form['name']:
            flash('Please you need to add name')
            return redirect(url_for('newWomenItem'))
        if not request.form['description']:
            flash('Please you need to add description')
            return redirect(url_for('newWomenItem'))
        if not request.form['price']:
            flash('Please you need to add price')
            return redirect(url_for('newWomenItem'))
        if not request.form['color']:
            flash('Please you need to add color')
            return redirect(url_for('newWomenItem'))

        # add shop item
        newItem = WomenItem(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            color=request.form['color'],
            shop_id=request.form['shop'],
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Category %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showShops'))
    else:
        shops = session.query(Shop).all()
        return render_template('newwomenitem.html', shops=shops)


@app.route('/shop/<int:shop_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editWomenItem(shop_id, item_id):
    # Check to see if user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    # Get the edited item
    try:
        editedItem = session.query(WomenItem).filter_by(id=item_id).one()
    except NoResultFound:
        abort(404)
    try:
        shop = session.query(Shop).filter_by(id=shop_id).one()
    except NoResultFound:
        abort(404)
    creator = getUserInfo(editedItem.user_id)
    if login_session['user_id'] != editedItem.user_id:
        flash(message="You are not allowed to edit this item.")
        return render_template('womenitems.html',
                               item=editedItem, shop=shop, creator=creator)
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['color']:
            editedItem.course = request.form['color']
        session.add(editedItem)
        session.commit()
        flash('Women Item Successfully Edited')
        return redirect(url_for('showItem',
                        shop_id=editedItem.shop_id, item_id=editedItem.id))
    else:
        return render_template('editwomenitem.html',
                               shop_id=editedItem.shop_id, item=editedItem)


# Delete a women item
@app.route('/shop/<int:shop_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteWomenItem(shop_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')

    try:
        shop = session.query(Shop).filter_by(id=shop_id).one()
    except NoResultFound:
        abort(404)
    try:
        item = session.query(WomenItem).filter_by(id=item_id).one()
    except NoResultFound:
        abort(404)
    creator = getUserInfo(item.user_id)
    if login_session['user_id'] != item.user_id:
        flash(message="You are not allowed to delete this item!")
        return render_template('womenitems.html', item=item,
                               shop=shop, creator=creator)
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Women Item Successfully Deleted')
        return redirect(url_for('showShop', shop_id=item.shop_id))
    else:
        return render_template('deletewomenitem.html', shop=shop, item=item)


# Disconnect based on provider
@app.route('/logout')
def logout():
    if login_session['provider'] == 'google':
        gdisconnect()
        del login_session['gplus_id']
        del login_session['access_token']
    if login_session['provider'] == 'facebook':
        fbdisconnect()
        del login_session['facebook_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']
    flash("You have successfully been logged out.")
    return redirect(url_for('showShops'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5010)
