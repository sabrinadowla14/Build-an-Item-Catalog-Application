from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Shop, WomenItem, User

engine = create_engine('sqlite:///itemsdatabase.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Sam Charles", email="samcharles2214@gmail.com",
             picture='https://pixabay.com/en/silhouette-little-girl-black-28870/')
session.add(User1)
session.commit()


# items from  
shop1 = Shop(user_id=1, name="Dress Shop")

session.add(shop1)
session.commit()



item1 = WomenItem(user_id=1, name="Midi Dress", description="Wrap back dress is one bouquet toss for you can't miss. Boatneck 22 inches from waist",
                     price="$50.00", color="Black", shop=shop1)

session.add(item1)
session.commit()


item3 = WomenItem(user_id=1, name="Tops", description="Short sleeve, scoop neck modern knit top.",
                     price="$9.99", color="Red", shop=shop1)

session.add(item3)
session.commit()

item2 = WomenItem(user_id=1, name="Maxi Dress", description="Quarter sleeve round neck",
                     price="$5.50", color="Blue", shop=shop1)

session.add(item2)
session.commit()

item4 = WomenItem(user_id=1, name="necklace", description="18 inch 10k gold pendant width: 13.2mm, pendant length: 19.7mm imported.",
                     price="$155.99", color="Gold", shop=shop1)

session.add(item4)
session.commit()

item5 = WomenItem(user_id=1, name="Ladies Shoes", description="Packed with features that have your comfort in mind, our Zibu by Yuu sandals make your feel happy.",
                     price="$50.79", color="Black", shop=shop1)

session.add(item5)
session.commit()

item6 = WomenItem(user_id=1, name="Womens Bag", description="a beautiful rose hue and a pocket for your laptop, flat handles.",
                     price="$30.00", color="Gold", shop=shop1)

session.add(item6)
session.commit()

item7 = WomenItem(user_id=1, name="Ear rings", description="Gold pearl imported.",
                     price="$55.00", color="Gold", shop=shop1)

session.add(item7)
session.commit()

# Womens items from Womens's World
shop2 = Shop(user_id=1, name="Womens\'s World")

session.add(shop2)
session.commit()

item1 = WomenItem(user_id=1, name="short dress", description="25 to 26 inches length, jersey nit, cotton washable.",
                     price="$14.00", color="Red", shop=shop2)
session.add(item1)
session.commit()


item2 = WomenItem(user_id=1, name="Long Dress", description="Quarter sleeve round neck",
                     price="$5.50", color="Blue", shop=shop2)

session.add(item2)
session.commit()

item3 = WomenItem(user_id=1, name="Tops", description="Short sleeve, scoop neck modern knit top.",
                     price="$9.99", color="white", shop=shop2)

session.add(item3)
session.commit()

item6 = WomenItem(user_id=1, name="Womens Bag", description="a beautiful rose hue and a pocket for your laptop, flat handles.",
                     price="$30.00", color="Brown", shop=shop2)

session.add(item6)
session.commit()

item7 = WomenItem(user_id=1, name="Ear rings", description="White pearl imported.",
                     price="$55.00", color="White", shop=shop2)

session.add(item7)
session.commit()


# Womens items from buy and smile 
shop1 = Shop(user_id=1, name="Buy and Smile")

session.add(shop1)
session.commit()

item1 = WomenItem(user_id=1, name="midi skirt", description="25 to 26 inches length, jersey nit, cotton washable.",
                     price="$14.00", color="Red", shop=shop1)

session.add(item1)
session.commit()

item2 = WomenItem(user_id=1, name="Night Dress", description="Quarter sleeve round neck",
                     price="$5.50", color="Blue", shop=shop1)

session.add(item2)
session.commit()

item3 = WomenItem(user_id=1, name="long Tops", description="Short sleeve, scoop neck modern knit top.",
                     price="$9.99", color="Black", shop=shop1)

session.add(item3)
session.commit()


item4 = WomenItem(user_id=1, name="Studs", description="Pearl imported.",
                     price="$55.00", color="Gold", shop=shop1)

session.add(item4)
session.commit()

item6 = WomenItem(user_id=1, name="Purse", description="a beautiful rose hue and a pocket for your laptop, flat handles.",
                     price="$30.00", color="Red", shop=shop1)

session.add(item6)
session.commit()


# items from category shop All Dress
shop1 = Shop(user_id=1, name="All Dress")

session.add(shop1)
session.commit()


item1 = WomenItem(user_id=1, name="midi skirt", description="25 to 26 inches length, jersey nit, cotton washable.",
                     price="$14.00", color="Red", shop=shop1)

session.add(item1)
session.commit()

item2 = WomenItem(user_id=1, name="Maxi Dress", description="Quarter sleeve round neck",
                     price="$5.50", color="Blue", shop=shop1)

session.add(item2)
session.commit()

item3 = WomenItem(user_id=1, name="Tops", description="Short sleeve, scoop neck modern knit top.",
                     price="$9.99", color="Red", shop=shop1)

session.add(item3)
session.commit()

item6 = WomenItem(user_id=1, name="Womens Bag", description="a beautiful rose hue and a pocket for your laptop, flat handles.",
                     price="$30.00", color="Black", shop=shop1)

session.add(item6)
session.commit()





print "All items for women are added!"
