from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ReviewSerializer, CreateReviewSerializer
from . import services


class ReviewListView(APIView):
    def get(self, request):
        product_id = request.query_params.get('product_id')
        user_id    = request.query_params.get('user_id')

        if product_id:
            reviews = services.get_reviews_by_product(product_id)
        elif user_id:
            reviews = services.get_reviews_by_user(user_id)
        else:
            return Response(
                {'detail': 'Provide product_id or user_id query parameter.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(ReviewSerializer(reviews, many=True).data)

    def post(self, request):
        serializer = CreateReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        review = services.create_review(
            d['user_id'], d['product_id'], d['rating'],
            d.get('comment', ''), d.get('created_by', 'system'),
        )
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class ReviewDetailView(APIView):
    def delete(self, request, pk):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'detail': 'user_id query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        services.delete_review(pk, user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
