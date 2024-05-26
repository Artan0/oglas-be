from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    USER_ROLES = (
        ('superadmin', 'Superadmin'),
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='user')
    email = models.EmailField(_('email address'), unique=True,
                              error_messages={'unique': "A user with that email already exists."})

    username = models.CharField(max_length=150, unique=False, blank=True, null=True)

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
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


class Ad(models.Model):
    CITY_CHOICES = [
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

    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    ad_type = models.CharField(max_length=4, choices=AD_TYPES)
    location = models.CharField(max_length=150, choices=CITY_CHOICES, default=CITY_CHOICES[0][0])
    address = models.CharField(max_length=150, default="Macedonia")
    imageUrl = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Auction(models.Model):
    ad = models.OneToOneField(Ad, on_delete=models.CASCADE)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    end_time = models.DateTimeField()
    winner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='won_auctions')

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


class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    host = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s wishlist"
