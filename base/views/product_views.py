from django.shortcuts import render


from base.models import Product, Review
from base.serializers import ProductSerializer


# Customize what is returned from the claim of a Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# get all products


@api_view(['GET'])
def getProducts(request):
    # if no keyword/query came through we will not be filtering by anything we will just be rendering all the products
    query = request.query_params.get('keyword')
    if query == None:
        query = ""
    products = Product.objects.filter(name__icontains=query)
    # pagination
    # What page we currently on
    # what products are supposed to be on that page
    # Number of pages we should have
    # the actual page number
    page = request.query_params.get('page')  # page number we should be on
    paginator = Paginator(products, 4)
    try:
        # if we pass a page from frontend
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    if page == None:
        page = 1
    page = int(page)
    serializer = ProductSerializer(products, many=True)
    # the products current-page and other-pages
    return Response({'products': serializer.data, "page": page, "pages": paginator.num_pages})

# TOP PRODUCTS

@api_view(['GET'])
def getTopProducts(request):
    products = Product.objects.filter(rating__gte=4).order_by("-rating")[0:5]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def getProduct(request, pk):
    product = Product.objects.get(_id=pk)
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)

# Admin can delete Product


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteProduct(request, pk):
    product = Product.objects.get(_id=pk)
    product.delete()
    return Response('product Deleted')

# Admin creates products


@api_view(['POST'])
@permission_classes([IsAdminUser])
def createProduct(request):
    user = request.user  # user who sent request to create a product

    # create a blank product then will updateform available to update it to our desired product  -> instead of having products
    product = Product.objects.create(
        user=user,
        name='sample Product',
        price=0,
        brand='sample brand',
        countInStock=0,
        category='sample category',
        description=""


    )
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)


# Update Product
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateProduct(request, pk):
    data = request.data  # data from editting form
    product = Product.objects.get(_id=pk)
    # now we update this product
    product.name = data['name']
    product.price = data['price']
    product.countInStock = data['countInStock']
    product.category = data['category']
    product.description = data['description']
    product.brand = data['brand']

    product.save()
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)


# for image upload on editing a product
# we send productId && and the image through  a POST request
@api_view(['POST'])
def uploadImage(request):
    # productId and image are in here
    data = request.data
    # extract the id d
    product_id = data['product_id']
    # get that product by its id
    product = Product.objects.get(_id=product_id)
    # set the image
    product.image = request.FILES.get('image')  # image is the key
    product.save()
    return Response('image was updated successfully')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createProductReview(request, pk):
    user = request.user
    product = Product.objects.get(_id=pk)
    data = request.data

    # review already exists
    # ( filter through all review of this product see if any is associated with request-user)
    alreadyExists = product.review_set.filter(user=user).exists()

    if alreadyExists:
        content = {'detail': 'Product already reviewed'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # submitted  with no rating
    #  (to review, the rating should be >1)
    elif data['rating'] == 0:
        content = {'detail': 'Please select a Rating'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # create the review

    else:
        review = Review.objects.create(
            user=user,
            product=product,
            # if user deleted their account we dont want null value for this
            name=user.first_name,
            rating=data['rating'],
            comment=data['comment']

        )

        # update the number of reviews for this product
        # get all reviews for this product len-> how many reviews
        # thats what we update our numReviews
        # numReviews => all reviews for this product
        reviews = product.review_set.all()
        product.numReviews = len(reviews)

        # Product rating = all rating from every review / num of reviews
        # product rating => average rating s for reviews

        total = 0
        for i in reviews:
            total += i.rating

        product.rating = total / len(reviews)
        product.save()

        return Response('Review Added')
