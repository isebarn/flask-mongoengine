You must add two files, `schema.txt` and `options.json`

`schema.txt` is where you define all the models for the database

```
table product {
    name varchar
}

table dog {
	name varchar
}

// embed
table laptop {
	name varchar
}

// embed
table cat {
	name varchar
}

table cart {
    email varchar
    item [ref: > product.id]
    dogs [ref: >> product.id]
    laptop [ref: < laptop.id]
    cats [ref: << cat.id]
}
```

**How dows it work**

Look at the `cart` table, you have

- `item [ref: > product.id]` this means that there is a single `product ` referenced
- `dogs [ref: >> product.id]` this means that `cart.dogs = [dog_1, dog_2, ...]` many dogs referenced
- `laptop [ref: < laptop.id]` means that there is a subdocument shaped like `laptop` (notice the `// embed` in the laptop table definition)
- `cats [ref: << cat.id]` means that there is a list of cat subdocuments (also `// embed`)

`options.json` should look like this

```
{
	"extensions": []
}
```
The available extensions are in the the `extensions` directory, they are `aws_cognito`, `aws_s3` and `aws_ses`

**How to run it?**

```
# environment setup
pipenv install
pipenv shell
pip install pyhumps
pip install black

# run the generator
python generate.py
```

This will create models and endpoints

Example usage
```
post */api/cart
{
  email: "blabla@gmail.com",
  item: { name: "product 1"} <- this will create also a product entry in the product collection
  dogs: [{ name: "dog_1"}], <- this will create also a dog entry in the dog collection
  laptop: { name: "dell" },
  cats: [{ name: "meow"}]
}

get */api/cart
->
{
  email: "blabla@gmail.com",
  item: object_id <- (object id of the product)
  dogs: [object_id] <- (object id of the dog)
  laptop: { name: "dell" },
  cats: [{ name: "meow"}]
}

get */api/cart?$include=product
->
{
  email: "blabla@gmail.com",
  item: { name: "product_1" }
  dogs: [object_id] <- (object id of the dog)
  laptop: { name: "dell" },
  cats: [{ name: "meow"}]
}

// filtering
get */api/cart?email=blablabla@gmail.com
get */api/cart?product__name=product_1

```

# Important
Do you need more than CRUD functionality?
If yes, place it in the `models/query_sets/__init__.py` and `models/triggers/__init__.py` files

## query_sets
The generator will create a query set class for every model
So the `models/query_sets/__init__.py` file will look like this (simplified)

```
from mongoengine import QuerySet

class CartQuerySet(QuerySet):
	pass
```

If you would like to find all carts where the name of the product starts with "product" you would do

```
class CartQuerySet(QuerySet):
	def default(self, cls, filters): (you must add this if you add something else)
		return cls.fetch(filters)
	
   
   def find_starts_with(filter):
	   return = list(cls.objects().aggregate.... # etc you just write a mongo query/aggregate
```		
## triggers
If you want extra stuff happen on insert add to the triggers file
Fx if you create a new Product

```
def email_notification(sender, document, created):
  send_email(**) <- some method that sends email to everyone that is waiting for the product


signals.pre_save.connect(available_products, sender=Product)
```
