from rest_framework import serializers
from .models import Author, Book, Order, OrderItem


class AuthorSerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'name', 'birth_date', 'biography', 'books_count']

    def get_books_count(self, obj):
        return obj.books.all()

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(many=True)
    is_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'price', 'stock', 'is_in_stock']

    def get_is_in_stock(self, obj):
        return True if obj.stock > 0 else False

    def validate_isbn(self, isbn):
        if not (isbn.isdigit() and len(isbn) == 13):
            raise serializers.ValidationError("""
            ISBN 13 raqamdan iborat bo'lishi va faqat raqamlardan tashkil topgan bo'lishi kerak.
            """)

class OrderItemSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['book', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        return obj.price * obj.quantity

    def validate_quantity(self, quantity):
        if quantity < 1:
            raise serializers.ValidationError("Miqdor 1 dan kichik bo'lmasligi kerak.")

        return quantity

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    books = BookSerializer(source='orderitem_set', many=True)
    total_price = serializers.SerializerMethodField(read_only=True)

    def get_user(self, obj):
        return {'id': obj.user.id, 'username': obj.user.username}

    def get_total_price(self, obj):
        # Umumiy qiymat ? shuni nazarga tutdiz digan umidtaman.
        total = sum(item.book.price for item in obj.orderitem_set.all())
        return total

    def validate(self, data):
        for order_item in data.get('orderitem_set', []):
            book = order_item.get('book')
            quantity = order_item.get('quantity')
            if quantity > book.stock:
                raise serializers.ValidationError(f"Kitob {book.title} zaxirada yetarli emas.")
        return data