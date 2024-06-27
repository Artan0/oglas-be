from urllib.parse import unquote

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from firebase_admin import storage

class CustomUser(AbstractUser):
    USER_ROLES = (
        ('superadmin', 'Superadmin'),
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=USER_ROLES, default='user')
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True,
                              error_messages={'unique': "A user with that email already exists."})
    first_name = models.CharField( max_length=150)
    last_name = models.CharField(max_length=150)
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_query_name='customuser',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_query_name='customuser',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    def __str__(self):
        return self.email


class Ad(models.Model):
    CITY_CHOICES = [
        ('All', 'All'),
        ('Berovo', 'Berovo'),
        ('Bitola', 'Bitola'),
        ('Bogdanci', 'Bogdanci'),
        ('Debar', 'Debar'),
        ('Delčevo', 'Delčevo'),
        ('Demir Hisar', 'Demir Hisar'),
        ('Gevgelija', 'Gevgelija'),
        ('Gostivar', 'Gostivar'),
        ('Kavadarci', 'Kavadarci'),
        ('Kičevo', 'Kičevo'),
        ('Kočani', 'Kočani'),
        ('Kriva Palanka', 'Kriva Palanka'),
        ('Kruševo', 'Kruševo'),
        ('Kumanovo', 'Kumanovo'),
        ('Makedonska Kamenica', 'Makedonska Kamenica'),
        ('Makedonski Brod', 'Makedonski Brod'),
        ('Negotino', 'Negotino'),
        ('Ohrid', 'Ohrid'),
        ('Prilep', 'Prilep'),
        ('Probistip', 'Probistip'),
        ('Radoviš', 'Radoviš'),
        ('Resen', 'Resen'),
        ('Sveti Nikole', 'Sveti Nikole'),
        ('Štip', 'Štip'),
        ('Struga', 'Struga'),
        ('Strumica', 'Strumica'),
        ('Sveti Nikole', 'Sveti Nikole'),
        ('Tearce', 'Tearce'),
        ('Tetovo', 'Tetovo'),
        ('Valandovo', 'Valandovo'),
        ('Veles', 'Veles'),
        ('Vinica', 'Vinica'),
        ('Želino', 'Želino'),
        ('Skopje', 'Skopje'),
    ]

    AD_TYPES = [
        ('sale', 'Sale'),
        ('rent', 'Rent'),
    ]

    CATEGORY_CHOICES = [
        ('All', 'All'),
        ('general', 'General'),
        ('car', 'Car'),
        ('motorcycle', 'Motorcycle'),
        ('house', 'House'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    ad_type = models.CharField(max_length=4, choices=AD_TYPES)
    location = models.CharField(max_length=150, choices=CITY_CHOICES, default=CITY_CHOICES[0][0])
    address = models.CharField(max_length=150, default="Macedonia")
    image_urls = ArrayField(models.CharField(max_length=500, blank=True, null=True), default=list)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default=CATEGORY_CHOICES[0])
    is_featured = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        # Delete images from Firebase Storage
        if self.image_urls:
            for url in self.image_urls:
                # Extract filename from the URL
                filename_with_params = url.split('/')[-1]
                filename = unquote(filename_with_params.split('?')[0])  # Decode URL and remove query params

                # Initialize Firebase Storage
                bucket = storage.bucket()

                # Delete the file
                try:
                    blob = bucket.blob(filename)
                    blob.delete()
                    print(f"Successfully deleted image {filename} from Firebase Storage")
                except Exception as e:
                    print(f"Failed to delete image {filename} from Firebase Storage: {e}")

        # Call the parent delete method
        super().delete(*args, **kwargs)
    def __str__(self):
        return self.title


class Auction(models.Model):
    ad = models.OneToOneField(Ad, on_delete=models.CASCADE)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    end_time = models.DateTimeField()
    winner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='won_auctions',)

    def __str__(self):
        return f"Auction for {self.ad.title}"


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    bidder = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)
    is_highest_bid = models.BooleanField(default=False)

    def __str__(self):
        return f"Bid of {self.bid_amount} by {self.bidder.username} for {self.auction.ad.title}"






class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    added_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s wishlist"


# models.py

class CarAd(Ad):
    MANUFACTURER_CHOICES = [
        ('All', 'All'),
        ('Audi', 'Audi'),
        ('BMW', 'BMW'),
        ('Mercedes-Benz', 'Mercedes-Benz'),
        ('Volkswagen', 'Volkswagen'),
        ('Toyota', 'Toyota'),
        ('Honda', 'Honda'),
        ('Ford', 'Ford'),
        ('Chevrolet', 'Chevrolet'),
        ('Nissan', 'Nissan'),
        ('Hyundai', 'Hyundai'),
        ('Kia', 'Kia'),
        ('Subaru', 'Subaru'),
        ('Mazda', 'Mazda'),
        ('Volvo', 'Volvo'),
        ('Lexus', 'Lexus'),
        ('Jeep', 'Jeep'),
        ('Tesla', 'Tesla'),
        ('Ferrari', 'Ferrari'),
        ('Porsche', 'Porsche'),
        ('Jaguar', 'Jaguar'),
        ('Land Rover', 'Land Rover'),
        ('Mitsubishi', 'Mitsubishi'),
        ('Suzuki', 'Suzuki'),
        ('Chrysler', 'Chrysler'),
        ('Dodge', 'Dodge'),
        ('Acura', 'Acura'),
        ('Buick', 'Buick'),
        ('Cadillac', 'Cadillac'),
        ('Infiniti', 'Infiniti'),
        ('Lincoln', 'Lincoln'),
        ('Mini', 'Mini'),
        ('Smart', 'Smart'),
        ('Other', 'Other'),
    ]

    FUEL_CHOICES = [
        ('All', 'All'),
        ('Gasoline', 'Gasoline'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid')
    ]

    COLOR_CHOICES = [
        ('All', 'All'),
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Yellow', 'Yellow'),
        ('Black', 'Black'),
        ('White', 'White'),
        ('Silver', 'Silver'),
        ('Gray', 'Gray'),
        ('Brown', 'Brown'),
        ('Orange', 'Orange'),
        ('Purple', 'Purple'),
        ('Other', 'Other'),
    ]

    CAR_TYPE_CHOICES = [
        ('All', 'All'),
        ('Compact Car', 'Compact Car'),
        ('Sedan', 'Sedan'),
        ('Hatchback', 'Hatchback'),
        ('Estate car', 'Estate car'),
        ('Coupe', 'Coupe'),
        ('Cabriolet', 'Cabriolet'),
        ('SUV', 'SUV'),
        ('Minibus', 'Minibus'),
        ('Other', 'Other'),
    ]

    manufacturer = models.CharField(max_length=100, choices=MANUFACTURER_CHOICES)
    year = models.IntegerField()
    mileage = models.IntegerField()
    fuel_type = models.CharField(max_length=100, choices=FUEL_CHOICES)
    color = models.CharField(max_length=100, choices=COLOR_CHOICES)
    car_type = models.CharField(max_length=100, choices=CAR_TYPE_CHOICES)

    @receiver(post_delete, sender=Ad)
    def delete_related_car_ad(sender, instance, **kwargs):
        if instance.category == 'car':
            try:
                car_ad = CarAd.objects.get(id=instance.id)
                car_ad.delete()
            except CarAd.DoesNotExist:
                pass
    def __str__(self):
        return self.title
